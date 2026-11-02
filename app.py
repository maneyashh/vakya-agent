import streamlit as st
import google.generativeai as genai
from sarvamai import SarvamAI
from PIL import Image

st.set_page_config(page_title="Vakya-Agent OS", layout="wide")
st.title("🚀 Vakya-Agent: Multilingual Voice-to-Code")

# Sidebar for API Keys
st.sidebar.header("Configuration")
gemini_key = st.sidebar.text_input("Gemini API Key", type="password")
sarvam_key = st.sidebar.text_input("Sarvam API Key", type="password")

col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Input Context")
    img_file = st.file_uploader("📸 Upload Problem Screenshot", type=["png", "jpg", "jpeg"])
    
    # NEW: Dropdown for Language Selection!
    target_language = st.selectbox("💻 Target Programming Language", ["C++", "Python", "Java", "JavaScript", "C"])
    
    user_command = st.text_input("🗣️ Command (Hinglish/Marathi)", value=f"Is problem ka optimized {target_language} solution likh")
    generate_btn = st.button("Generate Code 🧠", use_container_width=True)

with col2:
    st.subheader("2. Agent Output")
    if generate_btn:
        if not gemini_key or not sarvam_key:
            st.error("⚠️ Please paste both API keys in the sidebar.")
        elif not img_file:
            st.error("⚠️ Please upload a screenshot of the problem.")
        else:
            try:
                # 1. Gemini Code Generation
                genai.configure(api_key=gemini_key, transport="rest")
                gemini_model = genai.GenerativeModel('gemini-3.8-flash')
                
                img = Image.open(img_file)
                # Prompt dynamically updates to the chosen language
                prompt = f"The user asked: '{user_command}'. Write a highly optimized {target_language} solution based on the screenshot. Output ONLY raw {target_language} code. No markdown."
                
                with st.spinner(f"🧠 Gemini is analyzing and writing {target_language}..."):
                    response = gemini_model.generate_content([prompt, img])
                    clean_code = response.text.replace('```cpp', '').replace('```python', '').replace('```java', '').replace('```', '').strip()
                    
                    # Sets syntax highlighting color format automatically
                    highlight_lang = "cpp" if target_language == "C++" else target_language.lower()
                    st.code(clean_code, language=highlight_lang)
                
                # 2. Sarvam TTS Confirmation (Dynamic Audio)
                with st.spinner("🔊 Generating Sarvam audio..."):
                    sarvam_client = SarvamAI(api_subscription_key=sarvam_key)
                    tts_response = sarvam_client.text_to_speech.convert(
                        text=f"Bhai, {target_language} solution ready hai. Code screen par aa gaya hai.",
                        target_language_code="hi-IN"
                    )
                    st.audio(tts_response.audio, format="audio/wav")
                    st.success("✅ Execution Complete!")
                    
            except Exception as e:
                st.error(f"Network/API Error: {e}")