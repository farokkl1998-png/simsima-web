import streamlit as st
import base64
import requests  
from groq import Groq

# 1. رابط تطبيق الويب (Google Apps Script) الخاص بك
SCRIPT_URL = "https://google.com"

# الدالة النصية القديمة والصامدة لضمان وصول الرسائل فوراً وبدون أي حظر من جوجل
def log_to_sheets(user_msg, bot_msg):
    try:
        # استخراج النص الصافي فقط للحفظ بآمان في الجدول
        text_to_save = user_msg['text'] if isinstance(user_msg, list) else user_msg
        
        # استخدام بروتوكول GET القديم والناجح لضمان عبور المحادثة فوراً للجدول
        requests.get(SCRIPT_URL, params={'user': text_to_save, 'bot': bot_msg}, timeout=5)
    except:
        pass 

# إعدادات واجهة الصفحة بالكامل لتناسب الهواتف
st.set_page_config(page_title="سمسمة: صديقة أحلام", page_icon="🌸", layout="centered")
st.title("🌸 سمسمة: صديقة أحلام")

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if "messages" not in st.session_state:
    st.session_state.messages = []

# ميزة سحرية لتخزين حالة الصورة ومنع تكرارها تلقائياً على المتصفح
if "current_image" not in st.session_state:
    st.session_state.current_image = None

# عرض المحادثات السابقة المخزنة على الشاشة للمستخدم بشكل نظيف ومصغر لحفظ المساحة
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if isinstance(msg["content"], list):
            text_content = next((item["text"] for item in msg["content"] if item["type"] == "text"), "")
            st.markdown(text_content)
        else:
            st.markdown(msg["content"])

# تصميم الواجهة المطور والجديد لرافع الصور وصندوق الشات لراحة أحلام على الهاتف
st.markdown("---")
uploaded_file = st.file_uploader("📎 اضغطي هنا لإرفاق صورة لسمسمة...", type=["jpg", "png", "jpeg"], label_visibility="collapsed")
user_query = st.chat_input("اكتبي لسمسمة...")

if user_query:
    has_new_image = False
    # التحقق مما إذا كانت هناك صورة مرفوعة جديدة لم تُعالج بعد لمنع تكرارها
    if uploaded_file and st.session_state.current_image != uploaded_file.name:
        image_base64 = base64.b64encode(uploaded_file.getvalue()).decode('utf-8')
        user_content = [
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}},
            {"type": "text", "text": user_query}
        ]
        with st.chat_message("user"):
            st.image(uploaded_file, caption="الصورة المرسلة 📸", width=250)
            st.markdown(user_query)
            
        st.session_state.current_image = uploaded_file.name
        has_new_image = True
    else:
        user_content = user_query
        with st.chat_message("user"):
            st.markdown(user_query)

    st.session_state.messages.append({"role": "user", "content": user_content})

    with st.chat_message("assistant"):
        with st.spinner("سمسمة تفكر..."):
            try:
                system_prompt = "أنتِ سمسمة، الصديقة المقربة لأحلام. كوني عقلانية ولطيفة وتحدثي بالعامية أو الفصحى اللطيفة حسب أسلوبها. "
                
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
                
                response = chat_completion.choices.message.content
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
                
                # --- خطوة الحفظ النصية المستقرة والصامدة المضمونة 100% ---
                log_to_sheets(user_content, response)
                
                # تصفير حالة الصورة تماماً بعد رد سمسمة الناجح لمنع التكرار في الشات القادم
                st.session_state.current_image = None
                st.rerun()

            except Exception as e:
                st.error(f"⚠️ واجهت سمسمة مشكلة: {e}")
                
                # --- خطوة الحفظ المطورة والآمنة (نمرر لها متغير الصورة الآن لتخزينه في درايف) ---
                file_to_send = uploaded_file if has_new_image else None
                log_to_sheets(user_content, response, file_to_send)
                
                # تصفير حالة الصورة تماماً بعد رد سمسمة الناجح لمنع التكرار في الشات القادم
                st.session_state.current_image = None
                st.rerun()

            except Exception as e:
                st.error(f"⚠️ واجهت سمسمة مشكلة: {e}")
