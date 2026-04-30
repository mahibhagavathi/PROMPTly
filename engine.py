from groq import Groq
import streamlit as st
import json, re

client = Groq(api_key=st.secrets["GROQ_API_KEY"])
MODEL = "llama-3.3-70b-versatile"

# ─────────────────────────────────────────────────────────────────────────────
# CLEAN INPUT
# ─────────────────────────────────────────────────────────────────────────────

def clean_input(text: str) -> str:
    if not text:
        return ""
    text = text.strip()
    banned = ["idc", "idk", "whatever", "none", "na", "n/a"]
    if any(word in text.lower() for word in banned) or len(text) < 3:
        return ""
    return text


# ─────────────────────────────────────────────────────────────────────────────
# FACTUALITY MODES
# Injected into every prompt build based on user's toggle selection.
# ─────────────────────────────────────────────────────────────────────────────

FACTUALITY_MODES = {
    "🎨 Creative Mode": {
        "description": "Bold ideas, vivid analogies, imaginative speculation. Best for content, storytelling, and ideation.",
        "injection": (
            "FACTUALITY SETTING — CREATIVE MODE: Embrace bold ideas, vivid analogies, imaginative "
            "framing, and speculative thinking. Prioritise originality and resonance over strict "
            "accuracy. Use storytelling, metaphor, and unexpected angles to make the output memorable."
        ),
    },
    "⚖️ Balanced Mode": {
        "description": "Solid reasoning with light creativity. Best for most everyday use-cases.",
        "injection": (
            "FACTUALITY SETTING — BALANCED MODE: Blend clear, evidence-based reasoning with occasional "
            "creative framing to keep the reader engaged. Be accurate on facts you are confident about, "
            "and clearly signal when you are speculating or simplifying."
        ),
    },
    "🔬 Strict Factual Mode": {
        "description": "Zero fabrication. High precision. Uncertainty must be stated explicitly.",
        "injection": (
            "FACTUALITY SETTING — STRICT FACTUAL MODE. Follow these rules absolutely:\n"
            "- Do NOT fabricate facts, statistics, sources, names, dates, or examples.\n"
            "- Only use information explicitly provided by the user or widely verifiable facts.\n"
            "- If information is missing or uncertain, say exactly: 'I don't know' or ask a "
            "  specific clarifying question. Never fill gaps with plausible-sounding guesses.\n"
            "- Do not invent citations, studies, or experts.\n"
            "- Precision and honesty are more important than sounding confident or complete."
        ),
    },
}


def get_factuality_injection(mode_key: str) -> str:
    return FACTUALITY_MODES.get(mode_key, {}).get("injection", "")


# ─────────────────────────────────────────────────────────────────────────────
# FOLLOW-UP QUESTIONS
# ─────────────────────────────────────────────────────────────────────────────

def generate_followups(_prompt: str) -> list[dict]:
    return [
        {
            "key":      "role",
            "question": "What role should the AI assume? (leave blank for A/B persona mode)",
            "example":  "e.g. CEO, Data Analyst, Tour Guide — or leave empty for two auto-generated perspectives",
        },
        {
            "key":      "goal",
            "question": "What is the goal of this content?",
            "example":  "e.g. Get an interview call, Increase followers, Drive more sales",
        },
        {
            "key":      "audience",
            "question": "Who is the target audience?",
            "example":  "e.g. Hiring Manager, Students, CEOs, Potential customers",
        },
        {
            "key":      "tone",
            "question": "What tone should the content carry?",
            "example":  "e.g. Professional, Conversational, Witty, Creative",
        },
        {
            "key":      "word_limit",
            "question": "Approximate word limit?",
            "example":  "e.g. 150, 300, 500, 1000",
        },
        {
            "key":      "context",
            "question": "Any extra context or constraints?",
            "example":  "e.g. Avoid jargon, Include a stat, Use bullet points only",
        },
    ]


# ─────────────────────────────────────────────────────────────────────────────
# STYLE BLOCK
# ─────────────────────────────────────────────────────────────────────────────

def get_style_block(style: str) -> str:
    styles = {
        "Default":      "",
        "Human":        "Write in a warm, natural, deeply human tone. Avoid robotic phrasing, buzzwords, and AI-sounding constructions. Use contractions, short punchy sentences, and real emotion.",
        "Persuasive":   "Make every line persuasive and psychologically compelling. Use social proof, urgency, contrast, and emotional triggers. The reader should feel compelled to act.",
        "Analytical":   "Prioritise structure, evidence, and logical flow. Use data thinking, cause-effect reasoning, and numbered insights. Sound like a senior consultant presenting findings.",
        "Storytelling": "Frame everything through narrative. Use a protagonist, conflict, and resolution arc. Make abstract ideas concrete through vivid micro-stories or analogies.",
    }
    return styles.get(style, "")


# ─────────────────────────────────────────────────────────────────────────────
# GROQ HELPER
# ─────────────────────────────────────────────────────────────────────────────

def groq_generate(prompt: str, system: str = None, temperature: float = 0.85) -> str:
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        max_tokens=1500,
        temperature=temperature,
    )
    return response.choices[0].message.content.strip()


# ─────────────────────────────────────────────────────────────────────────────
# PERSONA GENERATOR  (used when role field is left blank)
# Returns two contrasting expert personas suited to the user's topic.
# ─────────────────────────────────────────────────────────────────────────────

def generate_personas(user_prompt: str) -> tuple[str, str]:
    """
    Ask the LLM to suggest two contrasting expert personas for the given topic.
    Returns (persona_a_title, persona_b_title).
    """
    system = (
        "You are a creative prompt engineer. "
        "Given a user's topic, suggest two contrasting expert personas that would each produce "
        "a distinctly valuable and different perspective on that topic. "
        "Return ONLY a JSON object with keys 'persona_a' and 'persona_b'. "
        "Each value is a short persona title (max 8 words). No explanation, no markdown fences."
    )
    raw = groq_generate(
        f"Topic: {user_prompt}",
        system=system,
        temperature=0.9,
    )
    raw = re.sub(r"^```json|^```|```$", "", raw, flags=re.MULTILINE).strip()
    try:
        data = json.loads(raw)
        return data["persona_a"], data["persona_b"]
    except Exception:
        # Safe fallback
        return "Industry Expert", "Practical Insider"


# ─────────────────────────────────────────────────────────────────────────────
# CORE PROMPT BUILDER  (single version)
# ─────────────────────────────────────────────────────────────────────────────

def _build_single(user_prompt: str, answers: dict, style: str, role_override: str, factuality_injection: str) -> str:
    role        = role_override or answers.get("role", "") or "a world-class expert in this domain"
    goal        = answers.get("goal", "")       or "deliver maximum value to the reader"
    audience    = answers.get("audience", "")   or "thoughtful professionals"
    tone        = answers.get("tone", "")       or "engaging and clear"
    word_limit  = answers.get("word_limit", "") or "200"
    context     = answers.get("context", "")    or "none"
    style_block = get_style_block(style)

    system = (
        "You are an elite prompt engineer who has studied thousands of high-performing prompts. "
        "Your job is to transform vague user inputs into hyper-specific, richly layered prompts "
        "that unlock the best possible AI output. "
        "A great prompt has: a vivid role definition, a crystal-clear task, layered instructions "
        "with nuance, and tight constraints. "
        "Always return ONLY the final prompt — no explanation, no preamble, no meta-commentary."
    )

    user = f"""Transform this raw input into a world-class AI prompt.

RAW INPUT: "{user_prompt}"

CONTEXT PROVIDED:
- Role the AI should embody: {role}
- Core goal: {goal}
- Target audience: {audience}
- Desired tone: {tone}
- Word limit: {word_limit} words
- Extra constraints or context: {context}

STYLE DIRECTION: {style_block if style_block else "No specific style — use best judgement."}

{factuality_injection}

BUILD THE PROMPT USING THIS STRUCTURE:

**ROLE**
Define the AI's identity with depth — not just a job title, but a persona with experience, perspective, and expertise.

**TASK**
State the task with precision. Include the format, the angle, and what makes this piece different from generic output.

**AUDIENCE BRIEF**
Describe who will read this, what they care about, what they already know, and what would genuinely impress them.

**LAYERED INSTRUCTIONS**
Give 5–7 rich instructions that go beyond the obvious. Include things like: specific structural choices, what to avoid, a unique angle to take, how to open, how to close, what kind of examples to use.

**OUTPUT FORMAT**
Specify the exact format: sections, flow, length of each part.

**CONSTRAINTS**
- Word count: {word_limit} words
- Tone: {tone}
- Any hard rules from the extra context

Make this prompt so specific and well-crafted that even a mediocre AI would produce excellent output from it."""

    return groq_generate(user, system=system)


# ─────────────────────────────────────────────────────────────────────────────
# PUBLIC BUILD FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────

def build_prompt(user_prompt: str, answers: dict, style: str, factuality_mode: str) -> str:
    """Single-version build. Used when the user has provided a role."""
    injection = get_factuality_injection(factuality_mode)
    return _build_single(user_prompt, answers, style, role_override="", factuality_injection=injection)


def build_prompt_ab(
    user_prompt: str,
    answers: dict,
    style: str,
    factuality_mode: str,
) -> tuple[str, str, str, str]:
    """
    A/B version build. Used when role field is blank.
    Returns (persona_a_title, prompt_a, persona_b_title, prompt_b).
    """
    injection = get_factuality_injection(factuality_mode)
    persona_a, persona_b = generate_personas(user_prompt)

    prompt_a = _build_single(user_prompt, answers, style, role_override=persona_a, factuality_injection=injection)
    prompt_b = _build_single(user_prompt, answers, style, role_override=persona_b, factuality_injection=injection)

    return persona_a, prompt_a, persona_b, prompt_b


# ─────────────────────────────────────────────────────────────────────────────
# DYNAMIC FINETUNE OPTIONS
# Analyses the generated prompt and returns only relevant improvement levers.
# ─────────────────────────────────────────────────────────────────────────────

def generate_finetune_options(prompt_text: str) -> dict[str, str]:
    """
    Look at the actual generated prompt and return a dict of
    {display_label: finetune_instruction} relevant to that specific prompt.
    Never returns hook options for a travel itinerary, etc.
    """
    system = (
        "You are a prompt engineering specialist. "
        "You receive an AI prompt and must identify which aspects could be meaningfully improved. "
        "Return ONLY a JSON object where:\n"
        "- keys are short emoji-prefixed labels (max 4 words) e.g. '🗓️ Day Structure'\n"
        "- values are precise improvement instructions for that specific prompt (1–2 sentences)\n"
        "Rules:\n"
        "- Only include options that genuinely apply to this prompt's task type.\n"
        "- Never include 'Hook' for prompts about itineraries, resumes, summaries, data tasks, or analysis.\n"
        "- Never include 'Call to Action' for non-marketing prompts.\n"
        "- Aim for 4–6 options maximum.\n"
        "- Return ONLY the JSON object. No markdown fences. No explanation."
    )

    user = f"""Here is the prompt to analyse:

---
{prompt_text}
---

Return the JSON object of relevant finetune options."""

    raw = groq_generate(user, system=system, temperature=0.4)
    raw = re.sub(r"^```json|^```|```$", "", raw, flags=re.MULTILINE).strip()

    try:
        return json.loads(raw)
    except Exception:
        # Safe fallback with universal options
        return {
            "🎯 Task Clarity":    "Rewrite the task definition to be sharper and more specific. Remove all vagueness.",
            "👥 Audience Detail": "Rewrite the audience brief to be more psychologically precise and insightful.",
            "📋 Instructions":    "Enrich the layered instructions — add at least 2 more non-obvious, high-quality directives.",
            "📐 Output Format":   "Rewrite the output format to be clearer. Specify exact sections, flow, and length per part.",
        }


# ─────────────────────────────────────────────────────────────────────────────
# FINETUNE A SPECIFIC ASPECT
# ─────────────────────────────────────────────────────────────────────────────

def finetune_prompt(original_prompt: str, aspect: str, instruction: str) -> str:
    """
    Improve one specific aspect of the prompt.
    `aspect`      — display label (e.g. '🗓️ Day Structure')
    `instruction` — the dynamic instruction generated by generate_finetune_options()
    """
    system = (
        "You are a prompt engineering specialist. You receive an existing AI prompt and a specific "
        "improvement instruction. Return the FULL improved prompt — not just the changed section. "
        "Preserve everything that is already good. Only improve what the instruction targets. "
        "Return ONLY the final prompt. No explanation, no preamble."
    )

    user = f"""Here is the existing prompt:

---
{original_prompt}
---

IMPROVEMENT TARGET: {aspect}
INSTRUCTION: {instruction}

Return the full improved prompt."""

    return groq_generate(user, system=system)


# ─────────────────────────────────────────────────────────────────────────────
# GENERATE OUTPUT  (run the final prompt through the LLM)
# ─────────────────────────────────────────────────────────────────────────────

def generate_output(prompt: str) -> str:
    system = (
        "You are a world-class writer and thinker. Execute the following prompt with exceptional "
        "skill, depth, and craft. Produce something genuinely impressive — not generic."
    )
    return groq_generate(prompt, system=system)
