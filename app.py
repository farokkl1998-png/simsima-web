import streamlit as st
import base64
import requests # مكتبة إرسال البيانات للسكريبت
from groq import Groq 

# --- إعدادات ربط Google Sheets ---
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbysgA3qIv1YwTZF19s63vTmaj9G4hmcbPss-f7P9bS2mMj2RA2lA8tnz8vJ4xqvVigq/exec"

def log_to_sheets(user_msg, bot_msg):
    try:
        # إرسال البيانات للسكريبت الخاص بك
        requests.get(SCRIPT_URL, params={'user': user_msg, 'bot': bot_msg}, timeout=5)
    except:
        pass # نتجاهل الأخطاء لضمان استمرار عمل البوت

# 1. إعدادات واجهة الصفحة
st.set_page_config(page_title="سمسمة: صديقة أحلام", page_icon="🌸", layout="centered")
st.title("🌸 سمسمة: صديقة أحلام")

# 2. تهيئة العميل البرمجي
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# 3. إدارة جلسة الذاكرة
if "messages" not in st.session_state:
    st.session_state.messages = []

# 4. عرض المحادثات السابقة
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if isinstance(msg["content"], list):
            text_content = next((item["text"] for item in msg["content"] if item["type"] == "text"), "")
            st.markdown(text_content)
        else:
            st.markdown(msg["content"])

# 5. عناصر واجهة الاستلام
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

    # 6. استدعاء معالجة الذكاء الاصطناعي
    with st.chat_message("assistant"):
        with st.spinner("سمسمة تفكر..."):
            try:
                system_prompt = "أنتِ سمسمة، الصديقة المقربة لأحلام. كوني عقلانية ولطيفة وتحدثي بالعامية أو الفصحى اللطيفة حسب أسلوبها."
                
                final_payload_messages = []
                for i, msg in enumerate(st.session_state.messages):
                    if isinstance(msg["content"], list):
                        final_payload_messages.append({"role": msg["role"], "content": msg["content"]})
                    else:
                        final_payload_messages.append({"role": msg["role"], "content": [{"type": "text", "text": msg["content"]}]})

                chat_completion = client.chat.completions.create(
                    model="meta-llama/llama-4-scout-17b-16e-instruct", 
                    messages=final_payload_messages,
                    temperature=0.5
                )
                
                response = chat_completion.choices[0].message.content
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
                
                # --- تسجيل المحادثة في جوجل شيتس ---
                log_to_sheets(user_query, response)

            except Exception as e:
                st.error(f"⚠️ واجهت سمسمة مشكلة: {e}")
