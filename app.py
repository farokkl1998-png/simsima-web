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

    # تهيئة دردشة جديدة مع التوجيه والنظام المستقر
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        system_instruction=system_prompt
    )
    
    # تحويل التاريخ إلى صيغة متوافقة تماماً ومستقرة
    chat = model.start_chat(history=[])
    for m in st.session_state.messages[:-1]:
        chat.history.append({
            "role": "user" if m["role"] == "user" else "model",
            "parts": [m["content"]]
        })

    # جلب رد سمسمة الهادئ
    with st.chat_message("assistant"):
        response = chat.send_message(prompt)
        st.markdown(response.text)
    
    st.session_state.messages.append({"role": "assistant", "content": response.text})
