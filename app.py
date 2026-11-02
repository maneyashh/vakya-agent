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

# Initialize session state for history
if "history" not in st.session_state:
    st.session_state.history = []

col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Input Context")
    img_file = st.file_uploader("📸 Upload Problem Screenshot", type=["png", "jpg", "jpeg"])
    
    target_language = st.selectbox("💻 Target Programming Language", ["C++", "Python", "Java", "JavaScript", "C"])
    instruction_lang = st.selectbox("🗣️ Spoken Language (For Explanations)", ["Hinglish", "Marathi", "Hindi", "English"])
    
    st.write("🗣️ **Click the mic to speak your command:**")
    audio_bytes = audio_recorder(text="", icon_size="2x")
    
    if audio_bytes:
        st.audio(audio_bytes, format="audio/wav")
        
    generate_btn = st.button("Generate Code & Instructions 🧠", use_container_width=True)

with col2:
    st.subheader("2. Agent Output & History")
    
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
                
                with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_wav:
                    temp_wav.write(audio_bytes)
                    temp_wav_path = temp_wav.name

                with st.spinner("🔄 Sarvam is translating your voice..."):
                    with open(temp_wav_path, 'rb') as f:
                        stt_response = sarvam_client.speech_to_text.translate(file=f)
                    user_intent = stt_response.transcript
                
                os.remove(temp_wav_path)

                genai.configure(api_key=gemini_key, transport="rest")
                gemini_model = genai.GenerativeModel('gemini-3.8-flash')
                
                img = Image.open(img_file)
                prompt = f"""
                The user asked: '{user_intent}'. 
                Based on the screenshot, write a highly optimized {target_language} solution.
                Also, provide step-by-step instructions on how the logic works in {instruction_lang}.
                
                Format EXACTLY like this:
                [CODE]
                raw code here
                [/CODE]
                [INSTRUCTIONS]
                instructions here
                [/INSTRUCTIONS]
                """
                
                with st.spinner(f"🧠 Gemini is writing {target_language} and {instruction_lang} instructions..."):
                    response = gemini_model.generate_content([prompt, img])
                    raw_text = response.text
                    
                    try:
                        clean_code = raw_text.split("[CODE]")[1].split("[/CODE]")[0].strip()
                        clean_instructions = raw_text.split("[INSTRUCTIONS]")[1].split("[/INSTRUCTIONS]")[0].strip()
                    except:
                        clean_code = raw_text
                        clean_instructions = "Generated successfully."

                    # Save to session history
                    st.session_state.history.insert(0, {
                        "intent": user_intent,
                        "code": clean_code,
                        "instructions": clean_instructions,
                        "lang": target_language
                    })
                
                with st.spinner("🔊 Generating Sarvam audio..."):
                    tts_response = sarvam_client.text_to_speech.convert(
                        text=f"Bhai, {target_language} code ready hai.",
                        target_language_code="hi-IN"
                    )
                    st.audio(tts_response.audio, format="audio/wav")
                    
            except Exception as e:
                st.error(f"Network/API Error: {e}")

    # Render History Feed
    if st.session_state.history:
        for idx, item in enumerate(st.session_state.history):
            with st.container():
                st.info(f"🗣️ **Command:** {item['intent']}")
                highlight_lang = "cpp" if item['lang'] == "C++" else item['lang'].lower()
                st.code(item['code'].replace('```cpp', '').replace('```', ''), language=highlight_lang)
                
                # Download button for each generated code snippet
                file_ext = "cpp" if item['lang'] == "C++" else ("py" if item['lang'] == "Python" else "txt")
                st.download_button(
                    label=f"📥 Download {item['lang']} Code",
                    data=item['code'],
                    file_name=f"solution.{file_ext}",
                    key=f"download_{idx}"
                )
                
                st.success(f"**Instructions:**\n\n{item['instructions']}")
                st.divider()