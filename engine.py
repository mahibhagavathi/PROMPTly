from groq import Groq
import streamlit as st

client = Groq(api_key=st.secrets["GROQ_API_KEY"])
MODEL = "llama-3.3-70b-versatile"

# ---------------- CLEAN INPUT ----------------
def clean_input(text: str):
    if not text:
        return ""
    text = text.strip()
    banned = ["idc", "idk", "whatever", "none", "na", "n/a"]
    if any(word in text.lower() for word in banned) or len(text) < 3:
        return ""
    return text

# ---------------- FOLLOW-UP QUESTIONS ----------------
def generate_followups(prompt):
    return [
        {
            "key": "role",
            "question": "What role should the AI assume?",
            "example": "e.g. Data Analyst, Consultant, Content Creator"
        },
        {
            "key": "goal",
            "question": "What is the goal of this content?",
            "example": "e.g. Get an interview call, Increase my followers, Understand a concept clearly, Drive more sales, Break down a complex problem"
        },
        {
            "key": "audience",
            "question": "Who is the target audience?",
            "example": "e.g. Hiring Manager, Students, CEOs, Potential customers "
        },
        {
            "key": "tone",
            "question": "What tone should the content carry?",
            "example": "e.g. Professional, Conversational, Witty, Creative, or a combination of tones"
        },
        {
            "key": "word_limit",
            "question": "Approximate word limit?",
            "example": "e.g. 150, 300, 500, 1000, etc"
        },
        {
            "key": "context",
            "question": "Any extra context or constraints?",
            "example": "e.g. Avoid jargon, Include a stat, Use bullet points only"
        }
    ]

# ---------------- STYLE BLOCK ----------------
def get_style_block(style):
    styles = {
        "Default":      "",
        "Human":        "Write in a warm, natural, deeply human tone. Avoid robotic phrasing, buzzwords, and AI-sounding constructions. Use contractions, short punchy sentences, and real emotion.",
        "Persuasive":   "Make every line persuasive and psychologically compelling. Use social proof, urgency, contrast, and emotional triggers. The reader should feel compelled to act.",
        "Analytical":   "Prioritise structure, evidence, and logical flow. Use data thinking, cause-effect reasoning, and numbered insights. Sound like a senior consultant presenting findings.",
        "Storytelling": "Frame everything through narrative. Use a protagonist, conflict, and resolution arc. Make abstract ideas concrete through vivid micro-stories or analogies."
    }
    return styles.get(style, "")

# ---------------- GROQ HELPER ----------------
def groq_generate(prompt: str, system: str = None) -> str:
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        max_tokens=1500,
        temperature=0.85,
    )
    return response.choices[0].message.content.strip()

# ---------------- BUILD PROMPT ----------------
def build_prompt(user_prompt, answers, style):
    role       = answers.get("role", "")       or "a world-class expert in this domain"
    goal       = answers.get("goal", "")       or "deliver maximum value to the reader"
    audience   = answers.get("audience", "")   or "thoughtful professionals"
    tone       = answers.get("tone", "")       or "engaging and clear"
    word_limit = answers.get("word_limit", "") or "200"
    context    = answers.get("context", "")    or "none"
    style_block = get_style_block(style)

    system = """You are an elite prompt engineer who has studied thousands of high-performing prompts.
Your job is to transform vague user inputs into hyper-specific, richly layered prompts that unlock the best possible AI output.
A great prompt has: a vivid role definition, a crystal-clear task, layered instructions with nuance, and tight constraints.
Always return ONLY the final prompt — no explanation, no preamble, no meta-commentary."""

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


# ---------------- FINETUNE OPTIONS ----------------
FINETUNE_OPTIONS = {
    "🪝 Hook":         "Rewrite only the hook section of this prompt to be more powerful, surprising, and scroll-stopping. The hook must grab attention in the very first line.",
    "🎯 Task Clarity": "Rewrite only the task definition to be sharper, more specific, and unambiguous. Remove all vagueness.",
    "👥 Audience":     "Rewrite only the audience brief to be more precise and psychologically insightful. Add detail about what this audience cares about and what would impress them.",
    "📋 Instructions": "Rewrite only the layered instructions section to be richer and more nuanced. Add at least 2 more high-quality, non-obvious instructions.",
    "🎨 Tone & Style": "Rewrite the tone and style instructions to be more vivid and specific. Replace generic tone words with precise, evocative descriptions.",
    "📐 Format":       "Rewrite only the output format section to be clearer and more structured. Specify exact sections, word counts per section, and logical flow."
}

def finetune_prompt(original_prompt: str, aspect: str) -> str:
    instruction = FINETUNE_OPTIONS[aspect]

    system = """You are a prompt engineering specialist. You receive an existing AI prompt and a specific improvement instruction.
Return the FULL improved prompt — not just the changed section.
Preserve everything that's already good. Only improve what the instruction targets.
Return ONLY the final prompt. No explanation, no preamble."""

    user = f"""Here is the existing prompt:

---
{original_prompt}
---

IMPROVEMENT INSTRUCTION:
{instruction}

Return the full improved prompt."""

    return groq_generate(user, system=system)


# ---------------- GENERATE OUTPUT ----------------
def generate_output(prompt: str) -> str:
    system = "You are a world-class writer and thinker. Execute the following prompt with exceptional skill, depth, and craft. Produce something genuinely impressive — not generic."
    return groq_generate(prompt, system=system)
