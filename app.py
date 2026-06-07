import streamlit as st
import base64
import requests # مكتبة الربط التي أثبتت نجاحها
from groq import Groq

# --- الإعدادات ---
# تأكد أن هذا الرابط هو الذي ظهر لك في صفحة الـ Deploy للسكريبت
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbysgA3qIv1YwTZF19s63vTmaj9G4hmcbPss-f7P9bS2mMj2RA2lA8tnz8vJ4xqvVigq/exec"

def log_to_sheets(user_msg, bot_msg):
    try:
        # إرسال البيانات للسكريبت
        requests.get(SCRIPT_URL, params={'user': user_msg, 'bot': bot_msg}, timeout=5)
    except:
        pass 

st.set_page_config(page_title="سمسمة: صديقة أحلام", page_icon="🌸", layout="centered")
st.title("🌸 سمسمة: صديقة أحلام")

# تهيئة العميل
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if "messages" not in st.session_state:
    st.session_state.messages = []

# عرض المحادثات
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if isinstance(msg["content"], list):
            text_content = next((item["text"] for item in msg["content"] if item["type"] == "text"), "")
            st.markdown(text_content)
        else:
            st.markdown(msg["content"])

uploaded_file = st.file_uploader("ارفعي صورة يا أحلام...", type=["jpg", "png", "jpeg"])
user_query = st.chat_input("اكتبي لسمسمة...")

if user_query:
    user_content = user_query
    if uploaded_file:
        image_base64 = base64.b64encode(uploaded_file.getvalue()).decode('utf-8')
        user_content = [{"type": "text", "text": user_query}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}]
        with st.chat_message("user"):
            st.image(uploaded_file)
            st.markdown(user_query)
    else:
        with st.chat_message("user"):
            st.markdown(user_query)

    st.session_state.messages.append({"role": "user", "content": user_content})

    with st.chat_message("assistant"):
        with st.spinner("سمسمة تفكر..."):
            try:
                system_prompt = "أنتِ سمسمة، الصديقة المقربة لأحلام. "
                
                # إعداد الرسائل
                final_payload = []
                for msg in st.session_state.messages:
                    final_payload.append({"role": msg["role"], "content": msg["content"]})
                
                chat_completion = client.chat.completions.create(
                    model="meta-llama/llama-4-scout-17b-16e-instruct", 
                    messages=final_payload,
                    temperature=0.5
                )
                
                response = chat_completion.choices[0].message.content
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
                
                # --- خطوة التسجيل التي نجحت في اختباراتك ---
                log_to_sheets(user_query, response)

            except Exception as e:
                st.error(f"⚠️ واجهت سمسمة مشكلة: {e}")
