import streamlit as st
from huggingface_hub import InferenceClient
import PyPDF2

# --- Hugging Face API ---
HF_TOKEN = st.secrets["HF_TOKEN"]
client = InferenceClient(token=HF_TOKEN)
MODEL = "Qwen/Qwen2.5-7B-Instruct"

# --- Page Config ---
st.set_page_config(page_title="JARVIS", page_icon="🤖", layout="wide")

# --- Custom CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background: linear-gradient(135deg, #0a0e17 0%, #0d1321 100%); }
    .main-header { font-size: 2.5rem; color: #00d4ff; text-shadow: 0 0 20px #00d4ff80;
        font-weight: bold; text-align: center; padding: 10px; }
    .chat-user { background: #00d4ff; color: #0a0e17; padding: 12px 18px;
        border-radius: 18px 18px 4px 18px; margin: 8px 0; max-width: 70%;
        margin-left: auto; animation: fadeIn 0.3s ease-in; }
    .chat-ai { background: #1a2332; color: #e0e0e0; padding: 12px 18px;
        border-radius: 18px 18px 18px 4px; margin: 8px 0; max-width: 70%;
        border: 1px solid #1e2a3a; animation: fadeIn 0.3s ease-in; }
    @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } 
                        to { opacity: 1; transform: translateY(0); } }
    [data-testid="stSidebar"] { background: #0d1321; border-right: 1px solid #1e2a3a; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">🤖 JARVIS</div>', unsafe_allow_html=True)
st.caption("તમારો પર્સનલ AI સહાયક | ફ્રી | Hugging Face દ્વારા")

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

    system = "તું JARVIS છે, એક મદદગાર AI સહાયક. વપરાશકર્તાની ભાષામાં જ જવાબ આપ."
    if st.session_state.pdf_text:
        system += f"\n\nPDF નો સંદર્ભ:\n{st.session_state.pdf_text}"

    messages = [{"role": "system", "content": system}] + st.session_state.messages

    with st.spinner("JARVIS વિચારે છે..."):
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
