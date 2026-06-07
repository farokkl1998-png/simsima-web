Import streamlit as st
import base64
import gspread
import json
from google.oauth2.service_account import Credentials
from groq import Groq

# 1. إعدادات الصفحة
st.set_page_config(page_title="سمسمة: صديقة أحلام", page_icon="🌸")
st.title("🌸 سمسمة: صديقة أحلام")

# 2. تهيئة العميل (Groq)
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def log_to_sheets(user_msg, bot_msg):
    try:
        # قراءة بيانات الاعتماد من Secrets
        creds_data = json.loads(st.secrets["GOOGLE_SHEETS_CREDENTIALS"])
        scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
        creds = Credentials.from_service_account_info(creds_data, scopes=scope)
        gc = gspread.authorize(creds)
        
        # --- [ملاحظة: هذا هو السطر الذي تحتاج لتعديله فقط] ---
        # استبدل الجملة التالية بـ اسم ملف الجدول الذي أنشأته في جوجل
        sheet_name = "simsima-bot" 
        # ----------------------------------------------------
        
        sh = gc.open(sheet_name).sheet1
        sh.append_row([user_msg, bot_msg])
    except Exception as e:
        st.error(f"⚠️ خطأ في الاتصال بالجدول: {e}")

# 3. إدارة الذاكرة
if "messages" not in st.session_state:
    st.session_state.messages = []

# 4. عرض الرسائل
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 5. منطقة الإدخال
user_query = st.chat_input("اكتبي لسمسمة...")

if user_query:
    with st.chat_message("user"):
        st.markdown(user_query)
    st.session_state.messages.append({"role": "user", "content": user_query})

    # 6. الرد من سمسمة
    with st.chat_message("assistant"):
        with st.spinner("سمسمة تفكر..."):
            try:
                chat_completion = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=st.session_state.messages,
                    temperature=0.7
                )
                response = chat_completion.choices[0].message.content
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
                
                # حفظ المحادثة في Google Sheets
                log_to_sheets(user_query, response)
                
            except Exception as e:
                st.error(f"خطأ في الرد: {e}") 
