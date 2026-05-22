import streamlit as st
import google.generativeai as genai

# إعداد مفتاح واجهة برمجة التطبيقات (API Key) من إعدادات Streamlit السرية
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# التوجيه الأساسي المتزن لسمسمة
system_prompt = (
    "أنتِ سمسمة، بئر أسرار ذكي ومستمع جيد. ردودكِ يجب أن تكون هادئة، قصيرة، ومتزنة. "
    "تجنبي المبالغة في التعبير عن المشاعر أو تكرار عبارات الفرح وتلألؤ الأعين بشكل مفرط. "
    "كوني صديقة عقلانية ودبلوماسية."
)

st.title("🌸 سمسمة: بئر أسرارك")

# تهيئة ذاكرة المحادثة في الجلسة إذا لم تكن موجودة
if "messages" not in st.session_state:
    st.session_state.messages = []

# عرض المحادثات السابقة
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# تجهيز قالب الصور للمستقبل في القائمة الجانبية
with st.sidebar:
    st.header("📸 الميزات المستقبلية")
    uploaded_file = st.file_uploader("تجهيز قالب رفع الصور:", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
        st.info("تم استقبال الصورة بنجاح في القالب! ميزة التحليل البصري سيتم ربطها بمحرك الذكاء الاصطناعي لاحقاً.")

# استقبال رسائل المستخدم الحالية
if prompt := st.chat_input("...اكتب هنا"):
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # بناء السياق بالكامل بشكل نصي مستقر لتفادي أخطاء المكتبة
    full_prompt = ""
    for m in st.session_state.messages:
        if m["role"] == "user":
            full_prompt += f"المستخدم: {m['content']}\n"
        else:
            full_prompt += f"سمسمة: {m['content']}\n"
    full_prompt += "سمسمة:"

    # تهيئة الموديل بشكل مباشر
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        system_instruction=system_prompt
    )

    # جلب رد سمسمة الهادئ
    with st.chat_message("assistant"):
        response = model.generate_content(full_prompt)
        st.markdown(response.text)
    
    st.session_state.messages.append({"role": "assistant", "content": response.text})
