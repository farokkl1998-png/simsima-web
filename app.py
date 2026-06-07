import streamlit as st
import requests
import base64

# إعدادات الصفحة
st.set_page_config(page_title="سمسمة: صديقة أحلام", page_icon="🌸", layout="centered")

st.title("🌸 سمسمة: صديقة أحلام")

# المفاتيح
API_KEY = st.secrets["GROQ_API_KEY"]
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

# دالة إرسال الطلب (تدعم النص والصورة)
def get_ai_response(messages, user_input, image_base64=None):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    # بناء المحتوى حسب هيكلية Groq الجديدة
    content = [{"type": "text", "text": user_input}]
    if image_base64:
        content.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}})

    # إضافة رسالة المستخدم الجديدة
    payload_messages = [{"role": m["role"], "content": m["content"]} for m in messages]
    payload_messages[-1]["content"] = content

    payload = {
        "model": "llama-3.2-11b-vision-preview",
        "messages": [{"role": "system", "content": "أنتِ سمسمة، الصديقة المقربة لأحلام. كوني عقلانية ولطيفة."}] + payload_messages,
        "temperature": 0.5
    }

    response = requests.post(GROQ_URL, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content']
    else:
        return f"عذراً، حدث خطأ (رمز {response.status_code})."

if "messages" not in st.session_state:
    st.session_state.messages = []

# عرض المحادثة
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# المدخلات
uploaded_file = st.file_uploader("ارفعي صورة يا أحلام...", type=["jpg", "png"])
user_query = st.chat_input("اكتبي لسمسمة...")

if user_query:
    image_base64 = None
    if uploaded_file:
        image_base64 = base64.b64encode(uploaded_file.getvalue()).decode('utf-8')
        st.session_state.messages.append({"role": "user", "content": user_query})
        with st.chat_message("user"):
            st.image(uploaded_file)
            st.markdown(user_query)
    else:
        st.session_state.messages.append({"role": "user", "content": user_query})
        with st.chat_message("user"):
            st.markdown(user_query)

    with st.chat_message("assistant"):
        with st.spinner("سمسمة تفكر..."):
            response = get_ai_response(st.session_state.messages, user_query, image_base64)
            st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})
