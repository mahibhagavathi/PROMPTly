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
st.caption("Turn vague prompts into powerful ones")

# ---------------- SESSION STATE ----------------
if "base_prompt" not in st.session_state:
    st.session_state.base_prompt = ""

if "questions" not in st.session_state:
    st.session_state.questions = []

if "answers" not in st.session_state:
    st.session_state.answers = {}

if "improved" not in st.session_state:
    st.session_state.improved = ""

# ---------------- STEP 1: USER INPUT ----------------
st.subheader("Step 1: Enter your prompt")

user_input = st.text_area(
    "What do you want to do?",
    placeholder="e.g. Write a LinkedIn post about agentic AI"
)

if st.button("Next ➡️"):
    if user_input.strip():
        st.session_state.base_prompt = user_input
        st.session_state.questions = generate_followups(user_input)
        st.session_state.answers = {}
    else:
        st.warning("Please enter a prompt first")

# ---------------- STEP 2: FOLLOW UPS ----------------
if st.session_state.questions:

    st.subheader("Step 2: Improve your prompt")

    st.markdown("Answer a few questions to make your prompt stronger 👇")

    # Example helper text
    st.info("""
**Examples:**
- **Role:** Data Analyst, Content Creator, Product Manager  
- **Audience:** Beginners, LinkedIn professionals, Developers  
- **Goal:** Educate, Generate leads, Explain a concept  
- **Tone:** Professional, Casual, Storytelling  
- **Word Limit:** 100, 150, 300  
""")

    for q in st.session_state.questions:
        ans = st.text_input(q, key=q)
        if ans:
            st.session_state.answers[q] = ans

# ---------------- STYLE ----------------
if st.session_state.base_prompt:
    st.subheader("Step 3: Choose output style")

    style = st.selectbox(
        "Select tone",
        ["Formal", "Balanced", "Human & Conversational"]
    )

# ---------------- CHEATCODES ----------------
if st.session_state.base_prompt:

    st.subheader("⚡ Optional Boosts (Cheatcodes)")

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

# ---------------- GENERATE ----------------
if st.session_state.base_prompt:

    if st.button("🚀 Generate Optimized Prompt"):

        answers = list(st.session_state.answers.values())

        mapped = {
            "goal": answers[0] if len(answers) > 0 else "inform",
            "audience": answers[1] if len(answers) > 1 else "general audience",
            "tone": "engaging",
            "word_limit": answers[2] if len(answers) > 2 else "150"
        }

        improved = build_prompt(
            st.session_state.base_prompt,
            mapped,
            style
        )

        st.session_state.improved = improved

# ---------------- RESULTS ----------------
if st.session_state.improved:

    st.subheader("✨ Results")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Original Prompt")
        st.write(st.session_state.base_prompt)
        st.metric("Score", score_prompt(st.session_state.base_prompt))

    with col2:
        st.markdown("### Optimized Prompt")
        st.write(st.session_state.improved)
        st.metric("Score", score_prompt(st.session_state.improved))

    st.progress(score_prompt(st.session_state.improved) / 100)

    st.code(st.session_state.improved)

    st.download_button(
        "Download Prompt",
        st.session_state.improved,
        "prompt.txt"
    )

    # Compare outputs
    if st.button("Compare Outputs"):

        with st.spinner("Generating outputs..."):
            orig = generate_output(st.session_state.base_prompt)
            new = generate_output(st.session_state.improved)

        c1, c2 = st.columns(2)

        with c1:
            st.markdown("### Original Output")
            st.write(orig)

        with c2:
            st.markdown("### Improved Output")
            st.write(new)
