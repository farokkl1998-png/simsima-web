import streamlit as st
import requests
from datetime import datetime

# --- إعدادات الرابط ---
GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbysgA3qIv1YwTZF19s63vTmaj9G4hmcbPss-f7P9bS2mMj2RA2lA8tnz8vJ4xqvVigq/exec"

# --- دالة الحفظ في Google Sheets ---
def log_to_sheets(user_msg, bot_res):
    try:
        params = {
            "user": user_msg,
            "bot": bot_res
        }
        response = requests.get(GOOGLE_SCRIPT_URL, params=params, timeout=10)
        return response.text
    except Exception as e:
        return f"خطأ في الاتصال: {str(e)}"

# --- واجهة Streamlit ---
st.title("Semsema AI")

# تهيئة سجل المحادثة
if "messages" not in st.session_state:
    st.session_state.messages = []

# عرض الرسائل السابقة
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- حلقة المحادثة ---
if prompt := st.chat_input("اكتب رسالتك هنا..."):
    # عرض رسالة المستخدم
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # هنا يتم استدعاء المنطق الخاص بالبوت (Groq API أو غيره)
    # لنفترض أن bot_response هو الرد الذي حصلت عليه
    bot_response = "هذا رد تجريبي من سمسمة" 

    # عرض رد البوت
    with st.chat_message("assistant"):
        st.markdown(bot_response)
    st.session_state.messages.append({"role": "assistant", "content": bot_response})

    # --- تسجيل البيانات تلقائياً ---
    status = log_to_sheets(prompt, bot_response)
    st.sidebar.success(f"حالة الحفظ: {status}")
