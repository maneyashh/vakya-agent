import streamlit as st
import google.generativeai as genai
from sarvamai import SarvamAI
from PIL import Image
from audio_recorder_streamlit import audio_recorder
import tempfile
import os

# Page Config
st.set_page_config(page_title="Vakya-Agent OS", page_icon="⚡", layout="wide")

# Futuristic Cyberpunk Dark Theme CSS
st.markdown("""
<style>
    .stApp {
        background-color: #0d1117;
        color: #c9d1d9;
    }
    .sidebar .st-v-q {
        background-color: #161b22;
    }
    h1, h2, h3 {
        color: #58a6ff !important;
        font-family: 'Inter', sans-serif;
    }
    .stButton>button {
        background: linear-gradient(90deg, #238636 0%, #2ea043 100%);
        color: white;
        border-radius: 8px;
        font-weight: bold;
        border: none;
        box-shadow: 0 0 15px rgba(46, 160, 67, 0.4);
        transition: 0.3s ease;
    }
    .stButton>button:hover {
        transform: scale(1.02);
        box-shadow: 0 0 25px rgba(46, 160, 67, 0.8);
    }
    .stTextInput>div>div>input, .stSelectbox>div>div>select {
        background-color: #161b22;
        color: #c9d1d9;
        border: 1px solid #30363d;
        border-radius: 6px;
    }
</style>
""", unsafe_allow_html=True)

st.title("⚡ VAKYA-AGENT // Multilingual Neural Code OS")
st.markdown("### *Next-Gen Multimodal Voice-to-Code Pipeline*")

st.sidebar.header("🔐 Neural Link Config")
gemini_key = st.sidebar.text_input("Gemini API Key", type="password")
sarvam_key = st.sidebar.text_input("Sarvam API Key", type="password")

if "history" not in st.session_state:
    st.session_state.history = []

col1, col2 = st.columns(2)

with col1:
    st.subheader("📡 1. Sensor Input & Context")
    
    # Futuristic File Uploader with Paste Support hint
    st.markdown("💡 **Tip:** Take a screenshot and press `Ctrl + V` anywhere on your screen, then upload it below, or drop it directly!")
    img_file = st.file_uploader("📸 Drop Problem Screenshot Here", type=["png", "jpg", "jpeg"])
    
    if img_file:
        preview_img = Image.open(img_file)
        st.image(preview_img, caption="Target Problem Buffer Loaded", use_container_width=True)

    target_language = st.selectbox("💻 Target Core Language", ["C++", "Python", "Java", "JavaScript", "C"])
    instruction_lang = st.selectbox("🗣️ Neural Explanation Dialect", ["Hinglish", "Marathi", "Hindi", "English"])
    
    st.markdown("🎙️ **Acoustic Audio Channel:**")
    audio_bytes = audio_recorder(text="", icon_size="2x")
    
    if audio_bytes:
        st.audio(audio_bytes, format="audio/wav")
        
    generate_btn = st.button("⚡ EXECUTE NEURAL SYNTHESIS", use_container_width=True)

with col2:
    st.subheader("🖥️ 2. Execution Feed & Logic")
    
    if generate_btn:
        if not gemini_key or not sarvam_key:
            st.error("⚠️ Neural keys missing in sidebar configuration.")
        elif not img_file:
            st.error("⚠️ Visual buffer empty. Upload a screenshot.")
        elif not audio_bytes:
            st.error("⚠️ Acoustic stream missing. Record a command.")
        else:
            try:
                sarvam_client = SarvamAI(api_subscription_key=sarvam_key)
                
                with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_wav:
                    temp_wav.write(audio_bytes)
                    temp_wav_path = temp_wav.name

                with st.spinner("🔄 Decoding acoustic signals via Sarvam..."):
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
                
                with st.spinner(f"🧠 Synthesizing {target_language} & {instruction_lang} breakdown..."):
                    response = gemini_model.generate_content([prompt, img])
                    raw_text = response.text
                    
                    try:
                        clean_code = raw_text.split("[CODE]")[1].split("[/CODE]")[0].strip()
                        clean_instructions = raw_text.split("[INSTRUCTIONS]")[1].split("[/INSTRUCTIONS]")[0].strip()
                    except:
                        clean_code = raw_text
                        clean_instructions = "Neural parse complete."

                    st.session_state.history.insert(0, {
                        "intent": user_intent,
                        "code": clean_code,
                        "instructions": clean_instructions,
                        "lang": target_language
                    })
                
                with st.spinner("🔊 Broadcasting acoustic confirmation..."):
                    tts_response = sarvam_client.text_to_speech.convert(
                        text=f"Bhai, {target_language} execution successful.",
                        target_language_code="hi-IN"
                    )
                    st.audio(tts_response.audio, format="audio/wav")
                    
            except Exception as e:
                st.error(f"System Error: {e}")

    # Render History Terminal Feed
    if st.session_state.history:
        for idx, item in enumerate(st.session_state.history):
            with st.container():
                st.markdown(f"🟢 **Command Vector:** `{item['intent']}`")
                highlight_lang = "cpp" if item['lang'] == "C++" else item['lang'].lower()
                st.code(item['code'].replace('```cpp', '').replace('```', ''), language=highlight_lang)
                
                file_ext = "cpp" if item['lang'] == "C++" else ("py" if item['lang'] == "Python" else "txt")
                st.download_button(
                    label=f"📥 Download Payload ({item['lang']})",
                    data=item['code'],
                    file_name=f"vakya_solution.{file_ext}",
                    key=f"download_{idx}"
                )
                
                st.markdown(f"🤖 **Neural Breakdown ({instruction_lang}):**\n\n{item['instructions']}")
                st.markdown("---")