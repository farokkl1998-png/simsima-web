import streamlit as st
import requests
import urllib3

# إيقاف تحذيرات الاتصال
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# إعدادات الصفحة
st.set_page_config(page_title="سمسمة: صديقة أحلام", page_icon="🌸", layout="centered")

st.markdown("""
<style>
div[data-testid="stChatMessage"] { text-align: right; direction: rtl; }
div[data-testid="stChatMessage"] p { font-size: 18px; font-family: 'Amiri', serif; }
h1 { text-align: center; color: #FF4081; font-family: 'Amiri', serif; }
</style>
""", unsafe_allow_html=True)

st.title("🌸 سمسمة: صديقة أحلام")

# الروابط والمفاتيح
API_KEY = st.secrets["GROQ_API_KEY"]
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

SYSTEM_INSTRUCTION = {
    "role": "system",
    "content": "أنتِ سمسمة، الصديقة المقربة لـ 'أحلام'. ردودكِ بسيطة، هادئة، ومختصرة. خاطبي 'أحلام' باسمها. كوني صديقة عقلانية ومتزنة."
}

if "messages" not in st.session_state:
    st.session_state.messages = []

# عرض المحادثة
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

def get_ai_response(user_input):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    # تجهيز سجل المحادثة (نص فقط)
    context = [SYSTEM_INSTRUCTION] + [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages[-10:]]
    
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": context,
        "temperature": 0.7
    }

    try:
        r = requests.post(GROQ_URL, headers=headers, json=payload, verify=False, timeout=20)
        if r.status_code == 200:
            return r.json()['choices'][0]['message']['content'].strip()
        else:
            return f"عذراً يا أحلام، سمسمة واجهت خطأ تقنياً بسيطاً (رمز: {r.status_code})."
    except:
        return "مشكلة في الاتصال، حاولي مجدداً يا أحلام."

# واجهة المدخلات (نص فقط)
user_query = st.chat_input("اكتبي لسمسمة يا أحلام...")

if user_query:
    with st.chat_message("user"):
        st.markdown(user_query)
    
    st.session_state.messages.append({"role": "user", "content": user_query})

    with st.chat_message("assistant"):
        with st.spinner("سمسمة تفكر..."):
            response = get_ai_response(user_query)
            st.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})

if st.sidebar.button("تصفير المحادثة"):
    st.session_state.messages = []
    st.rerun()
