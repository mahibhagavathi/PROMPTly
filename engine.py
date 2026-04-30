import streamlit as st
import google.generativeai as genai

# -------- SAFE API INIT --------
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    st.error("🚨 API Key missing. Add it in Streamlit Secrets.")
    st.stop()

genai.configure(api_key=api_key)

# ✅ IMPORTANT: define model AFTER configure
model = genai.GenerativeModel("gemini-1.5-flash")
