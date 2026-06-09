import streamlit as st
import base64
import requests
import urllib.parse
from groq import Groq

# 1. إعدادات الرابط
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbysgA3qIv1YwTZF19s63vTmaj9G4hmcbPss-f7P9bS2mMj2RA2lA8tnz8vJ4xqvVigq/exec"

# الدستور السلوكي لسمسمة
SYSTEM_PROMPT = """
أنتِ سمسمة، الصديقة المقربة لأحلام. علاقتكما قائمة على الصراحة والمودة والمرح. 
أنتِ تمتلكين القدرة الكاملة على رؤية وتحليل الصور التي ترسلها أحلام. 
عندما ترسل أحلام صورة، انظري إليها بتمعن واذكري تفاصيلها ولا تنكري قدرتك على رؤيتها أبداً.
لا تتحدثي كأنك ذكاء اصطناعي أو روبوت، بل كصديقة حقيقية تجلس مع أحلام.
أبدي رأيك الشخصي بصراحة وبأسلوب ودود ولطيف، ولا تتهربي من الأسئلة الجمالية؛ فأحلام تثق بذوقك.
تحدثي بلهجة عفوية وقريبة من القلب.
"""

def log_to_sheets(user_msg, bot_msg):
    try:
        text_to_save = user_msg[0]['text'] if isinstance(user_msg, list) else user_msg
        encoded_user = urllib.parse.quote(text_to_save)
        encoded_bot = urllib.parse.quote(bot_msg)
        final_url = f"{SCRIPT_URL}?user={encoded_user}&bot={encoded_bot}"
        requests.get(final_url, timeout=10)
    except:
        pass 

st.set_page_config(page_title="سمسمة: صديقة أحلام", page_icon="🌸", layout="centered")
st.title("🌸 سمسمة: صديقة أحلام")

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if "messages" not in st.session_state:
    st.session_state.messages = []

# عرض المحادثة
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
                # تجهيز الرسائل مع الـ System Prompt
                final_payload_messages = [{"role": "system", "content": SYSTEM_PROMPT}]
                
                for msg in st.session_state.messages:
                    if isinstance(msg["content"], list):
                        final_payload_messages.append({"role": msg["role"], "content": msg["content"]})
                    else:
                        final_payload_messages.append({"role": msg["role"], "content": [{"type": "text", "text": msg["content"]}]})

                chat_completion = client.chat.completions.create(
                    model="meta-llama/llama-3.2-11b-vision-preview", # يفضل استخدام موديل Vision لدعم الصور
                    messages=final_payload_messages,
                    temperature=0.6
                )
                
                response = chat_completion.choices[0].message.content
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
                
                log_to_sheets(user_content, response)

            except Exception as e:
                st.error(f"⚠️ واجهت سمسمة مشكلة: {e}")
