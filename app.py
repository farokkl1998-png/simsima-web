import streamlit as st
import base64
from groq import Groq  # المكتبة الرسمية لـ Groq

# 1. إعدادات واجهة الصفحة بالكامل لتناسب الهواتف
st.set_page_config(page_title="سمسمة: صديقة أحلام", page_icon="🌸", layout="centered")
st.title("🌸 سمسمة: صديقة أحلام")

# 2. تهيئة العميل البرمجي باستخدام المفتاح السري بأمان
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# 3. إدارة جلسة الذاكرة وتاريخ المحادثة
if "messages" not in st.session_state:
    st.session_state.messages = []

# ميزة سحرية لتخزين حالة الصورة ومنع تكرارها برمجياً
if "current_image" not in st.session_state:
    st.session_state.current_image = None

# 4. عرض المحادثات السابقة المخرنة على الشاشة للمستخدم بشكل نظيف جداً
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if isinstance(msg["content"], list):
            # استخراج النص وعرضه فقط لكي لا تتكرر الصور القديمة في الواجهة
            text_content = next((item["text"] for item in msg["content"] if item["type"] == "text"), "")
            st.markdown(text_content)
        else:
            st.markdown(msg["content"])

# 5. الواجهة الاحترافية الجديدة لإرفاق الصور (تم تصغيرها ونقلها للأسفل لحفظ مساحة الهاتف)
st.markdown("---")
uploaded_file = st.file_uploader("📎 اضغطي هنا لإرفاق صورة لسمسمة...", type=["jpg", "png", "jpeg"], label_visibility="collapsed")

# 6. صندوق الشات الرئيسي للكتابة والإرسال
user_query = st.chat_input("اكتبي لسمسمة هنا...")

if user_query:
    # التحقق مما إذا كانت هناك صورة مرفوعة جديدة لم تُعالج بعد
    if uploaded_file and st.session_state.current_image != uploaded_file.name:
        image_base64 = base64.b64encode(uploaded_file.getvalue()).decode('utf-8')
        user_content = [
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}},
            {"type": "text", "text": user_query}
        ]
        with st.chat_message("user"):
            st.image(uploaded_file, caption="الصورة المرسلة 📸", width=250)
            st.markdown(user_query)
            
        # حفظ اسم الصورة الحالية في الذاكرة لمنع إعادة إرسالها تلقائياً في المرة القادمة
        st.session_state.current_image = uploaded_file.name
    else:
        # شات نصي عادي إذا لم تكن هناك صورة جديدة
        user_content = user_query
        with st.chat_message("user"):
            st.markdown(user_query)

    # حفظ مدخلات المستخدم في الذاكرة الحالية للجلسة
    st.session_state.messages.append({"role": "user", "content": user_content})

    # 7. استدعاء معالجة الذكاء الاصطناعي وعرض رد المساعد
    with st.chat_message("assistant"):
        with st.spinner("سمسمة تفكر..."):
            try:
                system_prompt = "أنتِ سمسمة، الصديقة المقربة لأحلام. كوني عقلانية ولطيفة وتحدثي بالعامية أو الفصحى اللطيفة حسب أسلوبها. أجيبي على ما يلي: "
                
                # بناء هيكلية مصفوفة الرسائل المخصصة المعتمدة لدى كروك لضمان الرؤية
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

                # طلب التوليد من نموذج الرؤية والمحادثة المحدث والمعتمد Llama 4
                chat_completion = client.chat.completions.create(
                    model="meta-llama/llama-4-scout-17b-16e-instruct", 
                    messages=final_payload_messages,
                    temperature=0.5
                )
                
                response = chat_completion.choices.message.content
                st.markdown(response)
                
                # حفظ رد المساعد في الجلسة لمتابعة سياق الحديث
                st.session_state.messages.append({"role": "assistant", "content": response})
                
                # تصفير حالة الصورة تماماً بعد رد سمسمة الناجح لمنع التكرار في الرسائل القادمة
                st.session_state.current_image = None
                st.rerun()

            except Exception as e:
                st.error(f"⚠️ واجهت سمسمة مشكلة أثناء معالجة الطلب: {e}")
