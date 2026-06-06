import streamlit as st
import requests
import urllib3
import base64

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
    "content": "أنتِ سمسمة، الصديقة المقربة لـ 'أحلام'. ردودكِ بسيطة، هادئة، ومختصرة. خاطبي 'أحلام' باسمها. إذا أُرسلت لك صورة، صفيها بدقة وذكاء. كوني صديقة عقلانية ومتزنة."
}

if "messages" not in st.session_state:
    st.session_state.messages = []

# عرض المحادثة
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

def get_ai_response(user_input, image_base64=None):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    # تجهيز محتوى الرسالة (يدعم النص أو النص مع الصورة)
    content = [{"type": "text", "text": user_input}]
    if image_base64:
        content.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}})

    context = [SYSTEM_INSTRUCTION] + [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages[-10:]]
    
    # تحديث الرسالة الأخيرة لتشمل المحتوى (نص + صورة)
    context[-1]["content"] = content

    payload = {
        "model": "llama-3.2-11b-vision-preview",
        "messages": context,
        "temperature": 0.5
    }

    try:
        r = requests.post(GROQ_URL, headers=headers, json=payload, verify=False, timeout=20)
        if r.status_code == 200:
            return r.json()['choices'][0]['message']['content'].strip()
        return f"خطأ: {r.status_code}"
    except:
        return "مشكلة في الاتصال، حاولي مجدداً يا أحلام."

# واجهة المدخلات
uploaded_file = st.file_uploader("اختاري صورة لترها سمسمة...", type=["jpg", "png", "jpeg"])
user_query = st.chat_input("اكتبي لسمسمة يا أحلام...")

if user_query:
    image_base64 = None
    if uploaded_file:
        image_base64 = base64.b64encode(uploaded_file.getvalue()).decode('utf-8')
        with st.chat_message("user"):
            st.image(uploaded_file, caption="صورتك")
            st.markdown(user_query)
    else:
        with st.chat_message("user"):
            st.markdown(user_query)
    
    st.session_state.messages.append({"role": "user", "content": user_query})

    with st.chat_message("assistant"):
        with st.spinner("سمسمة تتأمل الصورة وتفكر..."):
            response = get_ai_response(user_query, image_base64)
            st.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})

if st.sidebar.button("تصفير المحادثة"):
    st.session_state.messages = []
    st.rerun()
