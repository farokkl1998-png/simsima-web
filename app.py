import streamlit as st
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# إعدادات الصفحة
st.set_page_config(page_title="سمسمة: صديقة أحلام", page_icon="🌸", layout="centered")

st.markdown("""
<style>
.reportview-container .main .block-container{ max-width: 600px; }
div[data-testid="stChatMessage"] { text-align: right; direction: rtl; }
div[data-testid="stChatMessage"] p { font-size: 18px; font-family: 'Amiri', serif; }
h1 { text-align: center; color: #FF4081; font-family: 'Amiri', serif; }
</style>
""", unsafe_allow_html=True)

# العنوان مع أيقونة تعبيرية
st.title("🌸 سمسمة: صديقة أحلام 🌸")

# الروابط والمفاتيح
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbysgA3qIv1YwTZF19s63vTmaj9G4hmcbPss-f7P9bS2mMj2RA2lA8tnz8vJ4xqvVigq/exec"
API_KEY = st.secrets["GROQ_API_KEY"]
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

# تعديل التعليمات لتعرف أنها تخاطب أحلام
SYSTEM_INSTRUCTION = {
    "role": "system",
    "content": "أنتِ سمسمة، الصديقة المقربة لـ 'أحلام'. ردودكِ يجب أن تكون بسيطة، هادئة، ومختصرة. خاطبي 'أحلام' باسمها دائماً. تجنبي المبالغة في المشاعر. كوني صديقة عقلانية، متزنة، ودبلوماسية، وتحدثي بلهجة ودية خفيفة ومريحة."
}

if "messages" not in st.session_state:
    st.session_state.messages = []

# عرض المحادثة مع أيقونات تميز المستخدم عن سمسمة
for message in st.session_state.messages:
    # استخدام أيقونة (user) لأحلام و (assistant) لسمسمة
    avatar = "🌸" if message["role"] == "assistant" else "👤"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

def log_to_sheets(user_msg, ai_res):
    try: 
        requests.get(SCRIPT_URL, params={'user': user_msg, 'bot': ai_res}, timeout=5, verify=False)
    except: 
        pass

def get_ai_response(user_input):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    clean_context = [msg for msg in st.session_state.messages if msg['role'] in ['user', 'assistant']]
    context = [SYSTEM_INSTRUCTION] + clean_context[-10:]

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": context,
        "temperature": 0.5,
        "frequency_penalty": 0.6,
        "presence_penalty": 0.4
    }

    try:
        r = requests.post(GROQ_URL, headers=headers, json=payload, verify=False, timeout=12)
        if r.status_code == 200:
            return r.json()['choices'][0]['message']['content'].strip()
        return f"خطأ في السيرفر {r.status_code}"
    except:
        return "مشكلة في الاتصال، حاول مجدداً"

if user_query := st.chat_input("اكتبي لسمسمة يا أحلام..."):
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_query)
    st.session_state.messages.append({"role": "user", "content": user_query})

    with st.chat_message("assistant", avatar="🌸"):
        with st.spinner("سمسمة تفكر..."):
            response = get_ai_response(user_query)
            st.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})
    log_to_sheets(user_query, response)

if st.sidebar.button("تصفير المحادثة"):
    st.session_state.messages = []
    st.sidebar.success("تم تصفير المحادثة بنجاح!")
    st.rerun()
