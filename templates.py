TEMPLATES = {
    "content": """
Act as a {role}.

Task: {task}

Goal: {goal}
Audience: {audience}
Tone: {tone}

Structure:
- Hook
- Key insight
- Example
- Call to action

Constraints:
- Max {word_limit} words
- Clear and engaging

{style_block}
""",

    "technical": """
Act as a {role}.

Task: {task}

Requirements:
- Step-by-step explanation
- Clear logic

Constraints:
{constraints}

{style_block}
""",

    "general": """
Task: {task}

Audience: {audience}
Tone: {tone}

Constraints:
{constraints}

{style_block}
"""
}
