import streamlit as st
import requests
import base64
import urllib3

# إيقاف تحذيرات الاتصال غير الآمن
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# إعدادات الصفحة
st.set_page_config(page_title="سمسمة: صديقة أحلام", page_icon="🌸", layout="centered")

st.markdown("""
<style>
div[data-testid="stChatMessage"] { text-align: right; direction: rtl; }
h1 { text-align: center; color: #FF4081; }
</style>
""", unsafe_allow_html=True)

st.title("🌸 سمسمة: صديقة أحلام")

# إعداد الـ API
if "GROQ_API_KEY" in st.secrets:
    API_KEY = st.secrets["GROQ_API_KEY"]
else:
    st.error("مفتاح API غير موجود في الإعدادات!")
    st.stop()

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

# تهيئة المحادثة
if "messages" not in st.session_state:
    st.session_state.messages = []

# وظيفة الاتصال بـ API
def get_ai_response(current_messages):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    # النموذج المحدث المدعوم حالياً
    payload = {
        "model": "llama-3.2-90b-vision-preview",
        "messages": [
            {"role": "system", "content": "أنتِ سمسمة، الصديقة المقربة لـ 'أحلام'. ردودكِ مختصرة وذكية. إذا رأيتِ صورة صفيها."}
        ] + current_messages,
        "temperature": 0.5
    }

    try:
        response = requests.post(GROQ_URL, headers=headers, json=payload, verify=False, timeout=30)
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            return f"خطأ ({response.status_code}): {response.text}"
    except Exception as e:
        return f"خطأ في الاتصال: {str(e)}"

# عرض الرسائل السابقة
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"] if isinstance(msg["content"], str) else "صورة مرفقة")

# واجهة المستخدم
uploaded_file = st.file_uploader("ارفعي صورة يا أحلام...", type=["jpg", "jpeg", "png"])
user_text = st.chat_input("اكتبي لسمسمة...")

if user_text:
    # تجهيز محتوى الرسالة
    message_content = [{"type": "text", "text": user_text}]
    
    if uploaded_file:
        image_data = base64.b64encode(uploaded_file.getvalue()).decode('utf-8')
        message_content.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}
        })
        # عرض الصورة في الشات
        with st.chat_message("user"):
            st.image(uploaded_file)
            st.markdown(user_text)
    else:
        with st.chat_message("user"):
            st.markdown(user_text)

    # إضافة الرسالة الحالية
    st.session_state.messages.append({"role": "user", "content": message_content})

    # الحصول على رد الذكاء الاصطناعي
    with st.chat_message("assistant"):
        with st.spinner("سمسمة تفكر..."):
            ai_response = get_ai_response(st.session_state.messages[-5:])
            st.markdown(ai_response)
    
    st.session_state.messages.append({"role": "assistant", "content": ai_response})
