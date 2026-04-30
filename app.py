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

# -------- Session State --------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "history" not in st.session_state:
    st.session_state.history = []

# -------- Sidebar --------
st.sidebar.title("📜 Prompt History")

for i, item in enumerate(st.session_state.history):
    if st.sidebar.button(f"Prompt {i+1}"):
        st.sidebar.write("Original:", item["original"])
        st.sidebar.write("Improved:", item["improved"])

# -------- Style --------
style = st.selectbox(
    "Output Style",
    ["Formal", "Balanced", "Human & Conversational"]
)

# -------- Chat Display --------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# -------- Input --------
user_input = st.chat_input("Enter your prompt...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.session_state.base_prompt = user_input

    questions = generate_followups(user_input)
    st.session_state.questions = questions
    st.session_state.answers = {}

# -------- Follow-ups --------
if "questions" in st.session_state:
    st.subheader("Answer to improve your prompt")

    for q in st.session_state.questions:
        ans = st.text_input(q, key=q)
        if ans:
            st.session_state.answers[q] = ans

# -------- Cheatcodes --------
st.subheader("⚡ Cheatcodes")

c1, c2, c3 = st.columns(3)

with c1:
    if st.button("Add Role"):
        st.session_state.base_prompt = apply_cheatcode(
            st.session_state.base_prompt, "role"
        )

with c2:
    if st.button("Add Constraints"):
        st.session_state.base_prompt = apply_cheatcode(
            st.session_state.base_prompt, "constraints"
        )

with c3:
    if st.button("Structure Output"):
        st.session_state.base_prompt = apply_cheatcode(
            st.session_state.base_prompt, "structure"
        )

# -------- Generate --------
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

# -------- Results --------
if "improved" in st.session_state:

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

    if st.button("Compare Outputs"):

        orig = generate_output(st.session_state.base_prompt)
        new = generate_output(st.session_state.improved)

        c1, c2 = st.columns(2)

        with c1:
            st.write("Original Output")
            st.write(orig)

        with c2:
            st.write("Improved Output")
            st.write(new)
