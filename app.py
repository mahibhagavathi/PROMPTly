import streamlit as st
from engine import (
    generate_followups,
    build_prompt,
    generate_output,
    apply_cheatcode
)
from scorer import score_prompt

st.set_page_config(page_title="PROMPTly", layout="wide")

st.title("⚡ PROMPTly")
st.caption("AI Prompt Optimizer with Human-like Output")

# ---------------- SESSION STATE INIT ----------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "history" not in st.session_state:
    st.session_state.history = []

if "base_prompt" not in st.session_state:
    st.session_state.base_prompt = ""

if "questions" not in st.session_state:
    st.session_state.questions = []

if "answers" not in st.session_state:
    st.session_state.answers = {}

if "improved" not in st.session_state:
    st.session_state.improved = ""

# ---------------- SIDEBAR ----------------
st.sidebar.title("📜 Prompt History")

for i, item in enumerate(st.session_state.history):
    if st.sidebar.button(f"Prompt {i+1}"):
        st.sidebar.write("Original:", item["original"])
        st.sidebar.write("Improved:", item["improved"])

# ---------------- STYLE ----------------
style = st.selectbox(
    "Output Style",
    ["Formal", "Balanced", "Human & Conversational"]
)

# ---------------- CHAT DISPLAY ----------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# ---------------- USER INPUT ----------------
user_input = st.chat_input("Enter your prompt...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.session_state.base_prompt = user_input

    questions = generate_followups(user_input)
    st.session_state.questions = questions
    st.session_state.answers = {}

# ---------------- FOLLOW-UP QUESTIONS ----------------
if st.session_state.questions:
    st.subheader("Answer to improve your prompt")

    for q in st.session_state.questions:
        ans = st.text_input(q, key=q)
        if ans:
            st.session_state.answers[q] = ans

# ---------------- CHEATCODES ----------------
st.subheader("⚡ Cheatcodes")

c1, c2, c3 = st.columns(3)

def warn_if_empty():
    if not st.session_state.base_prompt:
        st.warning("Enter a prompt first to apply cheatcodes")
        return True
    return False

with c1:
    if st.button("Add Role"):
        if not warn_if_empty():
            st.session_state.base_prompt = apply_cheatcode(
                st.session_state.base_prompt, "role"
            )

with c2:
    if st.button("Add Constraints"):
        if not warn_if_empty():
            st.session_state.base_prompt = apply_cheatcode(
                st.session_state.base_prompt, "constraints"
            )

with c3:
    if st.button("Structure Output"):
        if not warn_if_empty():
            st.session_state.base_prompt = apply_cheatcode(
                st.session_state.base_prompt, "structure"
            )

# ---------------- GENERATE PROMPT ----------------
if st.button("Generate Optimized Prompt"):

    answers = list(st.session_state.answers.values())

    mapped = {
        "goal": answers[0] if len(answers) > 0 else "",
        "audience": answers[1] if len(answers) > 1 else "",
        "tone": "engaging",
        "word_limit": "150"
    }

    improved = build_prompt(
        st.session_state.base_prompt,
        mapped,
        style
    )

    st.session_state.improved = improved

    st.session_state.history.append({
        "original": st.session_state.base_prompt,
        "improved": improved
    })

# ---------------- RESULTS ----------------
if st.session_state.improved:

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Original Prompt")
        st.write(st.session_state.base_prompt)
        st.metric("Score", score_prompt(st.session_state.base_prompt))

    with col2:
        st.subheader("Optimized Prompt")
        st.write(st.session_state.improved)
        st.metric("Score", score_prompt(st.session_state.improved))

    st.progress(score_prompt(st.session_state.improved) / 100)

    st.code(st.session_state.improved)

    st.download_button(
        "Download Prompt",
        st.session_state.improved,
        "prompt.txt"
    )

    # ---------------- OUTPUT COMPARISON ----------------
    if st.button("Compare Outputs"):

        with st.spinner("Generating outputs..."):
            orig = generate_output(st.session_state.base_prompt)
            new = generate_output(st.session_state.improved)

        c1, c2 = st.columns(2)

        with c1:
            st.subheader("Original Output")
            st.write(orig)

        with c2:
            st.subheader("Improved Output")
            st.write(new)
