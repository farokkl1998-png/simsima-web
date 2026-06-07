import streamlit as st
import base64
from groq import Groq  # استيراد المكتبة الرسمية والآمنة لـ Groq

# 1. إعدادات واجهة الصفحة بالكامل
st.set_page_config(page_title="سمسمة: صديقة أحلام", page_icon="🌸", layout="centered")
st.title("🌸 سمسمة: صديقة أحلام")

# 2. تهيئة العميل البرمجي باستخدام المفتاح السري بأمان من إعدادات Streamlit
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# 3. إدارة جلسة الذاكرة وتاريخ المحادثة
if "messages" not in st.session_state:
    st.session_state.messages = []

# 4. عرض المحادثات السابقة المخرنة على الشاشة للمستخدم
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if isinstance(msg["content"], list):
            text_content = next((item["text"] for item in msg["content"] if item["type"] == "text"), "")
            st.markdown(text_content)
        else:
            st.markdown(msg["content"])

# 5. عناصر واجهة الاستلام (رفع الصور وصندوق المدخلات)
uploaded_file = st.file_uploader("ارفعي صورة يا أحلام...", type=["jpg", "png", "jpeg"])
user_query = st.chat_input("اكتبي لسمسمة...")

if user_query:
    # صياغة محتوى رسالة المستخدم وتشفير الصورة إن وجدت بصيغة Base64
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

    # حفظ مدخلات المستخدم في الذاكرة الحالية للجلسة
    st.session_state.messages.append({"role": "user", "content": user_content})

    # 6. استدعاء معالجة الذكاء الاصطناعي وعرض رد المساعد
    with st.chat_message("assistant"):
        with st.spinner("سمسمة تفكر..."):
            try:
                # دمج توجيهات الشخصية لحماية توافق السيرفر مع موديلات الرؤية
                system_prompt = "أنتِ سمسمة، الصديقة المقربة لأحلام. كوني عقلانية ولطيفة وتحدثي بالعامية أو الفصحى اللطيفة حسب أسلوبها. أجيبي على ما يلي: "
                
                # بناء هيكلية مصفوفة الرسائل المخصصة المعتمدة لدى كروك
                final_payload_messages = []
                for i, msg in enumerate(st.session_state.messages):
                    if isinstance(msg["content"], list):
                        if i == 0 and msg["role"] == "user":
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
                        text_val = system_prompt + msg["content"] if i == 0 and msg["role"] == "user" else msg["content"]
                        final_payload_messages.append({
                            "role": msg["role"],
                            "content": [{"type": "text", "text": text_val}]
                        })

                # طلب التوليد من نموذج الرؤية والمحادثة المحدث والمعتمد بدلاً من القديم الموقوف
                chat_completion = client.chat.completions.create(
                    model="meta-llama/llama-4-scout-17b-16e-instruct", # النموذج المحدث بالكامل
                    messages=final_payload_messages,
                    temperature=0.5
                )
                
                # استخلاص النتيجة وعرضها
                response = chat_completion.choices.message.content
                st.markdown(response)
                
                # حفظ رد المساعد في الجلسة لمتابعة سياق الحديث
                st.session_state.messages.append({"role": "assistant", "content": response})

            except Exception as e:
                # إظهار رسالة خطأ واضحة للمطور في حال وجود مشاكل بالمفتاح أو الحصص
                st.error(f"⚠️ واجهت سمسمة مشكلة أثناء معالجة الطلب: {e}")
