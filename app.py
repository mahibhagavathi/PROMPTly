import streamlit as st
from engine import (
    generate_followups,
    build_prompt,
    generate_output,
    finetune_prompt,
    clean_input,
    FINETUNE_OPTIONS
)

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(page_title="PROMPTly", page_icon="✦", layout="centered")

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@500;600;700&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

/* Background */
.stApp {
    background: #f5f6fa;
    color: #1f2a44;
}

/* Hide Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 2.5rem; padding-bottom: 3rem; max-width: 760px; }

/* ── Hero ── */
.hero {
    text-align: center;
    padding: 2.5rem 0 1.5rem;
    border-bottom: 1px solid #e5e7eb;
    margin-bottom: 2.5rem;
}
.hero-logo {
    font-family: 'Syne', sans-serif;
    font-weight: 700;
    font-size: 2.8rem;
    color: #1f2a44;
}
.hero-sub {
    font-size: 0.95rem;
    color: #6b7280;
    font-style: italic;
}

/* ── Step indicator ── */
.step-bar {
    display: flex;
    justify-content: center;
    gap: 0.5rem;
    margin-bottom: 2rem;
    align-items: center;
}
.step-dot {
    width: 8px; height: 8px;
    border-radius: 50%;
    background: #d1d5db;
}
.step-dot.active { background: #a78bfa; }
.step-dot.done   { background: #2f3a5f; }

.step-label {
    font-family: 'Syne', sans-serif;
    font-size: 0.7rem;
    color: #6b7280;
    text-transform: uppercase;
}

/* ── Section heading ── */
.section-heading {
    font-family: 'Syne', sans-serif;
    font-weight: 600;
    font-size: 1.3rem;
    color: #2f3a5f;
}
.section-sub {
    font-size: 0.85rem;
    color: #6b7280;
}

/* ── Inputs ── */
.stTextArea textarea, .stTextInput input {
    background: #ffffff !important;
    border: 1px solid #e5e7eb !important;
    border-radius: 10px !important;
    color: #1f2a44 !important;
}
.stTextArea textarea:focus, .stTextInput input:focus {
    border-color: #a78bfa !important;
    box-shadow: 0 0 0 2px rgba(167,139,250,0.15) !important;
}

/* ── Select box ── */
.stSelectbox > div > div {
    background: #ffffff !important;
    border: 1px solid #e5e7eb !important;
    border-radius: 10px !important;
    color: #1f2a44 !important;
}

/* ── Primary button ── */
.stButton > button {
    background: #2f3a5f !important;
    color: #ffffff !important;
    border-radius: 8px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 600 !important;
}
.stButton > button:hover {
    background: #1f2a44 !important;
}

/* ── Cards ── */
.prompt-card, .output-card {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 12px;
    padding: 1.5rem;
    color: #374151;
}

/* ── Tags ── */
.tag {
    background: #f1f5f9;
    border: 1px solid #e5e7eb;
    border-radius: 999px;
    padding: 0.25rem 0.75rem;
    font-size: 0.75rem;
    color: #6b7280;
}

/* ── Divider ── */
.thin-divider {
    border-top: 1px solid #e5e7eb;
}

/* ── Labels ── */
.stTextArea label, .stTextInput label, .stSelectbox label {
    font-family: 'Syne', sans-serif !important;
    font-size: 0.75rem !important;
    font-weight: 600 !important;
    color: #6b7280 !important;
    text-transform: uppercase !important;
}
</style>
""", unsafe_allow_html=True)

# ── Hero header ──────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-logo">✦ PROMPTly</div>
    <div class="hero-sub">Communicate better with AI — because it's only as good as your prompt.</div>
</div>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
for key, default in {
    "step": 1,
    "user_prompt": "",
    "questions": [],
    "answers": {},
    "final_prompt": "",
    "output": "",
    "finetuned": False,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ── Step indicator ────────────────────────────────────────────────────────────
steps = ["Idea", "Refine", "Prompt", "Output"]
def step_bar(current):
    dots = ""
    for i, label in enumerate(steps, 1):
        cls = "active" if i == current else ("done" if i < current else "step-dot")
        if i == current:
            dots += f'<span class="step-label">{label}</span>'
        dots += f'<div class="step-dot {cls}"></div>'
    st.markdown(f'<div class="step-bar">{dots}</div>', unsafe_allow_html=True)

step_bar(st.session_state.step)

# ════════════════════════════════════════════════════════════════════════════
# STEP 1 — Raw idea
# ════════════════════════════════════════════════════════════════════════════
if st.session_state.step == 1:
    st.markdown('<div class="section-heading">What do you want to create?</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Drop in a rough idea — we\'ll shape it into something powerful.</div>', unsafe_allow_html=True)

    user_input = st.text_area(
        "Your idea",
        placeholder="e.g. Write a LinkedIn post on Agentic AI",
        height=110,
        label_visibility="collapsed"
    )

    col1, col2 = st.columns([3, 1])
    with col1:
        if st.button("Continue →", use_container_width=True):
            if user_input.strip():
                st.session_state.user_prompt = user_input
                st.session_state.questions = generate_followups(user_input)
                st.session_state.step = 2
                st.rerun()
            else:
                st.warning("Enter an idea to get started.")

# ════════════════════════════════════════════════════════════════════════════
# STEP 2 — Context questions
# ════════════════════════════════════════════════════════════════════════════
elif st.session_state.step == 2:
    st.markdown('<div class="section-heading">Add context</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Help us understand what great looks like for you.</div>', unsafe_allow_html=True)

    answers = {}
    for q in st.session_state.questions:
        answers[q["key"]] = st.text_input(
            q["question"],
            placeholder=q.get("example", ""),
            key=q["key"]
        )

    st.markdown("<br>", unsafe_allow_html=True)
    style = st.selectbox(
        "Writing style",
        ["Default", "Human", "Persuasive", "Analytical", "Storytelling"]
    )

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("← Back", use_container_width=True):
            st.session_state.step = 1
            st.rerun()
    with col2:
        if st.button("Build Prompt →", use_container_width=True):
            cleaned = {k: clean_input(v) for k, v in answers.items()}
            st.session_state.answers = cleaned
            with st.spinner("Crafting your prompt…"):
                st.session_state.final_prompt = build_prompt(
                    st.session_state.user_prompt, cleaned, style
                )
            st.session_state.step = 3
            st.rerun()

# ════════════════════════════════════════════════════════════════════════════
# STEP 3 — Optimised prompt + finetune
# ════════════════════════════════════════════════════════════════════════════
elif st.session_state.step == 3:
    st.markdown('<div class="section-heading">Your optimised prompt</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Ready to use — or fine-tune one aspect before running it.</div>', unsafe_allow_html=True)

    st.markdown(f'<div class="prompt-card">{st.session_state.final_prompt}</div>', unsafe_allow_html=True)

    # Copy helper
    st.code(st.session_state.final_prompt, language="markdown")

    st.markdown('<hr class="thin-divider">', unsafe_allow_html=True)
    st.markdown('<div class="section-heading" style="font-size:1rem;">🎛 Fine-tune one aspect</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Pick one dimension to sharpen — we\'ll rewrite just that part.</div>', unsafe_allow_html=True)

    aspect = st.selectbox(
        "What to improve",
        list(FINETUNE_OPTIONS.keys()),
        label_visibility="collapsed"
    )

    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("✦ Fine-tune", use_container_width=True):
            with st.spinner(f"Sharpening {aspect}…"):
                st.session_state.final_prompt = finetune_prompt(
                    st.session_state.final_prompt, aspect
                )
                st.session_state.finetuned = True
            st.rerun()
    with col2:
        if st.button("🚀 Generate Output", use_container_width=True):
            st.session_state.step = 4
            st.rerun()
    with col3:
        if st.button("↩ Start Over", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

    if st.session_state.finetuned:
        st.success(f"Prompt updated — {aspect} has been sharpened.")

# ════════════════════════════════════════════════════════════════════════════
# STEP 4 — Final output
# ════════════════════════════════════════════════════════════════════════════
elif st.session_state.step == 4:
    st.markdown('<div class="section-heading">Generated output</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Produced from your optimised prompt.</div>', unsafe_allow_html=True)

    if not st.session_state.output:
        with st.spinner("Generating…"):
            st.session_state.output = generate_output(st.session_state.final_prompt)
        st.rerun()

    st.markdown(f'<div class="output-card">{st.session_state.output}</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("← Back to Prompt", use_container_width=True):
            st.session_state.output = ""
            st.session_state.step = 3
            st.rerun()
    with col2:
        if st.button("↩ Start Over", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
