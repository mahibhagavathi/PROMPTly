import streamlit as st
import google.generativeai as genai
from templates import TEMPLATES

# -------- API SETUP --------
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    st.error("🚨 API Key missing. Add it in Streamlit secrets.")
    st.stop()

genai.configure(api_key=api_key)

# ✅ MODEL INIT
model = genai.GenerativeModel("gemini-1.5-flash")


# -------- INTENT DETECTION --------
def detect_intent(prompt):
    p = prompt.lower()
    if any(x in p for x in ["code", "sql", "debug"]):
        return "technical"
    elif any(x in p for x in ["write", "post", "content", "blog"]):
        return "content"
    else:
        return "general"


# -------- FOLLOW-UP QUESTIONS --------
def generate_followups(prompt):
    try:
        response = model.generate_content(f"""
        You are an expert in prompt engineering.

        A user gave this prompt:
        "{prompt}"

        Ask 3 short follow-up questions to improve it.

        Focus on:
        - Goal
        - Audience
        - Constraints

        Return only questions. One per line.
        """)

        text = getattr(response, "text", "")

        questions = [
            q.strip("- ").strip()
            for q in text.split("\n")
            if q.strip()
        ]

        return questions[:3]

    except Exception as e:
        print("Error:", e)
        return [
            "What is the goal?",
            "Who is the audience?",
            "Any constraints (word limit, tone, format)?"
        ]


# -------- STYLE --------
def get_style_block(style):
    if style == "Human & Conversational":
        return """
Style Instructions:
- Write like a human
- Avoid generic phrases
- Use natural tone
"""
    elif style == "Balanced":
        return "Keep a clear and semi-formal tone."
    else:
        return ""


# -------- PROMPT BUILDER --------
def build_prompt(user_prompt, answers, style):

    intent = detect_intent(user_prompt)
    template = TEMPLATES.get(intent, TEMPLATES["general"])

    filled = {
        "role": answers.get("role", "expert"),
        "task": user_prompt,
        "goal": answers.get("goal", "inform"),
        "audience": answers.get("audience", "general audience"),
        "tone": answers.get("tone", "professional"),
        "word_limit": answers.get("word_limit", "150"),
        "constraints": answers.get("constraints", "Keep it clear"),
        "style_block": get_style_block(style)
    }

    return template.format(**filled)


# -------- OUTPUT --------
def generate_output(prompt):
    response = model.generate_content(prompt)
    return getattr(response, "text", "")


# -------- CHEATCODES --------
def apply_cheatcode(prompt, code):
    if code == "role":
        return prompt + "\nAct as an expert."
    elif code == "constraints":
        return prompt + "\nKeep it concise and structured."
    elif code == "structure":
        return prompt + "\nGive output in bullet points."
    return prompt
