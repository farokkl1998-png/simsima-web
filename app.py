import streamlit as st
import requests
import base64

# إعدادات الصفحة
st.set_page_config(page_title="سمسمة: صديقة أحلام", page_icon="🌸", layout="centered")

st.markdown("""
<style>
div[data-testid="stChatMessage"] { text-align: right; direction: rtl; }
h1 { text-align: center; color: #FF4081; }
</style>
""", unsafe_allow_html=True)

st.title("🌸 سمسمة: صديقة أحلام")

# المفاتيح من إعدادات Streamlit
API_KEY = st.secrets["GROQ_API_KEY"]
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

# دالة الاستجابة مع دعم الصور
def get_ai_response(messages_history, user_input, image_base64=None):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    # 1. تنظيف التاريخ ليكون نصوصاً فقط (لتجنب الخطأ 400)
    payload_messages = [{"role": "system", "content": "أنتِ سمسمة، الصديقة المقربة لأحلام. كوني عقلانية ولطيفة."}]
    
    for msg in messages_history[:-1]:
        content = msg["content"]
        # استخراج النص إذا كان المحتوى بصيغة قائمة (من رسائل سابقة)
        if isinstance(content, list):
            for item in content:
                if item["type"] == "text":
                    content = item["text"]
                    break
        payload_messages.append({"role": msg["role"], "content": content})

    # 2. بناء الرسالة الأخيرة (نص + صورة إن وجدت)
    if image_base64:
        last_content = [
            {"type": "text", "text": user_input},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
        ]
    else:
        last_content = user_input

    payload_messages.append({"role": "user", "content": last_content})

    payload = {
        "model": "llama-3.2-11b-vision-preview",
        "messages": payload_messages,
        "temperature": 0.5
    }

    try:
        response = requests.post(GROQ_URL, headers=headers, json=payload)
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            return f"عذراً يا أحلام، حدث خطأ تقني (رمز {response.status_code})."
    except Exception as e:
        return f"خطأ في الاتصال: {e}"

# الحالة (State) للمحادثة
if "messages" not in st.session_state:
    st.session_state.messages = []

# عرض المحادثة السابقة
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# واجهة المدخلات
uploaded_file = st.file_uploader("ارفعي صورة يا أحلام...", type=["jpg", "png", "jpeg"])
user_query = st.chat_input("اكتبي لسمسمة يا أحلام...")

if user_query:
    image_base64 = None
    
    # إضافة الرسالة للحالة
    st.session_state.messages.append({"role": "user", "content": user_query})
    
    with st.chat_message("user"):
        if uploaded_file:
            st.image(uploaded_file, caption="صورة مرفوعة")
            image_base64 = base64.b64encode(uploaded_file.getvalue()).decode('utf-8')
        st.markdown(user_query)

    # جلب الرد
    with st.chat_message("assistant"):
        with st.spinner("سمسمة تتأمل الصورة وتفكر..."):
            response = get_ai_response(st.session_state.messages, user_query, image_base64)
            st.markdown(response)
    
    st.session_state.messages.append({"role": "assistant", "content": response})

if st.sidebar.button("مسح المحادثة"):
    st.session_state.messages = []
    st.rerun()
