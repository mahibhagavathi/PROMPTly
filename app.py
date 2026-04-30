import streamlit as st
from engine import (
    generate_followups,
    build_prompt,
    build_prompt_ab,
    generate_output,
    finetune_prompt,
    generate_finetune_options,
    clean_input,
    FACTUALITY_MODES,
)

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="PROMPTly", page_icon="✦", layout="centered")

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@500;600;700&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

.stApp { background: #dddfeb; color: #1f2a44; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 2.5rem; padding-bottom: 3rem; max-width: 800px; }

/* ── Hero ── */
.hero { text-align: center; padding: 2.5rem 0 1.5rem; border-bottom: 1px solid #e5e7eb; margin-bottom: 2.5rem; }
.hero-logo { font-family: 'Syne', sans-serif; font-weight: 700; font-size: 2.8rem; color: #1f2a44; }
.hero-sub { font-size: 0.95rem; color: #6b7280; font-style: italic; }

/* ── Step bar ── */
.step-bar { display: flex; justify-content: center; gap: 0.5rem; margin-bottom: 2rem; align-items: center; }
.step-dot { width: 8px; height: 8px; border-radius: 50%; background: #d1d5db; }
.step-dot.active { background: #a78bfa; }
.step-dot.done   { background: #2f3a5f; }
.step-label { font-family: 'Syne', sans-serif; font-size: 0.7rem; color: #6b7280; text-transform: uppercase; }

/* ── Typography ── */
.section-heading { font-family: 'Syne', sans-serif; font-weight: 600; font-size: 1.3rem; color: #2f3a5f; }
.section-sub { font-size: 0.85rem; color: #6b7280; }

/* ── Inputs ── */
.stTextArea textarea, .stTextInput input {
    background: #ffffff !important; border: 1px solid #e5e7eb !important;
    border-radius: 10px !important; color: #1f2a44 !important;
}
.stTextArea textarea:focus, .stTextInput input:focus {
    border-color: #a78bfa !important; box-shadow: 0 0 0 2px rgba(167,139,250,0.15) !important;
}
.stSelectbox > div > div {
    background: #ffffff !important; border: 1px solid #e5e7eb !important;
    border-radius: 10px !important; color: #1f2a44 !important;
}

/* ── Buttons ── */
.stButton > button {
    background: #2f3a5f !important; color: #ffffff !important;
    border-radius: 8px !important; font-family: 'Syne', sans-serif !important; font-weight: 600 !important;
}
.stButton > button:hover { background: #1f2a44 !important; }

/* ── Cards ── */
.prompt-card, .output-card {
    background: #ffffff; border: 1px solid #e5e7eb;
    border-radius: 12px; padding: 1.5rem; color: #374151;
    white-space: pre-wrap; font-size: 0.88rem; line-height: 1.75;
}

/* ── Before / After ── */
.before-box {
    background: #fef2f2; border: 1px solid #fecaca;
    border-radius: 10px; padding: 1rem 1.25rem;
    color: #7f1d1d; font-size: 0.88rem; font-style: italic;
}
.after-label {
    font-family: 'Syne', sans-serif; font-size: 0.7rem; font-weight: 700;
    text-transform: uppercase; letter-spacing: 0.08em; color: #6b7280; margin-bottom: 0.4rem;
}
.transform-arrow { text-align: center; font-size: 1.4rem; margin: 0.5rem 0; color: #a78bfa; }

/* ── A/B persona badge ── */
.persona-badge {
    background: #f1f5f9; border: 1px solid #e5e7eb; border-radius: 999px;
    display: inline-block; padding: 0.2rem 0.85rem; font-size: 0.72rem;
    font-family: 'Syne', sans-serif; font-weight: 600; color: #2f3a5f; margin-bottom: 0.75rem;
}

/* ── Factuality cards ── */
.fact-card {
    background: #ffffff; border: 1px solid #e5e7eb;
    border-radius: 10px; padding: 0.85rem 1.1rem; margin-bottom: 0.5rem;
}
.fact-card.selected { border-color: #a78bfa; background: #f5f3ff; }
.fact-title { font-family: 'Syne', sans-serif; font-weight: 600; font-size: 0.9rem; color: #2f3a5f; }
.fact-desc { font-size: 0.78rem; color: #6b7280; margin-top: 2px; }

/* ── Divider ── */
.thin-divider { border-top: 1px solid #e5e7eb; margin: 1.5rem 0; }

/* ── Labels ── */
.stTextArea label, .stTextInput label, .stSelectbox label {
    font-family: 'Syne', sans-serif !important; font-size: 0.75rem !important;
    font-weight: 600 !important; color: #6b7280 !important; text-transform: uppercase !important;
}
</style>
""", unsafe_allow_html=True)

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-logo">✦ PROMPTly</div>
    <div class="hero-sub">Communicate better with AI — because it's only as good as your prompt.</div>
</div>
""", unsafe_allow_html=True)

# ── Session state defaults ─────────────────────────────────────────────────────
for key, default in {
    "step":             1,
    "user_prompt":      "",
    "questions":        [],
    "answers":          {},
    "style":            "Default",
    "factuality_mode":  "⚖️ Balanced Mode",
    "is_ab":            False,
    "persona_a":        "",
    "persona_b":        "",
    "prompt_a":         "",
    "prompt_b":         "",
    "final_prompt":     "",
    "active_version":   "A",
    "finetune_options": {},
    "output":           "",
    "finetuned":        False,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ── Step indicator ────────────────────────────────────────────────────────────
steps = ["Idea", "Refine", "Prompt", "Output"]

def step_bar(current: int):
    dots = ""
    for i, label in enumerate(steps, 1):
        if i == current:
            dots += f'<span class="step-label">{label}</span>'
        cls = "active" if i == current else ("done" if i < current else "step-dot")
        dots += f'<div class="step-dot {cls}"></div>'
    st.markdown(f'<div class="step-bar">{dots}</div>', unsafe_allow_html=True)

step_bar(st.session_state.step)


# ═════════════════════════════════════════════════════════════════════════════
# STEP 1 — Raw idea
# ═════════════════════════════════════════════════════════════════════════════
if st.session_state.step == 1:
    st.markdown('<div class="section-heading">What do you want to create?</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Drop in a rough idea — we\'ll shape it into something powerful.</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    user_input = st.text_area(
        "Your idea",
        placeholder="e.g. Write a LinkedIn post on Agentic AI",
        height=110,
        label_visibility="collapsed",
    )

    if st.button("Continue →", use_container_width=True):
        if user_input.strip():
            st.session_state.user_prompt = user_input.strip()
            st.session_state.questions   = generate_followups(user_input)
            st.session_state.step        = 2
            st.rerun()
        else:
            st.warning("Enter an idea to get started.")


# ═════════════════════════════════════════════════════════════════════════════
# STEP 2 — Context + Factuality Mode
# ═════════════════════════════════════════════════════════════════════════════
elif st.session_state.step == 2:
    st.markdown('<div class="section-heading">Add context</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Help us understand what great looks like for you.</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    answers = {}
    for q in st.session_state.questions:
        answers[q["key"]] = st.text_input(
            q["question"],
            placeholder=q.get("example", ""),
            key=q["key"],
        )

    st.markdown("<br>", unsafe_allow_html=True)
    style = st.selectbox("Writing style", ["Default", "Human", "Persuasive", "Analytical", "Storytelling"])

    # ── Factuality Mode picker ────────────────────────────────────────────────
    st.markdown('<hr class="thin-divider">', unsafe_allow_html=True)
    st.markdown('<div class="section-heading" style="font-size:1rem;">🎚️ Factuality Mode</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Controls how the AI handles accuracy vs creativity in its output.</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    mode_keys = list(FACTUALITY_MODES.keys())
    fact_cols = st.columns(len(mode_keys))
    for col, mode_key in zip(fact_cols, mode_keys):
        mode = FACTUALITY_MODES[mode_key]
        is_selected = st.session_state.factuality_mode == mode_key
        with col:
            selected_class = "selected" if is_selected else ""
            st.markdown(
                f"""<div class="fact-card {selected_class}">
                    <div class="fact-title">{mode_key}</div>
                    <div class="fact-desc">{mode["description"]}</div>
                </div>""",
                unsafe_allow_html=True,
            )
            btn_label = "✓ Active" if is_selected else "Select"
            if st.button(btn_label, key=f"mode_{mode_key}", use_container_width=True):
                st.session_state.factuality_mode = mode_key
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("← Back", use_container_width=True):
            st.session_state.step = 1
            st.rerun()
    with col2:
        if st.button("Build Prompt →", use_container_width=True):
            cleaned  = {k: clean_input(v) for k, v in answers.items()}
            st.session_state.answers = cleaned
            st.session_state.style   = style
            role_given = cleaned.get("role", "")

            if role_given:
                with st.spinner("Crafting your prompt…"):
                    st.session_state.final_prompt     = build_prompt(
                        st.session_state.user_prompt, cleaned, style, st.session_state.factuality_mode
                    )
                    st.session_state.finetune_options = generate_finetune_options(st.session_state.final_prompt)
                st.session_state.is_ab = False
            else:
                with st.spinner("Generating two perspectives…"):
                    pa, prompt_a, pb, prompt_b = build_prompt_ab(
                        st.session_state.user_prompt, cleaned, style, st.session_state.factuality_mode
                    )
                    st.session_state.persona_a        = pa
                    st.session_state.prompt_a         = prompt_a
                    st.session_state.persona_b        = pb
                    st.session_state.prompt_b         = prompt_b
                    st.session_state.final_prompt     = prompt_a
                    st.session_state.active_version   = "A"
                    st.session_state.finetune_options = generate_finetune_options(prompt_a)
                st.session_state.is_ab = True

            st.session_state.step = 3
            st.rerun()


# ═════════════════════════════════════════════════════════════════════════════
# STEP 3 — Prompt result + Before/After + Finetune
# ═════════════════════════════════════════════════════════════════════════════
elif st.session_state.step == 3:

    # ── Before / After block ──────────────────────────────────────────────────
    st.markdown('<div class="after-label">Before</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="before-box">"{st.session_state.user_prompt}"</div>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="transform-arrow">↓ optimised by PROMPTly</div>', unsafe_allow_html=True)
    st.markdown('<div class="after-label">After</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # ── A/B view ─────────────────────────────────────────────────────────────
    if st.session_state.is_ab:
        st.markdown('<div class="section-heading">Two Perspectives</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="section-sub">Role was left blank — here are two expert takes. Pick one to proceed.</div>',
            unsafe_allow_html=True,
        )
        st.markdown("<br>", unsafe_allow_html=True)

        col_a, col_b = st.columns(2)

        with col_a:
            st.markdown(
                f'<div class="persona-badge">Version A — {st.session_state.persona_a}</div>',
                unsafe_allow_html=True,
            )
            st.markdown(f'<div class="prompt-card">{st.session_state.prompt_a}</div>', unsafe_allow_html=True)
            if st.button("Use Version A →", use_container_width=True, key="pick_a"):
                st.session_state.final_prompt     = st.session_state.prompt_a
                st.session_state.active_version   = "A"
                st.session_state.finetune_options = generate_finetune_options(st.session_state.prompt_a)
                st.session_state.is_ab            = False
                st.rerun()

        with col_b:
            st.markdown(
                f'<div class="persona-badge">Version B — {st.session_state.persona_b}</div>',
                unsafe_allow_html=True,
            )
            st.markdown(f'<div class="prompt-card">{st.session_state.prompt_b}</div>', unsafe_allow_html=True)
            if st.button("Use Version B →", use_container_width=True, key="pick_b"):
                st.session_state.final_prompt     = st.session_state.prompt_b
                st.session_state.active_version   = "B"
                st.session_state.finetune_options = generate_finetune_options(st.session_state.prompt_b)
                st.session_state.is_ab            = False
                st.rerun()

    # ── Single prompt view ────────────────────────────────────────────────────
    else:
        st.markdown('<div class="section-heading">Your optimised prompt</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="section-sub">Ready to use — or fine-tune one aspect before running it.</div>',
            unsafe_allow_html=True,
        )
        st.markdown(f'<div class="prompt-card">{st.session_state.final_prompt}</div>', unsafe_allow_html=True)

        with st.expander("📋 Copy-friendly version"):
            st.code(st.session_state.final_prompt, language="markdown")

        # ── Context-aware finetune ────────────────────────────────────────────
        st.markdown('<hr class="thin-divider">', unsafe_allow_html=True)
        st.markdown(
            '<div class="section-heading" style="font-size:1rem;">🎛 Fine-tune one aspect</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="section-sub">Options are generated for this specific prompt — no irrelevant levers.</div>',
            unsafe_allow_html=True,
        )
        st.markdown("<br>", unsafe_allow_html=True)

        finetune_options = st.session_state.finetune_options
        aspect = None
        if finetune_options:
            aspect = st.selectbox("What to improve", list(finetune_options.keys()), label_visibility="collapsed")
            st.caption(f"*{finetune_options[aspect]}*")

        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            if st.button("✦ Fine-tune", use_container_width=True, disabled=not aspect):
                with st.spinner(f"Sharpening {aspect}…"):
                    st.session_state.final_prompt = finetune_prompt(
                        st.session_state.final_prompt,
                        aspect,
                        finetune_options[aspect],
                    )
                    st.session_state.finetuned        = True
                    st.session_state.finetune_options = generate_finetune_options(st.session_state.final_prompt)
                st.rerun()
        with col2:
            if st.button("🚀 Generate Output", use_container_width=True):
                st.session_state.output = ""
                st.session_state.step   = 4
                st.rerun()
        with col3:
            if st.button("↩ Start Over", use_container_width=True):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()

        if st.session_state.finetuned:
            st.success(f"Prompt updated — {aspect} has been sharpened.")

    if st.button("← Back to Context", use_container_width=False):
        st.session_state.step = 2
        st.rerun()


# ═════════════════════════════════════════════════════════════════════════════
# STEP 4 — Final output
# ═════════════════════════════════════════════════════════════════════════════
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
            st.session_state.output    = ""
            st.session_state.finetuned = False
            st.session_state.step      = 3
            st.rerun()
    with col2:
        if st.button("↩ Start Over", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
