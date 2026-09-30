import streamlit as st
from huggingface_hub import InferenceClient
import PyPDF2

# --- Hugging Face API ---
HF_TOKEN = st.secrets["HF_TOKEN"]
client = InferenceClient(token=HF_TOKEN)
MODEL = "meta-llama/Llama-3.3-70B-Instruct"  # ફ્રી ટિયરમાં ચાલતું મોડેલ

# --- Page Config ---
st.set_page_config(page_title="MYRAA", page_icon="🤖", layout="wide")

# --- Custom CSS (Iron Man / JARVIS Style) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;900&family=Inter:wght@400;600&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background: radial-gradient(ellipse at center, #0a0e17 0%, #000000 100%); }
    .main-header {
        font-family: 'Orbitron', sans-serif;
        font-size: 3.5rem; font-weight: 900;
        color: #00d4ff;
        text-shadow: 0 0 10px #00d4ff, 0 0 30px #00d4ff, 0 0 60px #00d4ff80;
        text-align: center; padding: 20px 10px 5px 10px;
        letter-spacing: 8px;
        animation: pulse 2s ease-in-out infinite;
    }
    @keyframes pulse {
        0%, 100% { text-shadow: 0 0 10px #00d4ff, 0 0 30px #00d4ff, 0 0 60px #00d4ff80; }
        50% { text-shadow: 0 0 20px #00d4ff, 0 0 50px #00d4ff, 0 0 100px #00d4ff; }
    }
    .subtitle {
        text-align: center; color: #00d4ff80;
        font-family: 'Orbitron', sans-serif;
        font-size: 0.85rem; letter-spacing: 4px;
        margin-bottom: 20px;
    }
    .chat-user {
        background: linear-gradient(135deg, #00d4ff 0%, #0090ff 100%);
        color: #000; padding: 14px 20px;
        border-radius: 18px 18px 4px 18px;
        margin: 10px 0; max-width: 70%;
        margin-left: auto; font-weight: 500;
        box-shadow: 0 0 20px #00d4ff60;
        animation: fadeIn 0.3s ease-in;
    }
    .chat-ai {
        background: linear-gradient(135deg, #0d1321 0%, #1a2332 100%);
        color: #e0e0e0; padding: 14px 20px;
        border-radius: 18px 18px 18px 4px;
        margin: 10px 0; max-width: 75%;
        border: 1px solid #00d4ff40;
        box-shadow: 0 0 15px #00d4ff20;
        animation: fadeIn 0.3s ease-in;
        line-height: 1.6;
    }
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0a0e17 0%, #0d1321 100%);
        border-right: 1px solid #00d4ff40;
    }
    [data-testid="stSidebar"] h2 {
        font-family: 'Orbitron', sans-serif;
        color: #00d4ff;
        text-shadow: 0 0 10px #00d4ff80;
        letter-spacing: 2px;
    }
    .stButton > button {
        background: linear-gradient(135deg, #00d4ff 0%, #0090ff 100%);
        color: #000; border: none;
        border-radius: 12px; font-weight: 700;
        width: 100%; font-family: 'Orbitron', sans-serif;
        letter-spacing: 1px;
        box-shadow: 0 0 15px #00d4ff60;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #00ff88 0%, #00d4ff 100%);
        box-shadow: 0 0 30px #00ff8890;
        transform: translateY(-2px);
    }
    .stChatInput textarea {
        background: #0d1321 !important;
        border: 1px solid #00d4ff60 !important;
        color: #e0e0e0 !important;
        border-radius: 25px !important;
        box-shadow: 0 0 15px #00d4ff30;
    }
    .stChatInput textarea:focus {
        border-color: #00ff88 !important;
        box-shadow: 0 0 25px #00ff8860 !important;
    }
    [data-testid="stFileUploader"] {
        border: 2px dashed #00d4ff60;
        border-radius: 12px;
        padding: 10px;
        background: #0a0e17;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">MYRAA</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">◉ PERSONAL AI ASSISTANT ◉</div>', unsafe_allow_html=True)

# --- Session State ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "pdf_text" not in st.session_state:
    st.session_state.pdf_text = ""

# --- Sidebar ---
with st.sidebar:
    st.header("📄 PDF અપલોડ")
    pdf_file = st.file_uploader("PDF પસંદ કરો", type=["pdf"])
    if pdf_file:
        try:
            reader = PyPDF2.PdfReader(pdf_file)
            text = "".join([p.extract_text() for p in reader.pages if p.extract_text()])
            st.session_state.pdf_text = text[:5000]
            st.success(f"✅ PDF વાંચી! ({len(text)} અક્ષરો)")
        except Exception as e:
            st.error(f"PDF વાંચવામાં ભૂલ: {e}")
    st.divider()
    st.header("🧠 યાદશક્તિ")
    st.info(f"{len(st.session_state.messages)} સંદેશા યાદ")
    if st.button("🗑️ યાદશક્તિ સાફ કરો"):
        st.session_state.messages = []
        st.rerun()

# --- Chat Display ---
for msg in st.session_state.messages:
    cls = "chat-user" if msg["role"] == "user" else "chat-ai"
    st.markdown(f'<div class="{cls}">{msg["content"]}</div>', unsafe_allow_html=True)

# --- Input ---
prompt = st.chat_input("તમારો સવાલ લખો...")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.markdown(f'<div class="chat-user">{prompt}</div>', unsafe_allow_html=True)

    system = "તું MYRAA છે, એક અત્યંત બુદ્ધિશાળી અને મદદગાર AI સહાયક. તું વપરાશકર્તાની ભાષામાં જ (ગુજરાતી, હિન્દી, અંગ્રેજી) જવાબ આપે છે. તું સ્પષ્ટ, મૈત્રીપૂર્ણ અને ટૂંકો જવાબ આપે છે."
    if st.session_state.pdf_text:
        system += f"\n\nPDF નો સંદર્ભ:\n{st.session_state.pdf_text}"

    messages = [{"role": "system", "content": system}] + st.session_state.messages

    with st.spinner("MYRAA વિચારે છે..."):
        try:
            response = client.chat_completion(
                model=MODEL, messages=messages, max_tokens=800, temperature=0.7
            )
            reply = response.choices[0].message.content
        except Exception as e:
            reply = f"⚠️ ભૂલ: {str(e)}"

    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.markdown(f'<div class="chat-ai">{reply}</div>', unsafe_allow_html=True)
    st.rerun()
