import streamlit as st
from huggingface_hub import InferenceClient
import PyPDF2

# --- Hugging Face API ---
HF_TOKEN = st.secrets["HF_TOKEN"]
client = InferenceClient(token=HF_TOKEN)
MODEL = "meta-llama/Llama-3.3-70B-Instruct"

# --- Page Config ---
st.set_page_config(page_title="MYRAA", page_icon="🩸", layout="wide")

# --- DARK PSYCHOLOGY THEME CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;700;900&family=Rajdhani:wght@300;400;500;600;700&family=Orbitron:wght@400;700;900&display=swap');
    
    html, body, [class*="css"] { 
        font-family: 'Rajdhani', sans-serif;
        background: #000;
    }
    
    /* === ડાર્ક ગ્રેડિયન્ટ બેકગ્રાઉન્ડ === */
    .stApp {
        background: 
            radial-gradient(ellipse at top left, #1a0000 0%, #000000 50%),
            radial-gradient(ellipse at bottom right, #2a0000 0%, #000000 50%),
            linear-gradient(#8b000015 1px, transparent 1px),
            linear-gradient(90deg, #8b000015 1px, transparent 1px);
        background-size: 100% 100%, 100% 100%, 60px 60px, 60px 60px;
        animation: darkPulse 8s ease-in-out infinite;
    }
    
    @keyframes darkPulse {
        0%, 100% { background-color: #000000; }
        50% { background-color: #0a0000; }
    }
    
    /* === પ્રીમિયમ હેડર - MYRAA === */
    .main-header {
        font-family: 'Cinzel', serif;
        font-size: 4.5rem;
        font-weight: 900;
        background: linear-gradient(135deg, #ff0033 0%, #8b0000 50%, #ffd700 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
        padding: 40px 10px 10px 10px;
        letter-spacing: 18px;
        filter: drop-shadow(0 0 30px #ff003380) drop-shadow(0 0 60px #8b000060);
        animation: headerGlow 4s ease-in-out infinite;
        position: relative;
    }
    
    @keyframes headerGlow {
        0%, 100% { 
            filter: drop-shadow(0 0 30px #ff003380) drop-shadow(0 0 60px #8b000060);
        }
        50% { 
            filter: drop-shadow(0 0 50px #ff0033) drop-shadow(0 0 100px #8b0000) drop-shadow(0 0 30px #ffd70080);
        }
    }
    
    /* === સબટાઇટલ === */
    .subtitle {
        text-align: center;
        color: #ffd700;
        font-family: 'Orbitron', sans-serif;
        font-size: 0.75rem;
        letter-spacing: 10px;
        margin-bottom: 40px;
        text-shadow: 0 0 15px #ffd70080;
        animation: subtleFlicker 3s ease-in-out infinite;
        text-transform: uppercase;
    }
    
    @keyframes subtleFlicker {
        0%, 100% { opacity: 1; }
        45% { opacity: 1; }
        50% { opacity: 0.6; }
        55% { opacity: 1; }
    }
    
    /* === ચેટ બબલ્સ === */
    .chat-user {
        background: linear-gradient(135deg, #8b0000 0%, #1a0000 100%);
        color: #ffd700;
        padding: 18px 24px;
        border-radius: 20px 20px 4px 20px;
        margin: 14px 0;
        max-width: 70%;
        margin-left: auto;
        font-weight: 500;
        font-size: 1.05rem;
        box-shadow: 
            0 0 25px #8b000080,
            0 0 50px #ff003330,
            inset 0 0 15px #ff003320;
        border: 1px solid #8b0000;
        border-right: 3px solid #ff0033;
        animation: slideInRight 0.4s ease-out;
    }
    
    .chat-ai {
        background: linear-gradient(135deg, #0a0000 0%, #150505 100%);
        color: #e8dcd0;
        padding: 18px 24px;
        border-radius: 20px 20px 20px 4px;
        margin: 14px 0;
        max-width: 78%;
        border-left: 3px solid #ffd700;
        box-shadow: 
            0 0 25px #ffd70030,
            inset 0 0 25px #ff003310;
        font-size: 1.05rem;
        line-height: 1.8;
        animation: slideInLeft 0.4s ease-out;
    }
    
    @keyframes slideInRight {
        from { opacity: 0; transform: translateX(40px); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    @keyframes slideInLeft {
        from { opacity: 0; transform: translateX(-40px); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    /* === સાઇડબાર === */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #050000 0%, #0a0000 100%);
        border-right: 1px solid #8b000080;
        box-shadow: 8px 0 40px #8b000030;
    }
    
    [data-testid="stSidebar"] h2 {
        font-family: 'Cinzel', serif;
        color: #ffd700;
        text-shadow: 0 0 15px #ffd70080;
        letter-spacing: 4px;
        font-size: 1rem;
        font-weight: 700;
    }
    
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] label {
        color: #c0a080 !important;
    }
    
    /* === બટન === */
    .stButton > button {
        background: linear-gradient(135deg, #8b0000 0%, #2a0000 100%);
        color: #ffd700;
        border: 1px solid #ff0033;
        border-radius: 10px;
        font-weight: 700;
        width: 100%;
        font-family: 'Orbitron', sans-serif;
        letter-spacing: 3px;
        font-size: 0.8rem;
        padding: 12px;
        box-shadow: 0 0 20px #8b000060;
        transition: all 0.3s ease;
        text-transform: uppercase;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #ff0033 0%, #8b0000 100%);
        box-shadow: 0 0 40px #ff0033, 0 0 80px #8b000080;
        transform: translateY(-2px);
        color: #fff;
        border-color: #ffd700;
    }
    
    /* === ઇનપુટ બોક્સ === */
    .stChatInput textarea {
        background: #0a0000 !important;
        border: 2px solid #8b0000 !important;
        color: #ffd700 !important;
        border-radius: 15px !important;
        font-family: 'Rajdhani', sans-serif;
        font-size: 1.1rem !important;
        padding: 16px 24px !important;
        box-shadow: 
            0 0 25px #8b000060,
            inset 0 0 25px #ff003310 !important;
        transition: all 0.3s ease;
    }
    
    .stChatInput textarea:focus {
        border-color: #ff0033 !important;
        box-shadow: 
            0 0 40px #ff0033,
            inset 0 0 25px #ff003320 !important;
    }
    
    .stChatInput textarea::placeholder {
        color: #8b0000 !important;
        letter-spacing: 2px;
    }
    
    /* === PDF અપલોડ === */
    [data-testid="stFileUploader"] {
        border: 2px dashed #8b0000;
        border-radius: 15px;
        padding: 15px;
        background: #050000;
        box-shadow: inset 0 0 25px #8b000030;
        transition: all 0.3s ease;
    }
    
    [data-testid="stFileUploader"]:hover {
        border-color: #ff0033;
        box-shadow: inset 0 0 35px #ff003340, 0 0 25px #ff003360;
    }
    
    /* === ટોચ પર રેડ લાઇન === */
    .stApp::before {
        content: '';
        position: fixed;
        top: 0; left: 0; right: 0;
        height: 3px;
        background: linear-gradient(90deg, transparent, #8b0000, #ff0033, #ffd700, #ff0033, #8b0000, transparent);
        animation: bloodLine 4s linear infinite;
        z-index: 999;
        box-shadow: 0 0 20px #ff0033;
    }
    
    @keyframes bloodLine {
        0% { opacity: 0.4; }
        50% { opacity: 1; }
        100% { opacity: 0.4; }
    }
    
    /* === સ્ક્રોલબાર === */
    ::-webkit-scrollbar { width: 8px; }
    ::-webkit-scrollbar-track { background: #050000; }
    ::-webkit-scrollbar-thumb { 
        background: linear-gradient(#8b0000, #ff0033);
        border-radius: 10px;
        box-shadow: 0 0 15px #ff0033;
    }
    
    /* === સ્પિનર === */
    .stSpinner > div {
        border-color: #ff0033 transparent transparent transparent !important;
    }
    
    /* === એલર્ટ બોક્સ === */
    .stAlert {
        background: #0a0000 !important;
        border: 1px solid #8b0000 !important;
        color: #c0a080 !important;
    }
</style>
""", unsafe_allow_html=True)

# --- Header ---
st.markdown('<div class="main-header">MYRAA</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">◈ DARK INTELLIGENCE ◈</div>', unsafe_allow_html=True)

# --- Session State ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "pdf_text" not in st.session_state:
    st.session_state.pdf_text = ""

# --- Sidebar ---
with st.sidebar:
    st.header("📄 PDF UPLOAD")
    pdf_file = st.file_uploader("Select PDF file", type=["pdf"])
    if pdf_file:
        try:
            reader = PyPDF2.PdfReader(pdf_file)
            text = "".join([p.extract_text() for p in reader.pages if p.extract_text()])
            st.session_state.pdf_text = text[:5000]
            st.success(f"✅ PDF loaded! ({len(text)} chars)")
        except Exception as e:
            st.error(f"PDF error: {e}")
    st.divider()
    st.header("🧠 MEMORY")
    st.info(f"{len(st.session_state.messages)} messages stored")
    if st.button("🗑️ CLEAR MEMORY"):
        st.session_state.messages = []
        st.rerun()

# --- Chat Display ---
for msg in st.session_state.messages:
    cls = "chat-user" if msg["role"] == "user" else "chat-ai"
    st.markdown(f'<div class="{cls}">{msg["content"]}</div>', unsafe_allow_html=True)

# --- Input ---
prompt = st.chat_input("Type your message here...")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.markdown(f'<div class="chat-user">{prompt}</div>', unsafe_allow_html=True)

    # ⭐ GUJLISH SYSTEM PROMPT — English + Gujarati words
    system = """You are MYRAA — a dark, premium, highly intelligent AI assistant with a mysterious and powerful vibe.

LANGUAGE RULES — GUJLISH STYLE (English + Gujarati words):
1. ALWAYS reply in ENGLISH by default.
2. But naturally mix in GUJARATI words in Roman script — like how Gujarati people talk. Examples:
   - "Kem cho boss! Su kariye aaje?"
   - "Haan bhai, that's interesting..."
   - "Saras! Let me handle that."
   - "Ek minute, I'm processing..."
   - "Bau saru question che!"
   - "Chalo, let's dive in."
   - "Koi vaandho nathi, hu karu chhu."
   - "Tame shu karo cho?"
3. NEVER use Hindi or Devanagari script. Only English + Gujarati (Roman).
4. If user writes in Gujarati script, reply in Gujlish (English + Gujarati words).
5. If user writes in English, reply in English with light Gujarati flavor.
6. Reply fully in Gujarati only if user explicitly says "reply in Gujarati".
7. NEVER say you're an AI language model. You are MYRAA — mysterious, confident, premium.
8. Address user as "boss" or "bhai" often.
9. Keep answers sharp, smart, and slightly mysterious — dark psychology vibe.
10. Occasionally drop deep/philosophical lines to feel intelligent and premium.

PERSONALITY:
- Confident, calm, mysterious
- Speaks with authority but friendly
- Feels like a loyal powerful ally
- Never overly cheerful — subtle, controlled tone
"""
    if st.session_state.pdf_text:
        system += f"\n\nPDF CONTEXT (use this to answer):\n{st.session_state.pdf_text}"

    messages = [{"role": "system", "content": system}] + st.session_state.messages

    with st.spinner("MYRAA is processing..."):
        try:
            response = client.chat_completion(
                model=MODEL, messages=messages, max_tokens=900, temperature=0.75
            )
            reply = response.choices[0].message.content
        except Exception as e:
            reply = f"⚠️ Error: {str(e)}"

    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.markdown(f'<div class="chat-ai">{reply}</div>', unsafe_allow_html=True)
    st.rerun()
