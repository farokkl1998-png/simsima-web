import streamlit as st
import base64
from groq import Groq  # استيراد المكتبة الرسمية والآمنة لكروك

# إعدادات الصفحة والواجهة
st.set_page_config(page_title="سمسمة: صديقة أحلام", page_icon="🌸", layout="centered")
st.title("🌸 سمسمة: صديقة أحلام")

# تهيئة العميل الرسمي باستخدام المفتاح السري بأمان
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# إدارة الجلسة وتاريخ المحادثة
if "messages" not in st.session_state:
    st.session_state.messages = []

# عرض الرسائل السابقة على الشاشة
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if isinstance(msg["content"], list):
            text_content = next((item["text"] for item in msg["content"] if item["type"] == "text"), "")
            st.markdown(text_content)
        else:
            st.markdown(msg["content"])

# مدخلات الواجهة (الصورة والنص)
uploaded_file = st.file_uploader("ارفعي صورة يا أحلام...", type=["jpg", "png", "jpeg"])
user_query = st.chat_input("اكتبي لسمسمة...")

if user_query:
    # 1. صياغة محتوى رسالة المستخدم بناءً على وجود صورة أو عدمها
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

    # حفظ رسالة المستخدم الحالية في ذاكرة الجلسة
    st.session_state.messages.append({"role": "user", "content": user_content})

    # 2. إرسال الطلب عبر المكتبة الرسمية لضمان عدم حدوث أخطاء الـ HTTP
    with st.chat_message("assistant"):
        with st.spinner("سمسمة تفكر..."):
            try:
                # التوجيه الأساسي للشخصية مدمج بذكاء لحماية شروط موديلات الرؤية
                system_prompt = "أنتِ سمسمة، الصديقة المقربة لأحلام. كوني عقلانية ولطيفة وتحدثي بالعامية أو الفصحى اللطيفة حسب أسلوبها. أجيبي على ما يلي: "
                
                # إعداد قائمة الرسائل النهائية لإرسالها للمكتبة
                final_payload_messages = []
                for i, msg in enumerate(st.session_state.messages):
                    if isinstance(msg["content"], list):
                        if i == 0 and msg["role"] == "user":
                            # حقن الهوية في الرسالة الأولى إذا احتوت على صورة
                            injected = []
                            for item in msg["content"]:
                                if item["type"] == "text":
                                    injected.append({"type": "text", "text": system_prompt + item["text"]})
                                else:
                                    injected.append(item)
                            final_payload_messages.append({"role": msg["role"], "content": injected})
                        else:
                            final_payload_messages.append({"role": msg["role"], "content": msg["content"]})
                    else:
                        # حقن الهوية في الرسالة النصية العادية الأولى
                        text_val = system_prompt + msg["content"] if i == 0 and msg["role"] == "user" else msg["content"]
                        final_payload_messages.append({
                            "role": msg["role"],
                            "content": [{"type": "text", "text": text_val}]
                        })

                # استدعاء السيرفر من خلال عميل Groq الرسمي
                chat_completion = client.chat.completions.create(
                    model="llama-3.2-11b-vision-preview",
                    messages=final_payload_messages,
                    temperature=0.5
                )
                
                # استخراج الرد وعرضه
                response = chat_completion.choices[0].message.content
                st.markdown(response)
                
                # حفظ رد المساعد في ذاكرة الجلسة
                st.session_state.messages.append({"role": "assistant", "content": response})

            except Exception as e:
                st.error(f"⚠️ واجهت سمسمة مشكلة أثناء معالجة الطلب: {e}")
            
    st.session_state.messages.append({"role": "assistant", "content": response})
