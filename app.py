import streamlit as st
import google.generativeai as genai

# إعداد مفتاح API السري من Streamlit
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

st.title("🌸 سمسمة: بئر أسرارك")

# التوجيه الأساسي لتهدئة مشاعر سمسمة وجعلها متزنة
system_prompt = (
    "أنتِ سمسمة، بئر أسرار ذكي ومستمع جيد. ردودكِ يجب أن تكون هادئة، قصيرة، ومتزنة. "
    "تجنبي المبالغة في التعبير عن المشاعر أو تكرار عبارات الفرح وتلألؤ الأعين بشكل مفرط. "
    "كوني صديقة عقلانية ودبلوماسية وتحدثي بلهجة ودية بسيطة."
)

# تهيئة ذاكرة الجلسة للمحادثات
if "messages" not in st.session_state:
    st.session_state.messages = []

# عرض الرسائل السابقة في الواجهة
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# استقبال رسائل المستخدم الجديدة
if prompt := st.chat_input("...اكتب هنا"):
    # عرض رسالة المستخدم فوراً
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # إعداد الموديل مع التوجيه السلوكي الجديد
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        system_instruction=system_prompt
    )

    # تجهيز التاريخ المتوافق مع الموديل بدون تعقيد
    history = []
    for m in st.session_state.messages[:-1]:
        history.append({
            "role": "user" if m["role"] == "user" else "model",
            "parts": [m["content"]]
        })

    # بدء الدردشة وجلب الرد
    chat = model.start_chat(history=history)
    
    with st.chat_message("assistant"):
        response = chat.send_message(prompt)
        st.markdown(response.text)
        
    st.session_state.messages.append({"role": "assistant", "content": response.text})
