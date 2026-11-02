import streamlit as st
import google.generativeai as genai
from sarvamai import SarvamAI
from PIL import Image
from audio_recorder_streamlit import audio_recorder
import tempfile
import os

st.set_page_config(page_title="Vakya-Agent OS", layout="wide")
st.title("🚀 Vakya-Agent: Multilingual Voice-to-Code")

st.sidebar.header("Configuration")
gemini_key = st.sidebar.text_input("Gemini API Key", type="password")
sarvam_key = st.sidebar.text_input("Sarvam API Key", type="password")

col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Input Context")
    img_file = st.file_uploader("📸 Upload Problem Screenshot", type=["png", "jpg", "jpeg"])
    target_language = st.selectbox("💻 Target Programming Language", ["C++", "Python", "Java", "JavaScript", "C"])
    
    st.write("🗣️ **Click the mic to speak your command (Marathi/Hinglish):**")
    audio_bytes = audio_recorder(text="", icon_size="2x")
    
    if audio_bytes:
        st.audio(audio_bytes, format="audio/wav")
        
    generate_btn = st.button("Generate Code 🧠", use_container_width=True)

with col2:
    st.subheader("2. Agent Output")
    if generate_btn:
        if not gemini_key or not sarvam_key:
            st.error("⚠️ Please paste both API keys in the sidebar.")
        elif not img_file:
            st.error("⚠️ Please upload a screenshot of the problem.")
        elif not audio_bytes:
            st.error("⚠️ Please record a voice command first.")
        else:
            try:
                sarvam_client = SarvamAI(api_subscription_key=sarvam_key)
                
                # 1. Save browser audio to a temp file for Sarvam
                with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_wav:
                    temp_wav.write(audio_bytes)
                    temp_wav_path = temp_wav.name

                # 2. Sarvam Speech-to-Text Translation
                with st.spinner("🔄 Sarvam is translating your voice..."):
                    with open(temp_wav_path, 'rb') as f:
                        stt_response = sarvam_client.speech_to_text.translate(file=f)
                    user_intent = stt_response.transcript
                    st.info(f"**Translated Command:** {user_intent}")
                
                os.remove(temp_wav_path) # Clean up temp file

                # 3. Gemini Code Generation
                genai.configure(api_key=gemini_key, transport="rest")
                gemini_model = genai.GenerativeModel('gemini-3.8-flash')
                
                img = Image.open(img_file)
                prompt = f"The user asked: '{user_intent}'. Write a highly optimized {target_language} solution based on the screenshot. Output ONLY raw {target_language} code. No markdown."
                
                with st.spinner(f"🧠 Gemini is analyzing and writing {target_language}..."):
                    response = gemini_model.generate_content([prompt, img])
                    clean_code = response.text.replace('```cpp', '').replace('```python', '').replace('```java', '').replace('```', '').strip()
                    highlight_lang = "cpp" if target_language == "C++" else target_language.lower()
                    st.code(clean_code, language=highlight_lang)
                
                # 4. Sarvam Text-to-Speech Confirmation
                with st.spinner("🔊 Generating Sarvam audio..."):
                    tts_response = sarvam_client.text_to_speech.convert(
                        text=f"Bhai, {target_language} solution ready hai. Code screen par aa gaya hai.",
                        target_language_code="hi-IN"
                    )
                    st.audio(tts_response.audio, format="audio/wav")
                    st.success("✅ Execution Complete!")
                    
            except Exception as e:
                st.error(f"Network/API Error: {e}")