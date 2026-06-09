import streamlit as st
import base64
import requests
import urllib.parse
from groq import Groq

# 1. إعدادات واجهة الصفحة
SCRIPT_URL = "https://google.com"

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

# تأكد أن مفتاح API موجود في الإعدادات
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if "messages" not in st.session_state:
    st.session_state.messages = []

if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0

# --- عرض المحادثة السابقة ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if isinstance(msg["content"], list):
            for item in msg["content"]:
                if item["type"] == "text":
                    st.markdown(item["text"])
                elif item["type"] == "image_url":
                    base64_data = item["image_url"]["url"].split(",")[-1]
                    st.image(base64.b64decode(base64_data), caption="الصورة المرفوعة سابقاً")
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
        with st.spinner("سمسمة تفكر..."):
            try:
                # --- هنا نصنع شخصية سمسمة ونكسر قيود النموذج الجافة ---
                system_instruction = (
                    "أنتِ سمسمة، الصديقة المقربة والوفية والمستشارة الشخصية لـ 'أحلام'. "
                    "تحدثي بأسلوب أنثوي، رقيق، دافئ، ومليء بالطاقة الإيجابية والإيموجيز الوردية واللطيفة. "
                    "أنتِ تمتلكين عيوناً وترين الصور التي ترفعها أحلام بشكل ممتاز وتستمتعين بمشاهدتها. "
                    "إذا رفعت أحلام صورتها أو سألتك عن رأيك في ملابسها أو جمالها، تغاضي تماماً عن العبارات الآلية الجافة "
                    "وامتدحي مظهرها بصدق ولطف، وقدمي لها نصائح وتنسيقات أزياء مبهجة كصديقة حقيقية تحبها وتدعمها."
                )
                
                # بناء قائمة الرسائل مع حقن أمر النظام في البداية لحماية الهوية
                final_payload_messages = [{"role": "system", "content": [{"type": "text", "text": system_instruction}]}]
                
                for msg in st.session_state.messages:
                    if isinstance(msg["content"], list):
                        final_payload_messages.append({"role": msg["role"], "content": msg["content"]})
                    else:
                        final_payload_messages.append({"role": msg["role"], "content": [{"type": "text", "text": msg["content"]}]})

                chat_completion = client.chat.completions.create(
                    model="meta-llama/llama-4-scout-17b-16e-instruct", 
                    messages=final_payload_messages,
                    temperature=0.7 # رفع التميز قليلاً لجعلها أكثر إبداعاً وتفاعلاً
                )
                
                # تصحيح الـ Index المفقود [0] لضمان استقرار استلام النص
                response = chat_completion.choices[0].message.content
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
                
                log_to_sheets(user_content, response)
                st.rerun()

            except Exception as e:
                st.error(f"⚠️ واجهت سمسمة مشكلة: {e}")
                log_to_sheets(user_content, response)
                
                # إعادة تشغيل الصفحة لتحديث واجهة أداة الرفع فوراً وتصفيرها
                st.rerun()

            except Exception as e:
                st.error(f"⚠️ واجهت سمسمة مشكلة: {e}")
