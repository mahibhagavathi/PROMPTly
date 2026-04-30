# ✦ PROMPTly

> Better prompts → better AI output.

PROMPTly is an AI-powered prompt engineering tool that turns rough ideas into production-ready prompts through a guided conversation.  
Instead of writing prompts manually, you describe what you want — PROMPTly does the structuring, refinement, and optimization for you.

Link: https://promptly-ai.streamlit.app/

---

## 🧠 Tech Stack

- **Frontend:** Streamlit  
- **LLM:** LLaMA 3.3 (Groq API)  
- **Backend:** Python 3.10+  
- **State Management:** Streamlit session state  
- **Parsing:** JSON + regex fallback

---

## 🚀 Problem

Most users write vague prompts and get inconsistent AI outputs, leading to repeated trial-and-error.

PROMPTly solves this by:
- Extracting missing context through conversation
- Applying prompt engineering best practices automatically
- Generating structured, high-quality prompts in one shot

---

## ✨ Features

### 🗣️ Conversational Prompt Builder
Ask users targeted follow-up questions based on their task (goal, tone, audience, constraints) instead of static forms.

---

### 🆚 A/B Persona Mode
If no role is provided, PROMPTly generates two expert perspectives automatically.

Example:
- Luxury Travel Consultant → curated, premium itinerary  
- Local Resident → authentic, offbeat experiences  

Users can compare and choose the best direction.

---

### 📸 Before / After View
Shows how raw input transforms into an optimized prompt.

**Before:**  
`write a linkedin post on agentic ai`

**After:**  
A structured prompt with role, tone, constraints, and output guidelines.

---

### 🎚️ Factuality Modes
Control how the AI behaves:

- 🎨 Creative → imaginative and expressive output  
- ⚖️ Balanced → mix of reasoning + creativity  
- 🔬 Strict Factual → no hallucinations, no invented data  

---

### 🎛️ Context-Aware Refinement Engine
Suggests improvements based on prompt type:

- Travel → structure, pacing, hidden gems  
- Resume → impact, ATS keywords, alignment  
- Writing → hooks, tone, CTA  
- Research → clarity, conciseness, structure  

---

### 🌐 Multilingual Support
- Input in any language (Hindi, Tamil, Telugu, etc.)
- Output can be enforced in any language
- Supports mixed-language inputs (Hinglish, bilingual prompts)

---

### 📝 Writing Style Selector
- Default → general use  
- Human → natural tone  
- Persuasive → marketing/sales  
- Analytical → structured reasoning  
- Storytelling → narrative-driven content  

---

### 🔁 Iteration Loop
Refine prompts without restarting:
**generate → refine → regenerate → final output**

---
