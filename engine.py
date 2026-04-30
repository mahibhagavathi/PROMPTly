import google.generativeai as genai
import streamlit as st

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-pro")


# ---------------- CLEAN INPUT ----------------
def clean_input(text: str):
    if not text:
        return ""

    text = text.lower().strip()

    banned = [
        "fuck", "shit", "idc", "idk",
        "whatever", "none", "na", "n/a"
    ]

    if any(word in text for word in banned) or len(text) < 3:
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
            "question": "What is the goal?",
            "example": "e.g. Educate, Persuade, Inform"
        },
        {
            "key": "audience",
            "question": "Who is the audience?",
            "example": "e.g. Beginners, Professionals, Students"
        },
        {
            "key": "tone",
            "question": "Preferred tone?",
            "example": "e.g. Engaging, Professional, Casual"
        },
        {
            "key": "word_limit",
            "question": "Word limit?",
            "example": "e.g. 100, 200, 500"
        }
    ]


# ---------------- STYLE BLOCK ----------------
def get_style_block(style):
    if style == "Human":
        return "Write in a natural, human-like, non-generic tone."
    elif style == "Persuasive":
        return "Make it persuasive and impactful."
    elif style == "Analytical":
        return "Focus on structured, logical, insight-driven output."
    return ""


# ---------------- BUILD PROMPT ----------------
def build_prompt(user_prompt, answers, style):
    role = answers.get("role", "") or "expert in the subject"
    goal = answers.get("goal", "") or "provide valuable insights"
    audience = answers.get("audience", "") or "professionals"
    tone = answers.get("tone", "") or "engaging"
    word_limit = answers.get("word_limit", "") or "150"

    style_block = get_style_block(style)

    response = model.generate_content(f"""
You are an expert prompt engineer.

User input:
"{user_prompt}"

Context:
Role: {role}
Goal: {goal}
Audience: {audience}
Tone: {tone}
Word limit: {word_limit}

CRITICAL RULES:
- Ignore bad, abusive, or irrelevant inputs
- Improve vague inputs intelligently
- Expand role into domain expertise:
    Consultant → insights, trends, strategy
    Content Creator → storytelling, hooks, engagement
    Analyst → structured insights, data thinking

Create a HIGH-QUALITY prompt.

Format:

Act as a [refined role].

Task:
[clear rewritten task]

Goal:
[improved goal]

Audience:
[refined audience]

Instructions:
- Add depth based on role
- Include examples if relevant
- Ensure clarity and usefulness

Output Format:
- Hook
- Body
- Key insight
- CTA

Constraints:
- {word_limit} words
- Tone: {tone}
- Clear and engaging

{style_block}
""")

    return response.text


# ---------------- GENERATE OUTPUT ----------------
def generate_output(prompt):
    response = model.generate_content(prompt)
    return response.text
