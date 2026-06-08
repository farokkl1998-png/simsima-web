import streamlit as st
import base64
import requests
from groq import Groq

# 1. إعدادات واجهة الصفحة والرابط المعتمد
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbysgA3qIv1YwTZF19s63vTmaj9G4hmcbPss-f7P9bS2mMj2RA2lA8tnz8vJ4xqvVigq/exec"

def log_to_sheets(user_msg, bot_msg):
    try:
        # معالجة ذكية للصور: إذا كانت الرسالة قائمة، نكتب [صورة مرفقة]
        text_to_save = user_msg[0]['text'] if isinstance(user_msg, list) else user_msg
        if isinstance(user_msg, list): 
            text_to_save = "[صورة مرفقة] " + text_to_save
        
        requests.get(SCRIPT_URL, params={'user': text_to_save, 'bot': bot_msg}, timeout=5)
    except:
        pass 

st.set_page_config(page_title="سمسمة: صديقة أحلام", page_icon="🌸", layout="centered")
st.title("🌸 سمسمة: صديقة أحلام")

# 2. تهيئة العميل
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if "messages" not in st.session_state:
    st.session_state.messages = []

# 3. عرض المحادثات
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if isinstance(msg["content"], list):
            text_content = next((item["text"] for item in msg["content"] if item["type"] == "text"), "")
            st.markdown(text_content)
        else:
            st.markdown(msg["content"])

# 4. واجهة الإدخال
uploaded_file = st.file_uploader("ارفعي صورة يا أحلام...", type=["jpg", "png", "jpeg"])
user_query = st.chat_input("اكتبي لسمسمة...")

if user_query:
    if uploaded_file:
        image_base64 = base64.b64encode(uploaded_file.getvalue()).decode('utf-8')
        user_content = [
            {"type": "text", "text": user_query},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
        ]
        with st.chat_message("user"):
            st.image(uploaded_file, caption="الصورة المرفوعة")
            st.markdown(user_query)
    else:
        user_content = user_query
        with st.chat_message("user"):
            st.markdown(user_query)

    st.session_state.messages.append({"role": "user", "content": user_content})

    with st.chat_message("assistant"):
        with st.spinner("سمسمة تفكر..."):
            try:
                # 5. استدعاء الذكاء الاصطناعي
                chat_completion = client.chat.completions.create(
                    model="meta-llama/llama-4-scout-17b-16e-instruct", 
                    messages=st.session_state.messages,
                    temperature=0.5
                )
                
                response = chat_completion.choices[0].message.content
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
                
                # 6. الحفظ التلقائي في الجدول
                log_to_sheets(user_content, response)

            except Exception as e:
                st.error(f"⚠️ واجهت سمسمة مشكلة: {e}")
