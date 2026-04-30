import streamlit as st
from engine import (
    generate_followups,
    build_prompt,
    generate_output,
    clean_input
)

st.set_page_config(page_title="PROMPTly", layout="wide")

st.title("✨ PROMPTly")
st.caption("AI-powered prompt optimizer that thinks like a prompt engineer")

# ---------------- SESSION STATE INIT ----------------
if "step" not in st.session_state:
    st.session_state.step = 1

if "user_prompt" not in st.session_state:
    st.session_state.user_prompt = ""

if "questions" not in st.session_state:
    st.session_state.questions = []

if "answers" not in st.session_state:
    st.session_state.answers = {}

if "final_prompt" not in st.session_state:
    st.session_state.final_prompt = ""

if "output" not in st.session_state:
    st.session_state.output = ""

# ---------------- STEP 1: USER INPUT ----------------
if st.session_state.step == 1:
    st.subheader("🧠 What do you want to create?")

    user_input = st.text_area(
        "Enter your prompt",
        placeholder="e.g. Write a LinkedIn post on Agentic AI"
    )

    if st.button("Generate Smart Questions"):
        if user_input.strip():
            st.session_state.user_prompt = user_input
            st.session_state.questions = generate_followups(user_input)
            st.session_state.step = 2
            st.rerun()

# ---------------- STEP 2: FOLLOW-UP QUESTIONS ----------------
elif st.session_state.step == 2:
    st.subheader("🎯 Help me refine this")

    answers = {}

    for q in st.session_state.questions:
        label = q["question"]
        key = q["key"]
        example = q.get("example", "")

        answers[key] = st.text_input(
            f"{label} ({example})",
            key=key
        )

    style = st.selectbox(
        "✨ Style",
        ["Default", "Human", "Persuasive", "Analytical"]
    )

    if st.button("Build Prompt"):
        # Clean inputs
        cleaned_answers = {
            k: clean_input(v) for k, v in answers.items()
        }

        st.session_state.answers = cleaned_answers

        st.session_state.final_prompt = build_prompt(
            st.session_state.user_prompt,
            cleaned_answers,
            style
        )

        st.session_state.step = 3
        st.rerun()

# ---------------- STEP 3: FINAL OUTPUT ----------------
elif st.session_state.step == 3:
    st.subheader("🧾 Your Optimized Prompt")

    st.code(st.session_state.final_prompt, language="markdown")

    if st.button("🚀 Generate Output"):
        st.session_state.output = generate_output(
            st.session_state.final_prompt
        )
        st.rerun()

    if st.session_state.output:
        st.subheader("💡 Output")
        st.write(st.session_state.output)

    if st.button("🔄 Start Over"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
