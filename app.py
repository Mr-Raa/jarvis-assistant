import streamlit as st
from huggingface_hub import InferenceClient
import PyPDF2
from gTTS import gTTS
import io, tempfile, os

# ═══════════════════════════════════════
HF_TOKEN = st.secrets["HF_TOKEN"]
client = InferenceClient(token=HF_TOKEN)
CHAT_MODEL = "meta-llama/Llama-3.3-70B-Instruct"

st.set_page_config(page_title="MYRAA", page_icon="🔵", layout="wide", initial_sidebar_state="collapsed")

# ═══════════════════════════════════════
# JARVIS CSS — IRON MAN STYLE
# ═══════════════════════════════════════
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;700;900&family=Rajdhani:wght@300;400;500;600;700&display=swap');

    /* ═══ GLOBAL ═══ */
    * { font-family: 'Rajdhani', sans-serif; }
    
    .stApp {
        background: #000508;
        background-image: 
            radial-gradient(circle at 20% 10%, #001a3a 0%, transparent 40%),
            radial-gradient(circle at 80% 90%, #001030 0%, transparent 40%),
            linear-gradient(rgba(0, 212, 255, 0.04) 1px, transparent 1px),
            linear-gradient(90deg, rgba(0, 212, 255, 0.04) 1px, transparent 1px);
        background-size: 100% 100%, 100% 100%, 50px 50px, 50px 50px;
        color: #a8e8ff;
        overflow-x: hidden;
    }
    
    #MainMenu, footer, header { visibility: hidden; }
    .block-container { padding: 0 !important; max-width: 100% !important; }

    /* ═══ SCAN LINE ═══ */
    .scan-line {
        position: fixed;
        top: 0; left: 0; right: 0;
        height: 2px;
        background: linear-gradient(90deg, transparent, #00d4ff, #00ffea, #00d4ff, transparent);
        box-shadow: 0 0 20px #00d4ff, 0 0 40px #00d4ff;
        animation: scanDown 6s linear infinite;
        z-index: 9999;
        pointer-events: none;
    }
    @keyframes scanDown {
        0% { top: 0; opacity: 0; }
        10% { opacity: 1; }
        90% { opacity: 1; }
        100% { top: 100vh; opacity: 0; }
    }

    /* ═══ HUD CORNERS ═══ */
    .hud-corner {
        position: fixed;
        width: 60px; height: 60px;
        border-color: #00d4ff;
        z-index: 999;
        pointer-events: none;
        opacity: 0.7;
    }
    .hud-tl { top: 20px; left: 20px; border-top: 2px solid; border-left: 2px solid; }
    .hud-tr { top: 20px; right: 20px; border-top: 2px solid; border-right: 2px solid; }
    .hud-bl { bottom: 20px; left: 20px; border-bottom: 2px solid; border-left: 2px solid; }
    .hud-br { bottom: 20px; right: 20px; border-bottom: 2px solid; border-right: 2px solid; }

    /* ═══ TOP BAR ═══ */
    .top-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 18px 40px;
        border-bottom: 1px solid rgba(0, 212, 255, 0.2);
        background: linear-gradient(180deg, rgba(0, 20, 40, 0.6) 0%, transparent 100%);
        backdrop-filter: blur(10px);
    }
    
    .top-left {
        display: flex;
        align-items: center;
        gap: 14px;
    }
    
    .reactor-mini {
        width: 40px; height: 40px;
        border-radius: 50%;
        background: radial-gradient(circle, #ffffff 0%, #00ffea 25%, #00d4ff 50%, #0066cc 75%, transparent 100%);
        box-shadow: 
            0 0 20px #00d4ff,
            0 0 40px #00d4ff80,
            inset 0 0 15px #ffffff;
        animation: reactorPulse 2s ease-in-out infinite;
        position: relative;
    }
    .reactor-mini::before {
        content: '';
        position: absolute;
        inset: 8px;
        border-radius: 50%;
        border: 2px solid #ffffff;
        animation: reactorSpin 4s linear infinite;
    }
    @keyframes reactorPulse {
        0%, 100% { box-shadow: 0 0 20px #00d4ff, 0 0 40px #00d4ff80, inset 0 0 15px #ffffff; }
        50% { box-shadow: 0 0 30px #00ffea, 0 0 60px #00ffea, inset 0 0 25px #ffffff; }
    }
    @keyframes reactorSpin {
        to { transform: rotate(360deg); }
    }
    
    .top-title {
        font-family: 'Orbitron', sans-serif;
        font-size: 1.4rem;
        font-weight: 700;
        color: #00d4ff;
        letter-spacing: 8px;
        text-shadow: 0 0 15px #00d4ff, 0 0 30px #00d4ff80;
    }
    
    .top-title span { color: #00ffea; }
    
    .status-pill {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 6px 14px;
        border: 1px solid #00d4ff60;
        border-radius: 20px;
        background: rgba(0, 212, 255, 0.08);
        font-family: 'Orbitron', sans-serif;
        font-size: 0.7rem;
        color: #00ffea;
        letter-spacing: 2px;
        text-transform: uppercase;
    }
    
    .status-dot {
        width: 8px; height: 8px;
        background: #00ff88;
        border-radius: 50%;
        box-shadow: 0 0 10px #00ff88;
        animation: blink 1.5s ease-in-out infinite;
    }
    @keyframes blink {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.3; }
    }

    /* ═══ HERO / ARC REACTOR ═══ */
    .hero-area {
        text-align: center;
        padding: 40px 0 20px 0;
        position: relative;
    }
    
    .arc-reactor {
        width: 180px;
        height: 180px;
        margin: 0 auto;
        position: relative;
    }
    
    .arc-reactor .ring {
        position: absolute;
        inset: 0;
        border-radius: 50%;
        border: 2px solid transparent;
    }
    
    .arc-reactor .ring-1 {
        border-top-color: #00d4ff;
        border-right-color: #00d4ff;
        animation: spin 3s linear infinite;
        box-shadow: 0 0 20px #00d4ff;
    }
    
    .arc-reactor .ring-2 {
        inset: 15px;
        border-bottom-color: #00ffea;
        border-left-color: #00ffea;
        animation: spin 4s linear infinite reverse;
        box-shadow: 0 0 15px #00ffea;
    }
    
    .arc-reactor .ring-3 {
        inset: 30px;
        border-top-color: #ffffff;
        border-right-color: #00d4ff;
        animation: spin 2s linear infinite;
        box-shadow: 0 0 10px #ffffff;
    }
    
    .arc-reactor .core {
        position: absolute;
        inset: 50px;
        border-radius: 50%;
        background: radial-gradient(circle, #ffffff 0%, #00ffea 30%, #00d4ff 60%, transparent 100%);
        box-shadow: 
            0 0 30px #00d4ff,
            0 0 60px #00d4ff,
            0 0 100px #00d4ff80,
            inset 0 0 20px #ffffff;
        animation: corePulse 2s ease-in-out infinite;
    }
    
    @keyframes spin {
        to { transform: rotate(360deg); }
    }
    
    @keyframes corePulse {
        0%, 100% { transform: scale(1); box-shadow: 0 0 30px #00d4ff, 0 0 60px #00d4ff, 0 0 100px #00d4ff80, inset 0 0 20px #ffffff; }
        50% { transform: scale(1.08); box-shadow: 0 0 40px #00ffea, 0 0 80px #00ffea, 0 0 140px #00ffea80, inset 0 0 30px #ffffff; }
    }
    
    .hero-text {
        font-family: 'Orbitron', sans-serif;
        font-size: 2.4rem;
        font-weight: 900;
        color: #ffffff;
        letter-spacing: 15px;
        margin-top: 30px;
        text-shadow: 
            0 0 10px #00d4ff,
            0 0 30px #00d4ff,
            0 0 60px #00d4ff;
    }
    
    .hero-sub {
        font-family: 'Rajdhani', sans-serif;
        color: #5ca8d8;
        font-size: 0.9rem;
        letter-spacing: 6px;
        text-transform: uppercase;
        margin-top: 8px;
    }

    /* ═══ CHAT AREA ═══ */
    .chat-container {
        max-width: 900px;
        margin: 0 auto;
        padding: 20px 30px 120px 30px;
    }
    
    .msg-row {
        display: flex;
        gap: 16px;
        padding: 14px 0;
        animation: msgIn 0.4s cubic-bezier(0.16, 1, 0.3, 1);
    }
    
    @keyframes msgIn {
        from { opacity: 0; transform: translateY(15px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .msg-avatar {
        width: 40px; height: 40px;
        border-radius: 50%;
        flex-shrink: 0;
        display: flex;
        align-items: center;
        justify-content: center;
        font-family: 'Orbitron', sans-serif;
        font-size: 14px;
        font-weight: 700;
        border: 2px solid;
    }
    
    .msg-avatar-user {
        background: rgba(0, 212, 255, 0.1);
        border-color: #00d4ff;
        color: #00d4ff;
        box-shadow: 0 0 20px #00d4ff60;
    }
    
    .msg-avatar-ai {
        background: radial-gradient(circle, #00ffea20 0%, #00d4ff10 100%);
        border-color: #00ffea;
        color: #00ffea;
        box-shadow: 0 0 20px #00ffea80;
        animation: aiPulse 2s ease-in-out infinite;
    }
    
    @keyframes aiPulse {
        0%, 100% { box-shadow: 0 0 20px #00ffea80; }
        50% { box-shadow: 0 0 35px #00ffea, 0 0 60px #00ffea60; }
    }
    
    .msg-content {
        flex: 1;
        padding-top: 4px;
    }
    
    .msg-name {
        font-family: 'Orbitron', sans-serif;
        font-size: 0.75rem;
        letter-spacing: 3px;
        color: #5ca8d8;
        text-transform: uppercase;
        margin-bottom: 6px;
    }
    
    .msg-name-ai {
        color: #00ffea;
        text-shadow: 0 0 8px #00ffea60;
    }
    
    .msg-text {
        background: rgba(0, 30, 50, 0.4);
        border: 1px solid rgba(0, 212, 255, 0.25);
        border-left: 3px solid #00d4ff;
        border-radius: 12px;
        padding: 14px 20px;
        color: #d0eaff;
        font-size: 1rem;
        line-height: 1.7;
        box-shadow: inset 0 0 20px rgba(0, 212, 255, 0.05);
    }
    
    .msg-user .msg-text {
        border-left-color: #00d4ff;
        background: rgba(0, 40, 70, 0.5);
    }
    
    .msg-ai .msg-text {
        border-left-color: #00ffea;
        background: rgba(0, 30, 50, 0.5);
        box-shadow: inset 0 0 20px rgba(0, 255, 234, 0.05);
    }

    /* ═══ CHAT INPUT ═══ */
    .stChatInput {
        position: fixed !important;
        bottom: 0;
        left: 0;
        right: 0;
        background: linear-gradient(0deg, #000508 60%, transparent 100%);
        padding: 20px 40px 25px 40px;
        z-index: 100;
    }
    
    .stChatInput textarea {
        background: rgba(0, 30, 50, 0.7) !important;
        border: 2px solid #00d4ff !important;
        color: #a8e8ff !important;
        border-radius: 30px !important;
        font-family: 'Rajdhani', sans-serif !important;
        font-size: 1rem !important;
        padding: 16px 24px !important;
        box-shadow: 
            0 0 25px rgba(0, 212, 255, 0.3),
            inset 0 0 20px rgba(0, 212, 255, 0.05) !important;
        backdrop-filter: blur(10px);
    }
    
    .stChatInput textarea:focus {
        border-color: #00ffea !important;
        box-shadow: 
            0 0 40px #00ffea80,
            0 0 80px #00d4ff40,
            inset 0 0 25px rgba(0, 255, 234, 0.1) !important;
    }
    
    .stChatInput textarea::placeholder {
        color: #3a7a9a !important;
        letter-spacing: 2px;
    }

    /* ═══ SIDEBAR ═══ */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #000a12 0%, #000508 100%);
        border-right: 1px solid rgba(0, 212, 255, 0.3);
    }
    
    [data-testid="stSidebar"] * {
        color: #8ac8e8;
        font-family: 'Rajdhani', sans-serif;
    }
    
    [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        font-family: 'Orbitron', sans-serif;
        color: #00d4ff !important;
        font-size: 0.75rem !important;
        letter-spacing: 3px;
        text-transform: uppercase;
        text-shadow: 0 0 10px #00d4ff60;
    }

    /* ═══ BUTTONS ═══ */
    .stButton > button {
        background: rgba(0, 212, 255, 0.08);
        color: #00d4ff;
        border: 1px solid #00d4ff;
        border-radius: 8px;
        font-family: 'Orbitron', sans-serif;
        font-size: 0.7rem;
        letter-spacing: 2px;
        font-weight: 500;
        text-transform: uppercase;
        padding: 10px 16px;
        width: 100%;
        transition: all 0.2s ease;
        box-shadow: inset 0 0 10px rgba(0, 212, 255, 0.1);
    }
    
    .stButton > button:hover {
        background: rgba(0, 212, 255, 0.2);
        box-shadow: 
            0 0 20px #00d4ff80,
            inset 0 0 15px rgba(0, 212, 255, 0.2);
        color: #00ffea;
        border-color: #00ffea;
    }

    /* ═══ FILE UPLOADER ═══ */
    [data-testid="stFileUploader"] {
        border: 2px dashed rgba(0, 212, 255, 0.4);
        border-radius: 10px;
        padding: 12px;
        background: rgba(0, 30, 50, 0.3);
    }
    
    [data-testid="stFileUploader"]:hover {
        border-color: #00ffea;
        box-shadow: 0 0 20px #00ffea40;
    }

    /* ═══ TOGGLE ═══ */
    .stCheckbox label, .stToggle label {
        color: #8ac8e8 !important;
        font-family: 'Rajdhani', sans-serif !important;
        font-size: 0.85rem !important;
    }

    /* ═══ SCROLLBAR ═══ */
    ::-webkit-scrollbar { width: 8px; height: 8px; }
    ::-webkit-scrollbar-track { background: #000508; }
    ::-webkit-scrollbar-thumb { 
        background: linear-gradient(#00d4ff, #0066cc);
        border-radius: 4px;
        box-shadow: 0 0 10px #00d4ff;
    }

    /* ═══ ALERT ═══ */
    .stAlert {
        background: rgba(0, 30, 50, 0.6) !important;
        border: 1px solid #00d4ff60 !important;
        color: #8ac8e8 !important;
        border-radius: 8px !important;
    }

    /* ═══ SPINNER ═══ */
    .stSpinner > div {
        border-color: #00d4ff transparent transparent transparent !important;
    }

    /* ═══ EXPANDER ═══ */
    .streamlit-expanderHeader {
        font-family: 'Orbitron', sans-serif !important;
        color: #00d4ff !important;
        font-size: 0.75rem !important;
        letter-spacing: 2px;
        text-transform: uppercase;
    }

    /* ═══ DATA READOUT (bottom-left corner) ═══ */
    .data-readout {
        position: fixed;
        bottom: 30px;
        left: 30px;
        font-family: 'Orbitron', monospace;
        font-size: 0.65rem;
        color: #00d4ff;
        letter-spacing: 2px;
        opacity: 0.5;
        pointer-events: none;
        z-index: 50;
    }
</style>

<!-- HUD Overlays -->
<div class="scan-line"></div>
<div class="hud-corner hud-tl"></div>
<div class="hud-corner hud-tr"></div>
<div class="hud-corner hud-bl"></div>
<div class="hud-corner hud-br"></div>
<div class="data-readout">
    SYS.ONLINE // v2.0 // NEURAL.LINK.ACTIVE
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════
# SESSION STATE
# ═══════════════════════════════════════
if "messages" not in st.session_state:
    st.session_state.messages = []
if "pdf_text" not in st.session_state:
    st.session_state.pdf_text = ""
if "voice_output" not in st.session_state:
    st.session_state.voice_output = False
if "pending_input" not in st.session_state:
    st.session_state.pending_input = ""

# ═══════════════════════════════════════
# TOP BAR
# ═══════════════════════════════════════
st.markdown("""
<div class="top-bar">
    <div class="top-left">
        <div class="reactor-mini"></div>
        <div class="top-title">MYR<span>AA</span></div>
    </div>
    <div class="status-pill">
        <span class="status-dot"></span>
        SYSTEM ONLINE
    </div>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════
with st.sidebar:
    st.markdown("### ◆ CONTROLS")
    
    if st.button("＋ NEW SESSION", use_container_width=True):
        st.session_state.messages = []
        st.session_state.pdf_text = ""
        st.rerun()
    
    st.markdown("---")
    st.markdown("### ⚡ VOICE")
    voice_out = st.toggle("🔊 AUDIO OUTPUT", value=st.session_state.voice_output)
    st.session_state.voice_output = voice_out
    
    st.markdown("---")
    st.markdown("### 📄 DATA FEED")
    pdf_file = st.file_uploader("Upload PDF", type=["pdf"], label_visibility="collapsed")
    if pdf_file:
        try:
            reader = PyPDF2.PdfReader(pdf_file)
            text = "".join([p.extract_text() for p in reader.pages if p.extract_text()])
            st.session_state.pdf_text = text[:6000]
            st.success(f"✓ Data loaded ({len(text)} chars)")
        except Exception as e:
            st.error(f"Error: {e}")
    
    st.markdown("---")
    st.markdown("### 🧠 MEMORY CORE")
    st.caption(f"{len(st.session_state.messages)} records stored")
    
    if st.button("🗑 PURGE MEMORY", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ═══════════════════════════════════════
# HERO (Arc Reactor) — only when no messages
# ═══════════════════════════════════════
if not st.session_state.messages:
    st.markdown("""
    <div class="hero-area">
        <div class="arc-reactor">
            <div class="ring ring-1"></div>
            <div class="ring ring-2"></div>
            <div class="ring ring-3"></div>
            <div class="core"></div>
        </div>
        <div class="hero-text">MYRAA</div>
        <div class="hero-sub">◉ Awaiting your command ◉</div>
    </div>
    """, unsafe_allow_html=True)

# ═══════════════════════════════════════
# CHAT DISPLAY
# ═══════════════════════════════════════
st.markdown('<div class="chat-container">', unsafe_allow_html=True)

for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"""
        <div class="msg-row msg-user">
            <div class="msg-avatar msg-avatar-user">Y</div>
            <div class="msg-content">
                <div class="msg-name">USER</div>
                <div class="msg-text">{msg["content"]}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="msg-row msg-ai">
            <div class="msg-avatar msg-avatar-ai">M</div>
            <div class="msg-content">
                <div class="msg-name msg-name-ai">MYRAA</div>
                <div class="msg-text">{msg["content"]}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════
# VOICE INPUT
# ═══════════════════════════════════════
with st.sidebar:
    st.markdown("---")
    st.markdown("### 🎙 VOICE INPUT")
    audio_value = st.audio_input("Record", label_visibility="collapsed")
    if audio_value is not None:
        with st.spinner("TRANSCRIBING..."):
            try:
                result = client.automatic_speech_recognition(
                    audio_value.getvalue(),
                    model="openai/whisper-large-v3"
                )
                transcribed = result.text if hasattr(result, 'text') else str(result)
                if transcribed.strip():
                    st.session_state.pending_input = transcribed
                    st.rerun()
            except Exception as e:
                st.error(f"Voice error: {e}")

# ═══════════════════════════════════════
# CHAT INPUT
# ═══════════════════════════════════════
prompt = st.chat_input("◉ Command MYRAA...")

if st.session_state.pending_input and not prompt:
    prompt = st.session_state.pending_input
    st.session_state.pending_input = ""

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.rerun()

# ═══════════════════════════════════════
# AI RESPONSE
# ═══════════════════════════════════════
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    system = """You are MYRAA — an advanced AI assistant modeled after JARVIS from Iron Man. You are calm, brilliant, loyal, and slightly witty.

LANGUAGE RULES — GUJLISH (English + Gujarati words in Roman script):
1. ALWAYS reply in ENGLISH by default.
2. Naturally mix in GUJARATI words in Roman script:
   - "Kem cho boss!"
   - "Haan bhai, samjyo."
   - "Saras! Let me handle that."
   - "Ek minute, hu check karu chhu..."
   - "Bau saru question che!"
   - "Chalo, let's do it."
3. NEVER use Hindi or Devanagari.
4. If user writes Gujarati, reply in Gujlish.
5. If user writes English, reply in English with light Gujarati touch.
6. Only reply fully in Gujarati if user says "reply in Gujarati".
7. Never say you're an AI language model — you are MYRAA.
8. Address user as "boss" or "bhai" occasionally.
9. Keep answers sharp, helpful, and well-formatted.
10. Occasionally reference systems, protocols, or "scanning" for JARVIS feel.

PERSONALITY:
- Calm, confident, sophisticated
- Loyal like JARVIS
- Warm but professional
- Brief and clear
"""
    if st.session_state.pdf_text:
        system += f"\n\nDOCUMENT CONTEXT:\n{st.session_state.pdf_text}"
    
    messages = [{"role": "system", "content": system}] + st.session_state.messages
    
    with st.spinner("◉ PROCESSING..."):
        try:
            response = client.chat_completion(
                model=CHAT_MODEL,
                messages=messages,
                max_tokens=1200,
                temperature=0.7
            )
            reply = response.choices[0].message.content
        except Exception as e:
            reply = f"⚠️ ERROR: {str(e)}"
    
    st.session_state.messages.append({"role": "assistant", "content": reply})
    
    if st.session_state.voice_output:
        try:
            clean = reply.replace("*", "").replace("#", "").replace("`", "").replace("_", "")
            tts = gTTS(text=clean[:500], lang='en', tld='co.in', slow=False)
            buf = io.BytesIO()
            tts.write_to_fp(buf)
            buf.seek(0)
            st.audio(buf, format="audio/mp3", autoplay=True)
        except Exception as e:
            st.warning(f"TTS error: {e}")
    
    st.rerun()
