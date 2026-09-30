import streamlit as st
from huggingface_hub import InferenceClient
import PyPDF2
from gtts import gTTS
import io, tempfile, os

# ═══════════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════════
HF_TOKEN = st.secrets["HF_TOKEN"]
client = InferenceClient(token=HF_TOKEN)

CHAT_MODEL = "meta-llama/Llama-3.3-70B-Instruct"
WHISPER_MODEL = "openai/whisper-large-v3"

st.set_page_config(
    page_title="MYRAA",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ═══════════════════════════════════════════
# PREMIUM CSS — ChatGPT + Gemini + DeepSeek Style
# ═══════════════════════════════════════════
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

    /* ═══ GLOBAL ═══ */
    * { font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; }
    html, body, [class*="css"] { color-scheme: dark; }
    
    .stApp {
        background: #212121;
        color: #ececec;
    }
    
    #MainMenu, footer, header { visibility: hidden; }
    .block-container { padding-top: 1rem !important; max-width: 900px; }

    /* ═══ SIDEBAR — ChatGPT style ═══ */
    [data-testid="stSidebar"] {
        background: #171717;
        border-right: 1px solid #2a2a2a;
        min-width: 260px !important;
    }
    
    [data-testid="stSidebar"] > div:first-child {
        padding-top: 1rem;
    }
    
    [data-testid="stSidebar"] * {
        color: #d4d4d8;
        font-size: 0.85rem;
    }

    /* Sidebar headers */
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3 {
        font-family: 'JetBrains Mono', monospace;
        color: #9a9a9a;
        font-size: 0.7rem;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        font-weight: 500;
        margin: 1rem 0 0.5rem 0;
    }

    /* ═══ LOGO ═══ */
    .brand {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 0 0 1rem 0;
        margin-bottom: 0.5rem;
        border-bottom: 1px solid #2a2a2a;
    }
    
    .brand-icon {
        width: 28px; height: 28px;
        background: linear-gradient(135deg, #4a9eff 0%, #7c5cff 100%);
        border-radius: 7px;
        display: flex; align-items: center; justify-content: center;
        font-size: 14px; font-weight: 700;
        color: #fff;
    }
    
    .brand-text {
        font-size: 1rem;
        font-weight: 600;
        letter-spacing: 2px;
        color: #ececec;
    }
    
    .brand-text span { color: #4a9eff; }

    /* ═══ MAIN HEADER ═══ */
    .hero {
        text-align: center;
        padding: 2rem 0 1rem 0;
    }
    
    .hero h1 {
        font-size: 2rem;
        font-weight: 600;
        margin: 0;
        background: linear-gradient(135deg, #ececec 0%, #4a9eff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -0.5px;
    }
    
    .hero p {
        color: #8e8e8e;
        font-size: 0.85rem;
        margin-top: 6px;
    }

    /* ═══ CHAT MESSAGES ═══ */
    .msg-row {
        display: flex;
        gap: 14px;
        padding: 16px 0;
        animation: fadeIn 0.3s ease;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(6px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .avatar {
        width: 32px; height: 32px;
        border-radius: 6px;
        flex-shrink: 0;
        display: flex; align-items: center; justify-content: center;
        font-size: 13px; font-weight: 700;
        color: #fff;
    }
    
    .avatar-user {
        background: #4a9eff;
    }
    
    .avatar-ai {
        background: linear-gradient(135deg, #4a9eff 0%, #7c5cff 100%);
    }
    
    .bubble {
        flex: 1;
        padding: 4px 0;
        color: #ececec;
        font-size: 0.95rem;
        line-height: 1.7;
        word-wrap: break-word;
    }
    
    .bubble-user {
        color: #ececec;
    }
    
    .bubble-ai {
        color: #d4d4d8;
    }
    
    .role-name {
        font-size: 0.8rem;
        font-weight: 600;
        color: #8e8e8e;
        margin-bottom: 4px;
    }

    /* ═══ SIDEBAR BUTTONS ═══ */
    .stButton > button {
        background: #212121;
        color: #ececec;
        border: 1px solid #2a2a2a;
        border-radius: 8px;
        font-weight: 500;
        width: 100%;
        font-size: 0.85rem;
        padding: 10px 14px;
        text-align: left;
        transition: all 0.15s ease;
    }
    
    .stButton > button:hover {
        background: #2a2a2a;
        border-color: #3a3a3a;
    }

    /* ═══ SELECTBOX / SLIDER ═══ */
    .stSelectbox > div > div,
    .stSlider > div > div > div {
        background: #212121 !important;
        border-color: #2a2a2a !important;
        color: #ececec !important;
    }
    
    [data-testid="stSelectbox"] > div > div {
        background: #212121;
        border: 1px solid #2a2a2a;
        border-radius: 8px;
    }
    
    /* ═══ CHAT INPUT — ChatGPT style ═══ */
    .stChatInput {
        border-top: 1px solid #2a2a2a;
        background: #212121;
        padding-top: 12px;
    }
    
    .stChatInput textarea {
        background: #2f2f2f !important;
        border: 1px solid #3a3a3a !important;
        color: #ececec !important;
        border-radius: 24px !important;
        font-size: 0.95rem !important;
        padding: 14px 20px !important;
        box-shadow: none !important;
        transition: border-color 0.15s ease;
    }
    
    .stChatInput textarea:focus {
        border-color: #4a9eff !important;
        box-shadow: 0 0 0 3px rgba(74, 158, 255, 0.15) !important;
    }
    
    .stChatInput textarea::placeholder {
        color: #6b6b6b !important;
    }

    /* ═══ FILE UPLOADER ═══ */
    [data-testid="stFileUploader"] {
        border: 1px dashed #3a3a3a;
        border-radius: 10px;
        padding: 12px;
        background: #1a1a1a;
    }
    
    [data-testid="stFileUploader"]:hover {
        border-color: #4a9eff;
        background: #1f1f1f;
    }
    
    [data-testid="stFileUploader"] section {
        background: transparent !important;
        border: none !important;
    }

    /* ═══ AUDIO INPUT ═══ */
    [data-testid="stAudioInput"] {
        background: #1a1a1a;
        border-radius: 10px;
        padding: 8px;
    }
    
    [data-testid="stAudioInput"] button {
        background: #4a9eff !important;
        border-radius: 50% !important;
    }

    /* ═══ ALERTS ═══ */
    .stAlert {
        background: #1a1a1a !important;
        border: 1px solid #2a2a2a !important;
        border-radius: 8px !important;
        color: #a1a1aa !important;
        font-size: 0.8rem;
    }

    /* ═══ SPINNER ═══ */
    .stSpinner > div {
        border-color: #4a9eff transparent transparent transparent !important;
    }

    /* ═══ SCROLLBAR ═══ */
    ::-webkit-scrollbar { width: 8px; height: 8px; }
    ::-webkit-scrollbar-track { background: #171717; }
    ::-webkit-scrollbar-thumb { background: #3a3a3a; border-radius: 4px; }
    ::-webkit-scrollbar-thumb:hover { background: #4a9eff; }

    /* ═══ DIVIDER ═══ */
    hr { border-color: #2a2a2a !important; margin: 14px 0 !important; }
    
    /* ═══ LABEL TEXT ═══ */
    .stSlider label, .stSelectbox label, .stCheckbox label {
        color: #a1a1aa !important;
        font-size: 0.8rem !important;
    }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════
# SESSION STATE
# ═══════════════════════════════════════════
if "messages" not in st.session_state:
    st.session_state.messages = []
if "pdf_text" not in st.session_state:
    st.session_state.pdf_text = ""
if "voice_output" not in st.session_state:
    st.session_state.voice_output = False
if "pending_input" not in st.session_state:
    st.session_state.pending_input = ""

# ═══════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════
with st.sidebar:
    # Logo
    st.markdown("""
    <div class="brand">
        <div class="brand-icon">M</div>
        <div class="brand-text">MYR<span>AA</span></div>
    </div>
    """, unsafe_allow_html=True)
    
    # New Chat
    if st.button("＋  New chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.pdf_text = ""
        st.rerun()
    
    st.markdown("---")
    
    # Settings
    st.markdown("### ⚙ Settings")
    
    voice_out = st.toggle("🔊 Voice Output", value=st.session_state.voice_output, key="voice_toggle")
    st.session_state.voice_output = voice_out
    
    st.markdown("### 📄 Document")
    
    pdf_file = st.file_uploader("Upload PDF", type=["pdf"], label_visibility="collapsed")
    if pdf_file:
        try:
            reader = PyPDF2.PdfReader(pdf_file)
            text = "".join([p.extract_text() for p in reader.pages if p.extract_text()])
            st.session_state.pdf_text = text[:6000]
            st.success(f"✓ PDF loaded ({len(text)} chars)")
        except Exception as e:
            st.error(f"Error: {e}")
    elif st.session_state.pdf_text:
        st.info("✓ PDF in memory")
    
    st.markdown("---")
    
    # Memory info
    st.markdown(f"### 🧠 Memory")
    st.caption(f"{len(st.session_state.messages)} messages stored")
    
    if st.button("🗑  Clear memory", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ═══════════════════════════════════════════
# MAIN HEADER
# ═══════════════════════════════════════════
if not st.session_state.messages:
    st.markdown("""
    <div class="hero">
        <h1>How can I help you today?</h1>
        <p>Ask anything, upload a PDF, or use voice</p>
    </div>
    """, unsafe_allow_html=True)

# ═══════════════════════════════════════════
# CHAT DISPLAY
# ═══════════════════════════════════════════
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"""
        <div class="msg-row">
            <div class="avatar avatar-user">Y</div>
            <div class="bubble bubble-user">
                <div class="role-name">You</div>
                {msg["content"]}
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="msg-row">
            <div class="avatar avatar-ai">M</div>
            <div class="bubble bubble-ai">
                <div class="role-name">MYRAA</div>
                {msg["content"]}
            </div>
        </div>
        """, unsafe_allow_html=True)

# ═══════════════════════════════════════════
# VOICE INPUT
# ═══════════════════════════════════════════
with st.expander("🎙  Voice input", expanded=False):
    audio_value = st.audio_input("Record your message")
    if audio_value is not None:
        with st.spinner("Transcribing..."):
            try:
                # Save audio to temp file
                with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
                    tmp.write(audio_value.getvalue())
                    tmp_path = tmp.name
                
                # Transcribe using Whisper
                result = client.automatic_speech_recognition(
                    audio_value.getvalue(),
                    model=WHISPER_MODEL
                )
                transcribed = result.text if hasattr(result, 'text') else str(result)
                
                if transcribed.strip():
                    st.session_state.pending_input = transcribed
                    st.success(f"✓ Heard: {transcribed}")
                    st.rerun()
                else:
                    st.warning("Could not hear anything. Try again.")
                    
                os.unlink(tmp_path)
            except Exception as e:
                st.error(f"Voice error: {e}")

# ═══════════════════════════════════════════
# CHAT INPUT + PROCESSING
# ═══════════════════════════════════════════
prompt = st.chat_input("Message MYRAA...")

# Use pending input from voice if available
if st.session_state.pending_input and not prompt:
    prompt = st.session_state.pending_input
    st.session_state.pending_input = ""

if prompt:
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.rerun()

# Process last message if it's from user
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    user_msg = st.session_state.messages[-1]["content"]
    
    # System prompt — Gujlish
    system = """You are MYRAA — a highly intelligent, calm, and premium AI assistant. You have a sci-fi, sophisticated vibe similar to ChatGPT, Gemini, and DeepSeek.

LANGUAGE RULES — GUJLISH (English + Gujarati words in Roman script):
1. ALWAYS reply in ENGLISH by default.
2. Naturally mix in GUJARATI words (Roman script). Examples:
   - "Kem cho boss!"
   - "Haan bhai, that's correct."
   - "Saras! Let me handle that."
   - "Ek minute, hu check karu..."
   - "Bau saru question che!"
   - "Chalo, let's do it."
3. NEVER use Hindi or Devanagari script. Only English + Gujarati.
4. If user writes in Gujarati, reply in Gujlish.
5. If user writes in English, reply in English with light Gujarati touch.
6. Only reply fully in Gujarati if user explicitly says "reply in Gujarati".
7. Never say you're an AI language model — you are MYRAA.
8. Address user as "boss" or "bhai" occasionally.
9. Be warm, sharp, and helpful. Keep responses clean and well-formatted.

PERSONALITY:
- Calm, confident, modern
- Friendly but professional
- Clear and concise
- Occasionally witty
"""
    if st.session_state.pdf_text:
        system += f"\n\nPDF CONTEXT (reference this when relevant):\n{st.session_state.pdf_text}"
    
    messages = [{"role": "system", "content": system}] + st.session_state.messages
    
    with st.spinner("MYRAA is thinking..."):
        try:
            response = client.chat_completion(
                model=CHAT_MODEL,
                messages=messages,
                max_tokens=1200,
                temperature=0.7
            )
            reply = response.choices[0].message.content
        except Exception as e:
            reply = f"⚠️ Error: {str(e)}"
    
    st.session_state.messages.append({"role": "assistant", "content": reply})
    
    # Voice output if enabled
    if st.session_state.voice_output:
        try:
            # Clean text for TTS (remove markdown)
            clean_reply = reply.replace("*", "").replace("#", "").replace("`", "")
            tts = gTTS(text=clean_reply[:500], lang='en', tld='co.in', slow=False)
            audio_buffer = io.BytesIO()
            tts.write_to_fp(audio_buffer)
            audio_buffer.seek(0)
            st.audio(audio_buffer, format="audio/mp3", autoplay=True)
        except Exception as e:
            st.warning(f"Voice output error: {e}")
    
    st.rerun()
