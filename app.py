import streamlit as st
import base64
import requests
import urllib.parse

SCRIPT_URL = "https://google.com"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

def log_to_sheets(user_msg, bot_msg):
    try:
        text_to_save = user_msg['text'] if isinstance(user_msg, list) else user_msg
        encoded_user = urllib.parse.quote(text_to_save)
        encoded_bot = urllib.parse.quote(bot_msg)
        final_url = f"{SCRIPT_URL}?user={encoded_user}&bot={encoded_bot}"
        requests.get(final_url, timeout=10)
    except Exception as e:
        pass 

st.set_page_config(page_title="سمسمة: صديقة أحلام", page_icon="🌸", layout="centered")
st.title("🌸 سمسمة: صديقة أحلام")

# إضافة زر تصفير الذاكرة في الجانب الأيسر لتنظيف الأخطاء القديمة فوراً
if st.button("🔄 تفريغ المحادثة والبدء من جديد"):
    st.session_state.messages = []
    st.session_state.uploader_key = 0
    st.rerun()

OPENROUTER_API_KEY = st.secrets["OPENROUTER_API_KEY"]

if "messages" not in st.session_state:
    st.session_state.messages = []

if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0

# عرض السجل الحالي
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if isinstance(msg["content"], list):
            for item in msg["content"]:
                if item["type"] == "text":
                    st.markdown(item["text"])
                elif item["type"] == "image_url":
                    st.image(item["image_url"]["url"], caption="الصورة في السجل")
        else:
            st.markdown(msg["content"])

uploaded_file = st.file_uploader("ارفعي صورة يا أحلام...", type=["jpg", "png", "jpeg"], key=f"file_uploader_{st.session_state.uploader_key}")
user_query = st.chat_input("اكتبي لسمسمة...")

if user_query:
    if uploaded_file:
        image_bytes = uploaded_file.getvalue()
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        user_content = [
            {"type": "text", "text": user_query},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
        ]
        with st.chat_message("user"):
            st.image(uploaded_file, caption="الصورة المرفوعة")
            st.markdown(user_query)
        st.session_state.uploader_key += 1
    else:
        user_content = user_query
        with st.chat_message("user"):
            st.markdown(user_query)

    st.session_state.messages.append({"role": "user", "content": user_content})

    with st.chat_message("assistant"):
        with st.spinner("سمسمة تتفاعل معك..."):
            try:
                headers = {
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "Content-Type": "application/json"
                }

                final_payload_messages = []
                for msg in st.session_state.messages:
                    if isinstance(msg["content"], list):
                        final_payload_messages.append({"role": msg["role"], "content": msg["content"]})
                    else:
                        final_payload_messages.append({"role": msg["role"], "content": [{"type": "text", "text": msg["content"]}]})

                payload = {
                    "model": "google/gemini-2.5-flash",
                    "messages": final_payload_messages,
                    "max_tokens": 1000
                }

                response = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=20)
                res_data = response.json()
                
                # المعالجة الحمائية القاطعة لتجنب أزمة AttributeError الكاذبة
                if isinstance(res_data, dict) and 'choices' in res_data:
                    bot_response_text = res_data['choices'][0]['message']['content']
                    st.markdown(bot_response_text)
                    st.session_state.messages.append({"role": "assistant", "content": bot_response_text})
                else:
                    # سحب رسالة الخطأ النصية الصريحة من السيرفر وعرضها
                    error_msg = res_data.get('error', {}).get('message', str(res_data))
                    st.error(f"سيرفر OpenRouter رد ببيانات غير متوقعة: {error_msg}")
                    bot_response_text = "خطأ في معالجة البيانات السحابية"

                log_to_sheets(user_content, bot_response_text)
                st.rerun()

            except Exception as e:
                st.error(f"⚠️ واجهت سمسمة عقبة في معالجة طلبك: {e}")
