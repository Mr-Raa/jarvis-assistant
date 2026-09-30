import streamlit as st
from huggingface_hub import InferenceClient
import PyPDF2

# --- Hugging Face API ---
HF_TOKEN = st.secrets["HF_TOKEN"]
client = InferenceClient(token=HF_TOKEN)
MODEL = "meta-llama/Llama-3.3-70B-Instruct"

# --- Page Config ---
st.set_page_config(page_title="MYRAA", page_icon="🤖", layout="wide")

# --- Iron Man Style CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;700;900&family=Rajdhani:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] { 
        font-family: 'Rajdhani', sans-serif;
        background: #000;
    }
    
    /* === સ્પેસ ગ્રિડ બેકગ્રાઉન્ડ === */
    .stApp {
        background: 
            radial-gradient(ellipse at top, #001a33 0%, #000000 70%),
            linear-gradient(#00d4ff08 1px, transparent 1px),
            linear-gradient(90deg, #00d4ff08 1px, transparent 1px);
        background-size: 100% 100%, 40px 40px, 40px 40px;
        animation: gridMove 20s linear infinite;
    }
    
    @keyframes gridMove {
        0% { background-position: 0 0, 0 0, 0 0; }
        100% { background-position: 0 0, 40px 40px, 40px 40px; }
    }
    
    /* === આર્ક રિએક્ટર હેડર === */
    .main-header {
        font-family: 'Orbitron', sans-serif;
        font-size: 4rem;
        font-weight: 900;
        color: #00d4ff;
        text-align: center;
        padding: 30px 10px 10px 10px;
        letter-spacing: 12px;
        text-shadow: 
            0 0 10px #00d4ff,
            0 0 20px #00d4ff,
            0 0 40px #00d4ff,
            0 0 80px #00d4ff,
            0 0 120px #00d4ff;
        animation: headerPulse 3s ease-in-out infinite;
    }
    
    @keyframes headerPulse {
        0%, 100% { 
            text-shadow: 0 0 10px #00d4ff, 0 0 20px #00d4ff, 0 0 40px #00d4ff, 0 0 80px #00d4ff;
            transform: scale(1);
        }
        50% { 
            text-shadow: 0 0 20px #00ff88, 0 0 40px #00d4ff, 0 0 80px #00d4ff, 0 0 120px #00d4ff;
            transform: scale(1.02);
        }
    }
    
    .subtitle {
        text-align: center;
        color: #00ff88;
        font-family: 'Orbitron', sans-serif;
        font-size: 0.9rem;
        letter-spacing: 6px;
        margin-bottom: 30px;
        text-shadow: 0 0 10px #00ff88;
        animation: blink 2s ease-in-out infinite;
    }
    
    @keyframes blink {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    /* === હોલોગ્રાફિક ચેટ બબલ્સ === */
    .chat-user {
        background: linear-gradient(135deg, #00d4ff 0%, #0080ff 100%);
        color: #000;
        padding: 16px 22px;
        border-radius: 20px 20px 4px 20px;
        margin: 12px 0;
        max-width: 70%;
        margin-left: auto;
        font-weight: 600;
        font-size: 1.05rem;
        box-shadow: 
            0 0 20px #00d4ff80,
            0 0 40px #00d4ff40,
            inset 0 0 10px #ffffff40;
        border: 1px solid #00d4ff;
        animation: slideInRight 0.4s ease-out;
    }
    
    .chat-ai {
        background: linear-gradient(135deg, #0a1a2e 0%, #0d1321 100%);
        color: #e0f4ff;
        padding: 16px 22px;
        border-radius: 20px 20px 20px 4px;
        margin: 12px 0;
        max-width: 75%;
        border-left: 3px solid #00d4ff;
        box-shadow: 
            0 0 20px #00d4ff30,
            inset 0 0 20px #00d4ff10;
        font-size: 1.05rem;
        line-height: 1.7;
        animation: slideInLeft 0.4s ease-out;
    }
    
    @keyframes slideInRight {
        from { opacity: 0; transform: translateX(30px); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    @keyframes slideInLeft {
        from { opacity: 0; transform: translateX(-30px); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    /* === સાઇડબાર === */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #050a14 0%, #0a0e17 100%);
        border-right: 1px solid #00d4ff60;
        box-shadow: 5px 0 30px #00d4ff20;
    }
    
    [data-testid="stSidebar"] h2 {
        font-family: 'Orbitron', sans-serif;
        color: #00d4ff;
        text-shadow: 0 0 10px #00d4ff80;
        letter-spacing: 3px;
        font-size: 1rem;
    }
    
    /* === બટન === */
    .stButton > button {
        background: linear-gradient(135deg, #00d4ff 0%, #0080ff 100%);
        color: #000;
        border: 2px solid #00d4ff;
        border-radius: 12px;
        font-weight: 700;
        width: 100%;
        font-family: 'Orbitron', sans-serif;
        letter-spacing: 2px;
        font-size: 0.85rem;
        padding: 10px;
        box-shadow: 0 0 20px #00d4ff60;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #00ff88 0%, #00d4ff 100%);
        box-shadow: 0 0 40px #00ff88;
        transform: translateY(-2px);
        border-color: #00ff88;
    }
    
    /* === નીયોન ઇનપુટ બોક્સ === */
    .stChatInput textarea {
        background: #0a0e17 !important;
        border: 2px solid #00d4ff !important;
        color: #00d4ff !important;
        border-radius: 30px !important;
        font-family: 'Rajdhani', sans-serif;
        font-size: 1.1rem !important;
        padding: 15px 25px !important;
        box-shadow: 
            0 0 20px #00d4ff60,
            inset 0 0 20px #00d4ff10 !important;
    }
    
    .stChatInput textarea:focus {
        border-color: #00ff88 !important;
        box-shadow: 
            0 0 30px #00ff88,
            inset 0 0 20px #00ff8820 !important;
    }
    
    .stChatInput textarea::placeholder {
        color: #00d4ff80 !important;
    }
    
    /* === PDF અપલોડ === */
    [data-testid="stFileUploader"] {
        border: 2px dashed #00d4ff80;
        border-radius: 15px;
        padding: 15px;
        background: #0a0e17;
        box-shadow: inset 0 0 20px #00d4ff20;
        transition: all 0.3s ease;
    }
    
    [data-testid="stFileUploader"]:hover {
        border-color: #00ff88;
        box-shadow: inset 0 0 30px #00ff8830;
    }
    
    /* === ટોચ પર ગ્લો લાઇન === */
    .stApp::before {
        content: '';
        position: fixed;
        top: 0; left: 0; right: 0;
        height: 2px;
        background: linear-gradient(90deg, transparent, #00d4ff, #00ff88, #00d4ff, transparent);
        animation: glowLine 3s linear infinite;
        z-index: 999;
    }
    
    @keyframes glowLine {
        0% { opacity: 0.5; }
        50% { opacity: 1; }
        100% { opacity: 0.5; }
    }
    
    /* === સ્ક્રોલબાર === */
    ::-webkit-scrollbar { width: 8px; }
    ::-webkit-scrollbar-track { background: #0a0e17; }
    ::-webkit-scrollbar-thumb { 
        background: linear-gradient(#00d4ff, #0080ff);
        border-radius: 10px;
        box-shadow: 0 0 10px #00d4ff;
    }
</style>
""", unsafe_allow_html=True)

# --- Header ---
st.markdown('<div class="main-header">MYRAA</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">◉ PERSONAL AI ASSISTANT ◉</div>', unsafe_allow_html=True)

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

    # ⭐ સિસ્ટમ પ્રોમ્પ્ટ - English Default, Gujarati words OK
    system = """You are MYRAA, a highly intelligent and helpful AI assistant.
    
IMPORTANT LANGUAGE RULES:
1. ALWAYS respond in ENGLISH by default.
2. If the user writes in Gujarati or Hindi, still respond in English, BUT you may include some Gujarati/Hindi words naturally for warmth (like "kem cho", "bhai", "saras", "haan").
3. Never fully switch to Gujarati script unless the user EXPLICITLY asks "reply in Gujarati".
4. Keep answers clear, friendly, and concise.
5. When reading PDFs, extract key info and reply in English.
6. Address the user as "boss" or "friend" occasionally for a JARVIS-like feel.
"""
    if st.session_state.pdf_text:
        system += f"\n\nPDF CONTEXT:\n{st.session_state.pdf_text}"

    messages = [{"role": "system", "content": system}] + st.session_state.messages

    with st.spinner("MYRAA is thinking..."):
        try:
            response = client.chat_completion(
                model=MODEL, messages=messages, max_tokens=800, temperature=0.7
            )
            reply = response.choices[0].message.content
        except Exception as e:
            reply = f"⚠️ Error: {str(e)}"

    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.markdown(f'<div class="chat-ai">{reply}</div>', unsafe_allow_html=True)
    st.rerun()
