import streamlit as st
import google.generativeai as genai
from templates import TEMPLATES

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-pro")


# -------- Intent Detection --------
def detect_intent(prompt):
    p = prompt.lower()
    if any(x in p for x in ["code", "sql", "debug"]):
        return "technical"
    elif any(x in p for x in ["write", "post", "content", "blog"]):
        return "content"
    else:
        return "general"


# -------- Follow-up Questions --------
def generate_followups(prompt):
    response = model.generate_content(f"""
Given this prompt: "{prompt}"

Ask 3 concise follow-up questions to improve it.
Focus on missing:
- Goal
- Audience
- Constraints (like word limit, format)

Return only questions.
""")

    questions = [
        q.strip("- ").strip()
        for q in response.text.split("\n")
        if q.strip()
    ]

    return questions[:3]


# -------- Humanization --------
def get_style_block(style):
    if style == "Human & Conversational":
        return """
Style Instructions:
- Write in a natural, human tone
- Avoid sounding robotic or generic
- Use conversational phrasing
- Avoid clichés
- Add personality and variation
"""
    elif style == "Balanced":
        return """
Style Instructions:
- Keep a semi-formal tone
- Ensure clarity and readability
"""
    else:
        return ""


# -------- Prompt Builder --------
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
        "constraints": answers.get("constraints", "Keep it clear and structured"),
        "style_block": get_style_block(style)
    }

    return template.format(**filled)


# -------- Output --------
def generate_output(prompt):
    response = model.generate_content(prompt)
    return response.text


# -------- Cheatcodes --------
def apply_cheatcode(prompt, code):
    if code == "role":
        return prompt + "\nAct as an expert."
    elif code == "constraints":
        return prompt + "\nKeep it concise and structured."
    elif code == "structure":
        return prompt + "\nGive output in bullet points."
    return prompt
