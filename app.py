import streamlit as st
from huggingface_hub import InferenceClient
import PyPDF2

# --- Hugging Face API ---
HF_TOKEN = st.secrets["HF_TOKEN"]
client = InferenceClient(token=HF_TOKEN)
MODEL = "meta-llama/Llama-3.3-70B-Instruct"

# --- Page Config ---
st.set_page_config(page_title="MYRAA", page_icon="◆", layout="wide")

# --- Clean Sci-Fi CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
    
    * { font-family: 'Inter', -apple-system, sans-serif; }
    
    /* === મુખ્ય બેકગ્રાઉન્ડ — ChatGPT જેવું ડાર્ક ગ્રે === */
    .stApp {
        background: #18181b;
        color: #ececec;
    }
    
    /* === હેડર === */
    .header-wrap {
        text-align: center;
        padding: 24px 0 8px 0;
        border-bottom: 1px solid #2a2a2e;
        margin-bottom: 20px;
    }
    
    .main-header {
        font-family: 'JetBrains Mono', monospace;
        font-size: 1.6rem;
        font-weight: 500;
        color: #ececec;
        letter-spacing: 6px;
        text-transform: uppercase;
        margin: 0;
    }
    
    .main-header span {
        color: #4a9eff;
    }
    
    .subtitle {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.7rem;
        color: #6b6b73;
        letter-spacing: 4px;
        text-transform: uppercase;
        margin-top: 6px;
    }
    
    .status-dot {
        display: inline-block;
        width: 6px;
        height: 6px;
        background: #22c55e;
        border-radius: 50%;
        margin-right: 6px;
        box-shadow: 0 0 8px #22c55e;
        animation: pulse 2s ease-in-out infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.4; }
    }
    
    /* === ચેટ બબલ્સ — ChatGPT જેવા clean === */
    .chat-user {
        background: #2a2a2e;
        color: #ececec;
        padding: 14px 18px;
        border-radius: 18px 18px 4px 18px;
        margin: 12px 0;
        max-width: 75%;
        margin-left: auto;
        font-size: 0.95rem;
        line-height: 1.6;
        animation: fadeInUp 0.3s ease-out;
        border: 1px solid #35353a;
    }
    
    .chat-ai {
        background: #212124;
        color: #d4d4d8;
        padding: 14px 18px;
        border-radius: 18px 18px 18px 4px;
        margin: 12px 0;
        max-width: 80%;
        border: 1px solid #2a2a2e;
        border-left: 2px solid #4a9eff;
        font-size: 0.95rem;
        line-height: 1.7;
        animation: fadeInUp 0.3s ease-out;
    }
    
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(8px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* === સાઇડબાર === */
    [data-testid="stSidebar"] {
        background: #131316;
        border-right: 1px solid #2a2a2e;
    }
    
    [data-testid="stSidebar"] h2 {
        font-family: 'JetBrains Mono', monospace;
        color: #d4d4d8;
        font-size: 0.75rem;
        letter-spacing: 2px;
        text-transform: uppercase;
        font-weight: 500;
        margin-bottom: 12px;
    }
    
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] span {
        color: #a1a1aa !important;
        font-size: 0.85rem;
    }
    
    /* === બટન === */
    .stButton > button {
        background: #2a2a2e;
        color: #d4d4d8;
        border: 1px solid #35353a;
        border-radius: 10px;
        font-weight: 500;
        width: 100%;
        font-size: 0.85rem;
        padding: 10px;
        letter-spacing: 0.5px;
        transition: all 0.2s ease;
    }
    
    .stButton > button:hover {
        background: #35353a;
        border-color: #4a9eff;
        color: #4a9eff;
    }
    
    /* === ઇનપુટ બોક્સ — ChatGPT જેવું === */
    .stChatInput {
        border-top: 1px solid #2a2a2e;
    }
    
    .stChatInput textarea {
        background: #212124 !important;
        border: 1px solid #35353a !important;
        color: #ececec !important;
        border-radius: 14px !important;
        font-size: 0.95rem !important;
        padding: 14px 18px !important;
        box-shadow: none !important;
        transition: border-color 0.2s ease;
    }
    
    .stChatInput textarea:focus {
        border-color: #4a9eff !important;
        box-shadow: 0 0 0 3px #4a9eff20 !important;
    }
    
    .stChatInput textarea::placeholder {
        color: #6b6b73 !important;
    }
    
    /* === PDF અપલોડ === */
    [data-testid="stFileUploader"] {
        border: 1px dashed #35353a;
        border-radius: 12px;
        padding: 12px;
        background: #1c1c20;
        transition: all 0.2s ease;
    }
    
    [data-testid="stFileUploader"]:hover {
        border-color: #4a9eff;
        background: #212124;
    }
    
    [data-testid="stFileUploader"] section {
        background: transparent !important;
    }
    
    /* === એલર્ટ === */
    .stAlert {
        background: #1c1c20 !important;
        border: 1px solid #2a2a2e !important;
        border-radius: 10px !important;
        color: #a1a1aa !important;
    }
    
    /* === સ્પિનર === */
    .stSpinner > div {
        border-color: #4a9eff transparent transparent transparent !important;
    }
    
    /* === સ્ક્રોલબાર === */
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: #18181b; }
    ::-webkit-scrollbar-thumb { 
        background: #35353a;
        border-radius: 3px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #4a9eff;
    }
    
    /* === સ્ટ્રીમલિટ ડિફોલ્ટ છુપાવો === */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header { visibility: hidden; }
    
    /* === hr લાઇન === */
    hr {
        border-color: #2a2a2e !important;
        margin: 16px 0 !important;
    }
</style>
""", unsafe_allow_html=True)

# --- Header ---
st.markdown("""
<div class="header-wrap">
    <h1 class="main-header">MYR<span>AA</span></h1>
    <div class="subtitle"><span class="status-dot"></span>System Online · Ready</div>
</div>
""", unsafe_allow_html=True)

# --- Session State ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "pdf_text" not in st.session_state:
    st.session_state.pdf_text = ""

# --- Sidebar ---
with st.sidebar:
    st.header("◆ PDF Upload")
    pdf_file = st.file_uploader("Select PDF", type=["pdf"], label_visibility="collapsed")
    if pdf_file:
        try:
            reader = PyPDF2.PdfReader(pdf_file)
            text = "".join([p.extract_text() for p in reader.pages if p.extract_text()])
            st.session_state.pdf_text = text[:5000]
            st.success(f"✓ PDF loaded ({len(text)} chars)")
        except Exception as e:
            st.error(f"✗ Error: {e}")
    
    st.divider()
    
    st.header("◆ Memory")
    st.info(f"{len(st.session_state.messages)} messages")
    
    if st.button("⌫ Clear Memory"):
        st.session_state.messages = []
        st.rerun()

# --- Chat Display ---
for msg in st.session_state.messages:
    cls = "chat-user" if msg["role"] == "user" else "chat-ai"
    st.markdown(f'<div class="{cls}">{msg["content"]}</div>', unsafe_allow_html=True)

# --- Input ---
prompt = st.chat_input("Message MYRAA...")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.markdown(f'<div class="chat-user">{prompt}</div>', unsafe_allow_html=True)

    # ⭐ GUJLISH SYSTEM PROMPT
    system = """You are MYRAA — a highly intelligent AI assistant with a calm, confident, sci-fi vibe.

LANGUAGE RULES — GUJLISH STYLE (English + Gujarati words in Roman script):
1. ALWAYS reply in ENGLISH by default.
2. Naturally mix in GUJARATI words in Roman script. Examples:
   - "Kem cho boss. Su kariye aaje?"
   - "Haan bhai, that's correct."
   - "Saras! Let me handle that."
   - "Ek minute, hu check karu chhu..."
   - "Bau saru question che!"
   - "Chalo, let's do it."
3. NEVER use Hindi or Devanagari script. Only English + Gujarati (Roman).
4. If user writes in Gujarati, reply in Gujlish (English + Gujarati words).
5. If user writes in English, reply in English with light Gujarati touch.
6. Only reply fully in Gujarati if user explicitly says "reply in Gujarati".
7. Never say you're an AI language model — you are MYRAA.
8. Address user as "boss" or "bhai" occasionally.
9. Keep answers clean, sharp, and helpful.
10. Be warm but professional — like a smart friend.

PERSONALITY:
- Calm, confident, modern
- Friendly but not overly casual
- Speaks clearly and concisely
"""
    if st.session_state.pdf_text:
        system += f"\n\nPDF CONTEXT:\n{st.session_state.pdf_text}"

    messages = [{"role": "system", "content": system}] + st.session_state.messages

    with st.spinner("Thinking..."):
        try:
            response = client.chat_completion(
                model=MODEL, messages=messages, max_tokens=900, temperature=0.7
            )
            reply = response.choices[0].message.content
        except Exception as e:
            reply = f"⚠️ Error: {str(e)}"

    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.markdown(f'<div class="chat-ai">{reply}</div>', unsafe_allow_html=True)
    st.rerun()
