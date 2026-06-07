import streamlit as st
import requests
import base64

# إعدادات الصفحة
st.set_page_config(page_title="سمسمة: صديقة أحلام", page_icon="🌸", layout="centered")

st.title("🌸 سمسمة: صديقة أحلام")

# جلب المفتاح السري بأمان
API_KEY = st.secrets["GROQ_API_KEY"]
GROQ_URL = "https://groq.com"

# دالة إرسال الطلب بعد التعديل الجذري
def get_ai_response(messages_history):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    # التوجيه الأساسي (تم دمج شخصية سمسمة هنا بدلاً من خيار الـ system المرفوض)
    system_instruction = "أنتِ سمسمة، الصديقة المقربة لأحلام. كوني عقلانية ولطيفة وتحدثي بالعامية أو الفصحى اللطيفة حسب أسلوبها. أجيبي على ما يلي: "
    
    payload_messages = []
    
    # تحويل كافة الرسائل لتبدو مهيأة تماماً لشروط Groq
    for i, msg in enumerate(messages_history):
        if isinstance(msg["content"], list):
            # إذا كانت هذه أول رسالة مستخدم وبها صورة، ندمج التعليمات بداخل النص
            if i == 0 and msg["role"] == "user":
                updated_content = []
                for item in msg["content"]:
                    if item["type"] == "text":
                        updated_content.append({"type": "text", "text": system_instruction + item["text"]})
                    else:
                        updated_content.append(item)
                payload_messages.append({"role": msg["role"], "content": updated_content})
            else:
                payload_messages.append({"role": msg["role"], "content": msg["content"]})
        else:
            # معالجة النصوص العادية بدون صور
            text_to_send = system_instruction + msg["content"] if i == 0 and msg["role"] == "user" else msg["content"]
            payload_messages.append({
                "role": msg["role"],
                "content": [{"type": "text", "text": text_to_send}]
            })

    payload = {
        "model": "llama-3.2-11b-vision-preview",
        "messages": payload_messages,
        "temperature": 0.5
    }

    try:
        response = requests.post(GROQ_URL, headers=headers, json=payload)
        
        # حماية إضافية: التحقق من كود الاستجابة قبل محاولة قراءة الـ JSON
        if response.status_code == 200:
            return response.json()['choices']['message']['content']
        else:
            # إذا أرجع السيرفر خطأ، سنعرض نص الخطأ الخام لنعرف السبب فوراً
            return f"⚠️ خطأ من سيرفر كروك (رمز {response.status_code}): {response.text}"
            
    except Exception as e:
        return f"حدث خطأ أثناء الاتصال بالشبكة: {e}"

# إدارة الجلسة والمحادثة
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if isinstance(msg["content"], list):
            text_content = next((item["text"] for item in msg["content"] if item["type"] == "text"), "")
            st.markdown(text_content)
        else:
            st.markdown(msg["content"])

# استقبال الملفات والنصوص من الواجهة
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
            response = get_ai_response(st.session_state.messages)
            st.markdown(response)
            
    st.session_state.messages.append({"role": "assistant", "content": response})
