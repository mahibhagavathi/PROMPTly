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

# ── Accessibility: Session state defaults ─────────────────────────────────────
for key, default in {
    # Core app state
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
    # Accessibility state
    "a11y_theme":       "default",      # default | protanopia | deuteranopia | tritanopia | high_contrast
    "a11y_font_size":   16,             # base px size
    "a11y_voice_text":  "",             # last transcribed voice text
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ─────────────────────────────────────────────────────────────────────────────
# ACCESSIBILITY SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ♿ Accessibility Settings")
    st.caption("Customize PROMPTly for your needs.")

    # ── Color Vision / Theme ──────────────────────────────────────────────────
    st.markdown("### 🎨 Color Vision Mode")
    theme_options = {
        "default":       "🌐 Default",
        "protanopia":    "🔴 Protanopia (Red-blind)",
        "deuteranopia":  "🟢 Deuteranopia (Green-blind)",
        "tritanopia":    "🔵 Tritanopia (Blue-blind)",
        "high_contrast": "⬛ High Contrast",
    }
    selected_theme = st.selectbox(
        "Select color mode",
        options=list(theme_options.keys()),
        format_func=lambda k: theme_options[k],
        index=list(theme_options.keys()).index(st.session_state.a11y_theme),
        key="theme_select",
        help="Choose a color mode suited to your vision needs.",
    )
    if selected_theme != st.session_state.a11y_theme:
        st.session_state.a11y_theme = selected_theme
        st.rerun()

    st.divider()

    # ── Font Size ─────────────────────────────────────────────────────────────
    st.markdown("### 🔤 Text Size")
    font_size = st.slider(
        "Base font size (px)",
        min_value=12,
        max_value=24,
        value=st.session_state.a11y_font_size,
        step=1,
        key="font_slider",
        help="Adjust text size across the entire app.",
    )
    if font_size != st.session_state.a11y_font_size:
        st.session_state.a11y_font_size = font_size
        st.rerun()

    # Readable size label
    size_labels = {range(12, 14): "Small", range(14, 17): "Default", range(17, 20): "Large", range(20, 25): "Extra Large"}
    current_label = next((v for r, v in size_labels.items() if font_size in r), "Custom")
    st.caption(f"Current: **{current_label}** ({font_size}px)")

    st.divider()

    # ── Voice Input Info ──────────────────────────────────────────────────────
    st.markdown("### 🎙️ Voice Input")
    st.caption(
        "A microphone button appears on Step 1. "
        "Click it, speak your idea, and the text will auto-fill. "
        "Works with English and Indian languages (Hindi, Tamil, Telugu, Bengali, etc.)."
    )

    st.divider()

    # ── Multi-language note ───────────────────────────────────────────────────
    st.markdown("### 🌍 Language Support")
    st.caption(
        "You can type or speak in any language. "
        "The app will process your prompt as-is. "
        "For best results, typing in English is recommended for AI output quality."
    )

    st.divider()
    st.markdown("### ℹ️ Keyboard Shortcuts")
    st.caption("• **Tab** — move between fields\n• **Enter** — submit forms\n• **Esc** — cancel voice recording")


# ─────────────────────────────────────────────────────────────────────────────
# THEME CSS VARIABLES
# Each theme overrides only the CSS custom properties — layout/structure intact.
# ─────────────────────────────────────────────────────────────────────────────
THEME_VARS = {
    "default": """
        --color-bg:           #dddfeb;
        --color-surface:      #ffffff;
        --color-text:         #1f2a44;
        --color-text-muted:   #6b7280;
        --color-accent:       #a78bfa;
        --color-accent-dark:  #2f3a5f;
        --color-border:       #e5e7eb;
        --color-before-bg:    #fef2f2;
        --color-before-border:#fecaca;
        --color-before-text:  #7f1d1d;
        --color-badge-bg:     #f1f5f9;
        --color-fact-sel-bg:  #f5f3ff;
        --color-fact-sel-bdr: #a78bfa;
        --color-success-bg:   #d1fae5;
        --color-success-text: #065f46;
        --color-btn-primary:  #2f3a5f;
        --color-btn-hover:    #1f2a44;
        --color-focus-ring:   rgba(167,139,250,0.4);
    """,
    # Protanopia: avoid pure red signals; shift accent to blue/purple, warnings to amber
    "protanopia": """
        --color-bg:           #e8eaf6;
        --color-surface:      #ffffff;
        --color-text:         #1a237e;
        --color-text-muted:   #5c6bc0;
        --color-accent:       #1565c0;
        --color-accent-dark:  #0d1b4b;
        --color-border:       #c5cae9;
        --color-before-bg:    #fff8e1;
        --color-before-border:#ffcc02;
        --color-before-text:  #5d3a00;
        --color-badge-bg:     #e8eaf6;
        --color-fact-sel-bg:  #e3f2fd;
        --color-fact-sel-bdr: #1565c0;
        --color-success-bg:   #e3f2fd;
        --color-success-text: #0d47a1;
        --color-btn-primary:  #0d1b4b;
        --color-btn-hover:    #1a237e;
        --color-focus-ring:   rgba(21,101,192,0.4);
    """,
    # Deuteranopia: avoid green signals; use blue/orange palette
    "deuteranopia": """
        --color-bg:           #fef9f0;
        --color-surface:      #ffffff;
        --color-text:         #3e2723;
        --color-text-muted:   #8d6e63;
        --color-accent:       #f57c00;
        --color-accent-dark:  #3e2723;
        --color-border:       #d7ccc8;
        --color-before-bg:    #fff3e0;
        --color-before-border:#ffb74d;
        --color-before-text:  #4e2000;
        --color-badge-bg:     #fbe9e7;
        --color-fact-sel-bg:  #fff3e0;
        --color-fact-sel-bdr: #f57c00;
        --color-success-bg:   #e3f2fd;
        --color-success-text: #0d47a1;
        --color-btn-primary:  #3e2723;
        --color-btn-hover:    #4e342e;
        --color-focus-ring:   rgba(245,124,0,0.4);
    """,
    # Tritanopia: avoid blue signals; use warm red/green palette
    "tritanopia": """
        --color-bg:           #f1f8e9;
        --color-surface:      #ffffff;
        --color-text:         #1b5e20;
        --color-text-muted:   #558b2f;
        --color-accent:       #c62828;
        --color-accent-dark:  #1b5e20;
        --color-border:       #c8e6c9;
        --color-before-bg:    #fce4ec;
        --color-before-border:#ef9a9a;
        --color-before-text:  #880e4f;
        --color-badge-bg:     #f1f8e9;
        --color-fact-sel-bg:  #fce4ec;
        --color-fact-sel-bdr: #c62828;
        --color-success-bg:   #f1f8e9;
        --color-success-text: #1b5e20;
        --color-btn-primary:  #1b5e20;
        --color-btn-hover:    #2e7d32;
        --color-focus-ring:   rgba(198,40,40,0.4);
    """,
    # High Contrast: WCAG AAA ratios, clear borders everywhere
    "high_contrast": """
        --color-bg:           #000000;
        --color-surface:      #1a1a1a;
        --color-text:         #ffffff;
        --color-text-muted:   #e0e0e0;
        --color-accent:       #ffff00;
        --color-accent-dark:  #ffff00;
        --color-border:       #ffffff;
        --color-before-bg:    #330000;
        --color-before-border:#ff6666;
        --color-before-text:  #ffcccc;
        --color-badge-bg:     #222222;
        --color-fact-sel-bg:  #333300;
        --color-fact-sel-bdr: #ffff00;
        --color-success-bg:   #003300;
        --color-success-text: #66ff66;
        --color-btn-primary:  #ffff00;
        --color-btn-hover:    #ffffaa;
        --color-focus-ring:   rgba(255,255,0,0.6);
    """,
}

active_theme_vars = THEME_VARS[st.session_state.a11y_theme]
fs = st.session_state.a11y_font_size
is_hc = st.session_state.a11y_theme == "high_contrast"

# High contrast uses inverted button text
hc_btn_text = "#000000" if is_hc else "#ffffff"
hc_btn_text_hover = "#000000" if is_hc else "#ffffff"

st.markdown(f"""
<style>
/* ── Accessibility CSS custom properties (theme) ─────────────────────────── */
:root {{
    {active_theme_vars}
    --font-size-base: {fs}px;
    --font-size-sm:   {max(fs - 3, 10)}px;
    --font-size-xs:   {max(fs - 4, 9)}px;
    --font-size-lg:   {fs + 4}px;
    --font-size-xl:   {fs + 10}px;
}}

/* ── Typography imports ───────────────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@500;600;700&family=DM+Sans:wght@300;400;500&display=swap');

/* ── Base ─────────────────────────────────────────────────────────────────── */
html, body, [class*="css"] {{
    font-family: 'DM Sans', sans-serif;
    font-size: var(--font-size-base);
}}

.stApp {{
    background: var(--color-bg);
    color: var(--color-text);
}}

#MainMenu, footer, header {{ visibility: hidden; }}
.block-container {{ padding-top: 2.5rem; padding-bottom: 3rem; max-width: 800px; }}

/* ── Hero ─────────────────────────────────────────────────────────────────── */
.hero {{
    text-align: center;
    padding: 2.5rem 0 1.5rem;
    border-bottom: 2px solid var(--color-border);
    margin-bottom: 2.5rem;
}}
.hero-logo {{
    font-family: 'Syne', sans-serif;
    font-weight: 700;
    font-size: var(--font-size-xl);
    color: var(--color-text);
}}
.hero-sub {{
    font-size: var(--font-size-sm);
    color: var(--color-text-muted);
    font-style: italic;
}}

/* ── Step bar ─────────────────────────────────────────────────────────────── */
.step-bar {{
    display: flex;
    justify-content: center;
    gap: 0.5rem;
    margin-bottom: 2rem;
    align-items: center;
}}
.step-dot {{
    width: 10px; height: 10px;
    border-radius: 50%;
    background: var(--color-border);
    /* Non-color indicator for screen readers handled via aria */
}}
.step-dot.active {{
    background: var(--color-accent);
    outline: 2px solid var(--color-accent);
    outline-offset: 2px;
}}
.step-dot.done {{
    background: var(--color-accent-dark);
}}
.step-label {{
    font-family: 'Syne', sans-serif;
    font-size: var(--font-size-xs);
    color: var(--color-text-muted);
    text-transform: uppercase;
    font-weight: 700;
}}

/* ── Typography ───────────────────────────────────────────────────────────── */
.section-heading {{
    font-family: 'Syne', sans-serif;
    font-weight: 600;
    font-size: var(--font-size-lg);
    color: var(--color-accent-dark);
}}
.section-sub {{
    font-size: var(--font-size-sm);
    color: var(--color-text-muted);
}}

/* ── Inputs ───────────────────────────────────────────────────────────────── */
.stTextArea textarea, .stTextInput input {{
    background: var(--color-surface) !important;
    border: {('2px' if is_hc else '1px')} solid var(--color-border) !important;
    border-radius: 10px !important;
    color: var(--color-text) !important;
    font-size: var(--font-size-base) !important;
}}
.stTextArea textarea:focus, .stTextInput input:focus {{
    border-color: var(--color-accent) !important;
    box-shadow: 0 0 0 3px var(--color-focus-ring) !important;
    outline: 2px solid var(--color-accent) !important;
}}
.stSelectbox > div > div {{
    background: var(--color-surface) !important;
    border: {('2px' if is_hc else '1px')} solid var(--color-border) !important;
    border-radius: 10px !important;
    color: var(--color-text) !important;
    font-size: var(--font-size-base) !important;
}}

/* ── Buttons ──────────────────────────────────────────────────────────────── */
.stButton > button {{
    background: var(--color-btn-primary) !important;
    color: {hc_btn_text} !important;
    border-radius: 8px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 600 !important;
    font-size: var(--font-size-base) !important;
    border: {('2px solid #ffffff' if is_hc else 'none')} !important;
    min-height: 44px !important; /* WCAG touch target */
    transition: background 0.15s, box-shadow 0.15s;
}}
.stButton > button:hover {{
    background: var(--color-btn-hover) !important;
    color: {hc_btn_text_hover} !important;
}}
.stButton > button:focus-visible {{
    outline: 3px solid var(--color-accent) !important;
    outline-offset: 2px !important;
    box-shadow: 0 0 0 4px var(--color-focus-ring) !important;
}}

/* ── Cards ────────────────────────────────────────────────────────────────── */
.prompt-card, .output-card {{
    background: var(--color-surface);
    border: {('2px' if is_hc else '1px')} solid var(--color-border);
    border-radius: 12px;
    padding: 1.5rem;
    color: var(--color-text);
    white-space: pre-wrap;
    font-size: var(--font-size-sm);
    line-height: 1.8;
}}

/* ── Before / After ───────────────────────────────────────────────────────── */
.before-box {{
    background: var(--color-before-bg);
    border: {('2px' if is_hc else '1px')} solid var(--color-before-border);
    border-radius: 10px;
    padding: 1rem 1.25rem;
    color: var(--color-before-text);
    font-size: var(--font-size-sm);
    font-style: italic;
}}
.after-label {{
    font-family: 'Syne', sans-serif;
    font-size: var(--font-size-xs);
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--color-text-muted);
    margin-bottom: 0.4rem;
}}
/* Text + icon so meaning isn't color-only */
.transform-arrow {{
    text-align: center;
    font-size: 1.4rem;
    margin: 0.5rem 0;
    color: var(--color-accent);
}}

/* ── A/B persona badge ────────────────────────────────────────────────────── */
.persona-badge {{
    background: var(--color-badge-bg);
    border: 1px solid var(--color-border);
    border-radius: 999px;
    display: inline-block;
    padding: 0.2rem 0.85rem;
    font-size: var(--font-size-xs);
    font-family: 'Syne', sans-serif;
    font-weight: 600;
    color: var(--color-text);
    margin-bottom: 0.75rem;
}}

/* ── Factuality cards ─────────────────────────────────────────────────────── */
.fact-card {{
    background: var(--color-surface);
    border: {('2px' if is_hc else '1px')} solid var(--color-border);
    border-radius: 10px;
    padding: 0.85rem 1.1rem;
    margin-bottom: 0.5rem;
}}
.fact-card.selected {{
    border-color: var(--color-fact-sel-bdr);
    background: var(--color-fact-sel-bg);
    /* Added text indicator alongside color */
}}
.fact-title {{
    font-family: 'Syne', sans-serif;
    font-weight: 600;
    font-size: var(--font-size-sm);
    color: var(--color-accent-dark);
}}
.fact-desc {{
    font-size: var(--font-size-xs);
    color: var(--color-text-muted);
    margin-top: 2px;
}}

/* ── Divider ──────────────────────────────────────────────────────────────── */
.thin-divider {{
    border-top: {('2px' if is_hc else '1px')} solid var(--color-border);
    margin: 1.5rem 0;
}}

/* ── Form labels ──────────────────────────────────────────────────────────── */
.stTextArea label, .stTextInput label, .stSelectbox label {{
    font-family: 'Syne', sans-serif !important;
    font-size: var(--font-size-xs) !important;
    font-weight: 600 !important;
    color: var(--color-text-muted) !important;
    text-transform: uppercase !important;
}}

/* ── Sidebar ──────────────────────────────────────────────────────────────── */
[data-testid="stSidebar"] {{
    background: var(--color-surface) !important;
    border-right: {('2px' if is_hc else '1px')} solid var(--color-border) !important;
}}
[data-testid="stSidebar"] * {{
    color: var(--color-text) !important;
}}

/* ── Skip-to-content link (screen reader & keyboard) ─────────────────────── */
.skip-link {{
    position: absolute;
    top: -100px;
    left: 0;
    background: var(--color-accent-dark);
    color: #fff;
    padding: 0.5rem 1rem;
    border-radius: 0 0 8px 0;
    font-weight: 700;
    z-index: 9999;
    text-decoration: none;
    transition: top 0.2s;
}}
.skip-link:focus {{ top: 0; }}

/* ═══════════════════════════════════════════════════════════════════════════
   VOICE INPUT WIDGET
   ═══════════════════════════════════════════════════════════════════════════ */
.voice-container {{
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-bottom: 0.5rem;
}}

/* Mic button */
#micBtn {{
    width: 48px;
    height: 48px;
    border-radius: 50%;
    border: 2px solid var(--color-accent, #a78bfa);
    background: var(--color-surface, #fff);
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.3rem;
    transition: background 0.2s, transform 0.1s, box-shadow 0.2s;
    flex-shrink: 0;
    outline: none;
    position: relative;
}}
#micBtn:hover {{
    background: var(--color-fact-sel-bg, #f5f3ff);
    transform: scale(1.08);
}}
#micBtn:focus-visible {{
    outline: 3px solid var(--color-accent, #a78bfa);
    outline-offset: 3px;
}}
#micBtn.recording {{
    background: #dc2626;
    border-color: #dc2626;
    animation: pulse 1s infinite;
}}
#micBtn.recording .mic-icon {{
    filter: brightness(10);
}}

/* Pulse animation for active recording */
@keyframes pulse {{
    0%   {{ box-shadow: 0 0 0 0 rgba(220,38,38,0.5); }}
    70%  {{ box-shadow: 0 0 0 12px rgba(220,38,38,0); }}
    100% {{ box-shadow: 0 0 0 0 rgba(220,38,38,0); }}
}}

/* Status text */
#voiceStatus {{
    font-size: var(--font-size-xs, 12px);
    color: var(--color-text-muted, #6b7280);
    font-family: 'DM Sans', sans-serif;
    min-width: 180px;
    transition: color 0.2s;
}}
#voiceStatus.listening {{
    color: #dc2626;
    font-weight: 600;
}}
#voiceStatus.done {{
    color: #059669;
    font-weight: 600;
}}
#voiceStatus.error {{
    color: #d97706;
    font-weight: 600;
}}

/* Language selector for voice */
#langSelect {{
    font-size: var(--font-size-xs, 12px);
    border: 1px solid var(--color-border, #e5e7eb);
    border-radius: 6px;
    padding: 0.25rem 0.4rem;
    background: var(--color-surface, #fff);
    color: var(--color-text, #1f2a44);
    cursor: pointer;
}}

/* ── Alerts / Status — always icon + text, never color alone ─────────────── */
.a11y-success {{
    background: var(--color-success-bg);
    color: var(--color-success-text);
    border: 1px solid var(--color-success-text);
    border-radius: 8px;
    padding: 0.6rem 1rem;
    font-size: var(--font-size-sm);
    display: flex;
    align-items: center;
    gap: 0.5rem;
}}
.a11y-warning {{
    background: #fffbeb;
    color: #92400e;
    border: 1px solid #fbbf24;
    border-radius: 8px;
    padding: 0.6rem 1rem;
    font-size: var(--font-size-sm);
    display: flex;
    align-items: center;
    gap: 0.5rem;
}}
</style>

<!-- Skip to main content (keyboard / screen-reader) -->
<a class="skip-link" href="#main-content" tabindex="0">Skip to main content</a>

<!-- Landmark for screen readers -->
<div id="main-content" role="main" aria-label="PROMPTly prompt enhancement tool"></div>
""", unsafe_allow_html=True)

# ── Inline JS: Web Speech API voice input component ──────────────────────────
# This injects a mic button + language selector into Step 1.
# It uses the Web Speech API (SpeechRecognition) supported in Chrome/Edge/Safari.
# Transcribed text is posted to a Streamlit text_input via JS → DOM manipulation.
VOICE_INPUT_HTML = """
<div class="voice-container" role="group" aria-label="Voice input controls">
    <!-- Language selector for speech recognition -->
    <select id="langSelect" aria-label="Select language for voice input" title="Voice input language">
        <option value="en-IN">🇮🇳 English (India)</option>
        <option value="en-US">🇺🇸 English (US)</option>
        <option value="en-GB">🇬🇧 English (UK)</option>
        <option value="hi-IN">🇮🇳 हिन्दी (Hindi)</option>
        <option value="te-IN">🇮🇳 తెలుగు (Telugu)</option>
        <option value="ta-IN">🇮🇳 தமிழ் (Tamil)</option>
        <option value="kn-IN">🇮🇳 ಕನ್ನಡ (Kannada)</option>
        <option value="ml-IN">🇮🇳 മലയാളം (Malayalam)</option>
        <option value="mr-IN">🇮🇳 मराठी (Marathi)</option>
        <option value="bn-IN">🇮🇳 বাংলা (Bengali)</option>
        <option value="gu-IN">🇮🇳 ગુજરાતી (Gujarati)</option>
        <option value="pa-IN">🇮🇳 ਪੰਜਾਬੀ (Punjabi)</option>
        <option value="ur-PK">🇵🇰 اردو (Urdu)</option>
    </select>

    <!-- Mic button: accessible with aria-label and role -->
    <button
        id="micBtn"
        type="button"
        role="button"
        aria-label="Start voice recording — click to speak your idea"
        aria-pressed="false"
        title="Click to record voice input"
    >
        <span class="mic-icon" aria-hidden="true">🎙️</span>
    </button>

    <!-- Live status region announced by screen readers -->
    <span id="voiceStatus" role="status" aria-live="polite" aria-atomic="true">
        🎙️ Click mic to speak
    </span>
</div>

<script>
(function () {
    // ── Feature detection ────────────────────────────────────────────────────
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const btn    = document.getElementById('micBtn');
    const status = document.getElementById('voiceStatus');
    const langSel = document.getElementById('langSelect');

    if (!SpeechRecognition) {
        status.textContent = '⚠️ Voice not supported in this browser. Try Chrome or Edge.';
        status.className = 'error';
        btn.disabled = true;
        btn.setAttribute('aria-label', 'Voice input not supported in this browser');
        return;
    }

    let recognition = null;
    let isRecording = false;

    // ── Helper: find the Streamlit textarea and inject text ──────────────────
    // Streamlit renders textareas inside shadow-like wrappers; we find by
    // placeholder text to target the correct field.
    function getTargetTextarea() {
        // Try to find the "Your idea" textarea via placeholder
        const textareas = document.querySelectorAll('textarea');
        for (const ta of textareas) {
            if (
                ta.placeholder &&
                (ta.placeholder.includes('e.g.') || ta.placeholder.includes('rough idea') || ta.placeholder.includes('LinkedIn'))
            ) {
                return ta;
            }
        }
        // Fallback: first visible textarea
        return textareas[0] || null;
    }

    // ── Inject text into Streamlit textarea (triggers React's onChange) ───────
    function injectText(text) {
        const ta = getTargetTextarea();
        if (!ta) {
            status.textContent = '⚠️ Could not find input field. Please type manually.';
            status.className = 'error';
            return;
        }
        const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
            window.HTMLTextAreaElement.prototype, 'value'
        ).set;
        nativeInputValueSetter.call(ta, text);
        ta.dispatchEvent(new Event('input', { bubbles: true }));
        ta.dispatchEvent(new Event('change', { bubbles: true }));
        ta.focus();
        // Move cursor to end
        ta.selectionStart = ta.selectionEnd = ta.value.length;
    }

    // ── Start / stop recording ────────────────────────────────────────────────
    function startRecording() {
        recognition = new SpeechRecognition();
        recognition.lang = langSel.value;
        recognition.interimResults = true;
        recognition.maxAlternatives = 1;
        recognition.continuous = false;

        recognition.onstart = () => {
            isRecording = true;
            btn.classList.add('recording');
            btn.setAttribute('aria-pressed', 'true');
            btn.setAttribute('aria-label', 'Stop recording — click to stop');
            btn.innerHTML = '<span class="mic-icon" aria-hidden="true">⏹️</span>';
            status.textContent = '🔴 Listening… speak now';
            status.className = 'listening';
        };

        recognition.onresult = (event) => {
            const transcript = Array.from(event.results)
                .map(r => r[0].transcript)
                .join('');
            // Show interim result live
            status.textContent = `"${transcript}"`;
            if (event.results[0].isFinal) {
                injectText(transcript);
                status.textContent = `✅ Got it: "${transcript.substring(0, 60)}${transcript.length > 60 ? '…' : ''}"`;
                status.className = 'done';
            }
        };

        recognition.onerror = (event) => {
            const errorMessages = {
                'not-allowed':   '🚫 Microphone access denied. Please allow mic in browser settings.',
                'no-speech':     '🔇 No speech detected. Please try again.',
                'network':       '🌐 Network error. Check your connection.',
                'aborted':       '⏹️ Recording stopped.',
                'audio-capture': '🎤 No microphone found.',
            };
            status.textContent = errorMessages[event.error] || `⚠️ Error: ${event.error}`;
            status.className = 'error';
            stopRecording();
        };

        recognition.onend = () => {
            stopRecording();
            // If status is still "listening", means no result came through
            if (status.className === 'listening') {
                status.textContent = '🔇 No speech detected. Try again.';
                status.className = 'error';
            }
        };

        recognition.start();
    }

    function stopRecording() {
        isRecording = false;
        if (recognition) {
            try { recognition.stop(); } catch(e) {}
            recognition = null;
        }
        btn.classList.remove('recording');
        btn.setAttribute('aria-pressed', 'false');
        btn.setAttribute('aria-label', 'Start voice recording — click to speak your idea');
        btn.innerHTML = '<span class="mic-icon" aria-hidden="true">🎙️</span>';
    }

    // ── Button click handler ──────────────────────────────────────────────────
    btn.addEventListener('click', () => {
        if (isRecording) {
            stopRecording();
            if (status.className === 'listening') {
                status.textContent = '⏹️ Recording stopped.';
                status.className = '';
            }
        } else {
            startRecording();
        }
    });

    // ── Keyboard: Escape stops recording ─────────────────────────────────────
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && isRecording) {
            stopRecording();
            status.textContent = '⏹️ Recording stopped (Esc pressed).';
            status.className = '';
        }
    });

    // ── Language change restarts if currently recording ───────────────────────
    langSel.addEventListener('change', () => {
        if (isRecording) {
            stopRecording();
            setTimeout(startRecording, 300);
        }
    });
})();
</script>
"""

# ── Hero ──────────────────────────────────────────────────────────────────────
# Added role="banner" for screen readers; aria-label on the logo
theme_badge = ""
if st.session_state.a11y_theme != "default":
    badge_labels = {
        "protanopia":    "♿ Protanopia Mode",
        "deuteranopia":  "♿ Deuteranopia Mode",
        "tritanopia":    "♿ Tritanopia Mode",
        "high_contrast": "♿ High Contrast Mode",
    }
    badge = badge_labels.get(st.session_state.a11y_theme, "")
    theme_badge = f'<span style="font-size:0.75rem;background:var(--color-accent);color:var(--color-surface);padding:0.2rem 0.7rem;border-radius:999px;font-weight:700;" role="status" aria-live="polite">{badge}</span>'

st.markdown(f"""
<header role="banner">
    <div class="hero">
        <div class="hero-logo" aria-label="PROMPTly - prompt enhancement tool">✦ PROMPTly</div>
        <div class="hero-sub" role="doc-subtitle">
            Communicate better with AI — because the output is only as good as your prompt.
        </div>
        <div style="margin-top:10px; font-size:var(--font-size-sm); opacity:0.8;" role="note">
            ⚠️ This is not a chatbot. It is a prompt enhancement tool that helps you refine, structure, and improve your prompts for better AI outputs.
        </div>
        {f'<div style="margin-top:10px;">{theme_badge}</div>' if theme_badge else ''}
    </div>
</header>
""", unsafe_allow_html=True)

# ── Step indicator ─────────────────────────────────────────────────────────────
steps = ["Idea", "Refine", "Prompt", "Output"]

def step_bar(current: int):
    # Accessible step indicator: uses aria-current for screen readers
    dots = ""
    for i, label in enumerate(steps, 1):
        if i == current:
            dots += f'<span class="step-label" aria-current="step" aria-label="Current step: {label}">{label}</span>'
            dots += f'<div class="step-dot active" role="img" aria-label="Step {i} of {len(steps)}: {label} (current)"></div>'
        elif i < current:
            dots += f'<div class="step-dot done" role="img" aria-label="Step {i}: {steps[i-1]} (completed)"></div>'
        else:
            dots += f'<div class="step-dot" role="img" aria-label="Step {i}: {steps[i-1]} (upcoming)"></div>'
    st.markdown(
        f'<nav aria-label="Progress steps"><div class="step-bar" role="list">{dots}</div></nav>',
        unsafe_allow_html=True
    )

step_bar(st.session_state.step)


# ═════════════════════════════════════════════════════════════════════════════
# STEP 1 — Raw idea
# ═════════════════════════════════════════════════════════════════════════════
if st.session_state.step == 1:
    st.markdown(
        '<h1 class="section-heading" id="step1-heading">What do you want to create?</h1>',
        unsafe_allow_html=True
    )
    st.markdown(
        '<p class="section-sub" role="doc-subtitle">Drop in a rough idea — we\'ll shape it into something powerful. '
        'You can type or use the microphone button below.</p>',
        unsafe_allow_html=True
    )
    st.markdown("<br>", unsafe_allow_html=True)

    # ── Voice Input Component ─────────────────────────────────────────────────
    # Render the mic + language selector above the text area
    st.markdown(
        '<p style="font-size:var(--font-size-xs);color:var(--color-text-muted);margin-bottom:0.3rem;" '
        'aria-label="Voice input section">'
        '🎙️ <strong>Voice Input</strong> — choose your language, then click the mic button to speak:</p>',
        unsafe_allow_html=True
    )
    st.components.v1.html(VOICE_INPUT_HTML, height=70, scrolling=False)

    # ── Text area — aria-labelledby links to heading ──────────────────────────
    user_input = st.text_area(
        "Your idea (type or use voice input above)",
        placeholder="e.g. Write a LinkedIn post on Agentic AI, Write a cold email for sales outreach, Build a study plan for learning SQL",
        height=110,
        label_visibility="visible",
        key="idea_textarea",
        help="Describe your prompt idea. You can type in any language.",
    )

    # Multilingual hint
    st.markdown(
        '<p style="font-size:var(--font-size-xs);color:var(--color-text-muted);margin-top:0.25rem;">'
        '🌍 You can type in English, Hindi, Telugu, Tamil, or any language.</p>',
        unsafe_allow_html=True
    )

    if st.button(
        "Continue → Step 2",
        use_container_width=True,
        help="Move to the next step to add context to your idea",
        key="btn_step1_continue",
    ):
        if user_input.strip():
            st.session_state.user_prompt = user_input.strip()
            st.session_state.questions   = generate_followups(user_input)
            st.session_state.step        = 2
            st.rerun()
        else:
            # Accessible warning: icon + text, not color alone
            st.markdown(
                '<div class="a11y-warning" role="alert" aria-live="assertive">'
                '⚠️ <strong>Please enter an idea</strong> before continuing.'
                '</div>',
                unsafe_allow_html=True
            )


# ═════════════════════════════════════════════════════════════════════════════
# STEP 2 — Context + Factuality Mode
# ═════════════════════════════════════════════════════════════════════════════
elif st.session_state.step == 2:
    st.markdown(
        '<h1 class="section-heading" id="step2-heading">Add context</h1>',
        unsafe_allow_html=True
    )
    st.markdown(
        '<p class="section-sub">Help us understand what great looks like for you.</p>',
        unsafe_allow_html=True
    )
    st.markdown("<br>", unsafe_allow_html=True)

    answers = {}
    for q in st.session_state.questions:
        # Accessible labels: use the question as the label (never hidden)
        answers[q["key"]] = st.text_input(
            q["question"],
            placeholder=q.get("example", ""),
            key=q["key"],
            help=f'Example: {q.get("example", "")}' if q.get("example") else None,
        )

    st.markdown("<br>", unsafe_allow_html=True)
    style = st.selectbox(
        "Writing style",
        ["Default", "Human", "Persuasive", "Analytical", "Storytelling"],
        help="Choose the tone and style for the final prompt output.",
    )

    # ── Factuality Mode picker ────────────────────────────────────────────────
    st.markdown('<hr class="thin-divider" role="separator">', unsafe_allow_html=True)
    st.markdown(
        '<h2 class="section-heading" style="font-size:var(--font-size-base);" id="factuality-heading">'
        '🎚️ Factuality Mode</h2>',
        unsafe_allow_html=True
    )
    st.markdown(
        '<p class="section-sub">Controls how the AI handles accuracy vs creativity in its output.</p>',
        unsafe_allow_html=True
    )
    st.markdown("<br>", unsafe_allow_html=True)

    mode_keys = list(FACTUALITY_MODES.keys())
    fact_cols = st.columns(len(mode_keys))
    for col, mode_key in zip(fact_cols, mode_keys):
        mode = FACTUALITY_MODES[mode_key]
        is_selected = st.session_state.factuality_mode == mode_key
        with col:
            selected_class = "selected" if is_selected else ""
            # Non-color indicator: "✓ Selected" text inside the card
            selected_indicator = '<span style="font-size:0.7rem;font-weight:700;color:var(--color-fact-sel-bdr);">✓ SELECTED</span>' if is_selected else ""
            st.markdown(
                f"""<div class="fact-card {selected_class}" role="region" aria-label="{mode_key} factuality mode{' — currently selected' if is_selected else ''}">
                    <div class="fact-title">{mode_key}</div>
                    <div class="fact-desc">{mode["description"]}</div>
                    {selected_indicator}
                </div>""",
                unsafe_allow_html=True,
            )
            btn_label = "✓ Active" if is_selected else f"Select {mode_key}"
            if st.button(
                btn_label,
                key=f"mode_{mode_key}",
                use_container_width=True,
                help=f"Activate {mode_key}: {mode['description']}",
            ):
                st.session_state.factuality_mode = mode_key
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("← Back to Step 1", use_container_width=True, help="Return to the idea input step"):
            st.session_state.step = 1
            st.rerun()
    with col2:
        if st.button("Build Prompt →", use_container_width=True, help="Generate your optimised prompt"):
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
    # Added role="region" and labels so screen readers understand context
    st.markdown('<p class="after-label" aria-hidden="true">Before</p>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="before-box" role="note" aria-label="Your original unoptimised idea">'
        f'"{st.session_state.user_prompt}"</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="transform-arrow" role="img" aria-label="Transformed and optimised by PROMPTly">↓ optimised by PROMPTly</div>',
        unsafe_allow_html=True
    )
    st.markdown('<p class="after-label" aria-hidden="true">After</p>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # ── A/B view ─────────────────────────────────────────────────────────────
    if st.session_state.is_ab:
        st.markdown(
            '<h1 class="section-heading">Two Perspectives</h1>',
            unsafe_allow_html=True
        )
        st.markdown(
            '<p class="section-sub">Role was left blank — here are two expert takes. '
            'Pick one to proceed.</p>',
            unsafe_allow_html=True,
        )
        st.markdown("<br>", unsafe_allow_html=True)

        col_a, col_b = st.columns(2)

        with col_a:
            st.markdown(
                f'<div class="persona-badge" aria-label="Version A — {st.session_state.persona_a}">'
                f'Version A — {st.session_state.persona_a}</div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                f'<div class="prompt-card" role="article" aria-label="Version A prompt">'
                f'{st.session_state.prompt_a}</div>',
                unsafe_allow_html=True
            )
            if st.button(
                "Use Version A →",
                use_container_width=True,
                key="pick_a",
                help=f"Select Version A: {st.session_state.persona_a}",
            ):
                st.session_state.final_prompt     = st.session_state.prompt_a
                st.session_state.active_version   = "A"
                st.session_state.finetune_options = generate_finetune_options(st.session_state.prompt_a)
                st.session_state.is_ab            = False
                st.rerun()

        with col_b:
            st.markdown(
                f'<div class="persona-badge" aria-label="Version B — {st.session_state.persona_b}">'
                f'Version B — {st.session_state.persona_b}</div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                f'<div class="prompt-card" role="article" aria-label="Version B prompt">'
                f'{st.session_state.prompt_b}</div>',
                unsafe_allow_html=True
            )
            if st.button(
                "Use Version B →",
                use_container_width=True,
                key="pick_b",
                help=f"Select Version B: {st.session_state.persona_b}",
            ):
                st.session_state.final_prompt     = st.session_state.prompt_b
                st.session_state.active_version   = "B"
                st.session_state.finetune_options = generate_finetune_options(st.session_state.prompt_b)
                st.session_state.is_ab            = False
                st.rerun()

    # ── Single prompt view ────────────────────────────────────────────────────
    else:
        st.markdown(
            '<h1 class="section-heading">Your optimised prompt</h1>',
            unsafe_allow_html=True
        )
        st.markdown(
            '<p class="section-sub">Ready to use — or fine-tune one aspect before running it.</p>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="prompt-card" role="article" aria-label="Optimised prompt ready to use">'
            f'{st.session_state.final_prompt}</div>',
            unsafe_allow_html=True
        )

        with st.expander("📋 Copy-friendly version", expanded=False):
            st.code(st.session_state.final_prompt, language="markdown")

        # ── Context-aware finetune ────────────────────────────────────────────
        st.markdown('<hr class="thin-divider" role="separator">', unsafe_allow_html=True)
        st.markdown(
            '<h2 class="section-heading" style="font-size:var(--font-size-base);">🎛 Fine-tune one aspect</h2>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<p class="section-sub">Options are generated for this specific prompt — no irrelevant levers.</p>',
            unsafe_allow_html=True,
        )
        st.markdown("<br>", unsafe_allow_html=True)

        finetune_options = st.session_state.finetune_options
        aspect = None
        if finetune_options:
            aspect = st.selectbox(
                "What to improve",
                list(finetune_options.keys()),
                label_visibility="visible",
                help="Choose which aspect of the prompt to fine-tune.",
            )
            st.caption(f"*{finetune_options[aspect]}*")

        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            if st.button(
                "✦ Fine-tune Prompt",
                use_container_width=True,
                disabled=not aspect,
                help=f"Sharpen the '{aspect}' aspect of your prompt" if aspect else "Select an aspect to fine-tune",
                key="btn_finetune",
            ):
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
            if st.button(
                "🚀 Generate Output",
                use_container_width=True,
                help="Generate final AI output from your optimised prompt",
                key="btn_generate",
            ):
                st.session_state.output = ""
                st.session_state.step   = 4
                st.rerun()
        with col3:
            if st.button(
                "↩ Start Over",
                use_container_width=True,
                help="Clear everything and start fresh",
                key="btn_restart_3",
            ):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()

        if st.session_state.finetuned:
            # Accessible success: icon + text, not color alone
            st.markdown(
                f'<div class="a11y-success" role="status" aria-live="polite">'
                f'✅ <strong>Prompt updated</strong> — {aspect} has been sharpened.</div>',
                unsafe_allow_html=True
            )

    if st.button(
        "← Back to Context",
        use_container_width=False,
        help="Return to Step 2 to modify context",
        key="btn_back_to_context",
    ):
        st.session_state.step = 2
        st.rerun()


# ═════════════════════════════════════════════════════════════════════════════
# STEP 4 — Final output
# ═════════════════════════════════════════════════════════════════════════════
elif st.session_state.step == 4:
    st.markdown(
        '<h1 class="section-heading">Generated output</h1>',
        unsafe_allow_html=True
    )
    st.markdown(
        '<p class="section-sub">Produced from your optimised prompt.</p>',
        unsafe_allow_html=True
    )

    if not st.session_state.output:
        with st.spinner("Generating your output…"):
            st.session_state.output = generate_output(st.session_state.final_prompt)
        st.rerun()

    st.markdown(
        f'<div class="output-card" role="article" aria-label="AI generated output">'
        f'{st.session_state.output}</div>',
        unsafe_allow_html=True
    )

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button(
            "← Back to Prompt",
            use_container_width=True,
            help="Return to Step 3 to modify your prompt",
            key="btn_back_to_prompt",
        ):
            st.session_state.output    = ""
            st.session_state.finetuned = False
            st.session_state.step      = 3
            st.rerun()
    with col2:
        if st.button(
            "↩ Start Over",
            use_container_width=True,
            help="Clear everything and start a new prompt from scratch",
            key="btn_restart_4",
        ):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
