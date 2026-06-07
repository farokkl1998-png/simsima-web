import streamlit as st
import requests
import base64

# إعدادات الصفحة
st.set_page_config(page_title="سمسمة: صديقة أحلام", page_icon="🌸", layout="centered")

st.title("🌸 سمسمة: صديقة أحلام")

# المفاتيح
API_KEY = st.secrets["GROQ_API_KEY"]
GROQ_URL = "https://groq.com"

# دالة إرسال الطلب (موحدة بالكامل لتجنب خطأ 400)
def get_ai_response(messages_history):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    # بناء هيكل الرسائل المتوافق تماماً مع نماذج الرؤية في Groq
    payload_messages = [
        {
            "role": "system", 
            "content": [{"type": "text", "text": "أنتِ سمسمة، الصديقة المقربة لأحلام. كوني عقلانية ولطيفة وتحدثي بالعامية أو الفصحى اللطيفة حسب أسلوبها."}]
        }
    ]
    
    # تحويل كافة الرسائل السابقة والحالية إلى صيغة الـ List المنظمة للرؤية
    for msg in messages_history:
        if isinstance(msg["content"], list):
            # إذا كانت الرسالة مهيأة مسبقاً كقائمة (نص وصورة)
            payload_messages.append({"role": msg["role"], "content": msg["content"]})
        else:
            # إذا كانت نصاً عادياً، نحولها إلى صيغة الكائن المتوافقة مع موديلات الرؤية
            payload_messages.append({
                "role": msg["role"],
                "content": [{"type": "text", "text": msg["content"]}]
            })

    payload = {
        "model": "llama-3.2-11b-vision-preview",
        "messages": payload_messages,
        "temperature": 0.5
    }

    try:
        response = requests.post(GROQ_URL, headers=headers, json=payload)
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            # إظهار تفاصيل الخطأ القادمة من كروك للمساعدة في تشخيصه إن وجد
            error_details = response.json().get('error', {}).get('message', 'خطأ غير معروف')
            return f"عذراً يا أحلام، حدث خطأ في السيرفر (رمز {response.status_code}): {error_details}"
    except Exception as e:
        return f"حدث خطأ أثناء الاتصال: {e}"

if "messages" not in st.session_state:
    st.session_state.messages = []

# عرض المحادثة السابقة بشكل مقروء للمستخدم
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if isinstance(msg["content"], list):
            # استخراج النص من القائمة لعرضه في واجهة شات ستريمليت
            text_content = next((item["text"] for item in msg["content"] if item["type"] == "text"), "")
            st.markdown(text_content)
        else:
            st.markdown(msg["content"])

# المدخلات (استقبال الصور والنصوص)
uploaded_file = st.file_uploader("ارفعي صورة يا أحلام...", type=["jpg", "png", "jpeg"])
user_query = st.chat_input("اكتبي لسمسمة...")

if user_query:
    # 1. بناء محتوى رسالة المستخدم الحالية
    if uploaded_file:
        image_base64 = base64.b64encode(uploaded_file.getvalue()).decode('utf-8')
        user_content = [
            {"type": "text", "text": user_query},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
        ]
        # عرض الصورة والنص للمستخدم فوراً في الواجهة
        with st.chat_message("user"):
            st.image(uploaded_file, caption="الصورة المرفوعة")
            st.markdown(user_query)
    else:
        user_content = user_query
        with st.chat_message("user"):
            st.markdown(user_query)

    # حفظ رسالة المستخدم في الجلسة
    st.session_state.messages.append({"role": "user", "content": user_content})

    # 2. جلب رد سمسمة من السيرفر وعرضه
    with st.chat_message("assistant"):
        with st.spinner("سمسمة تفكر..."):
            response = get_ai_response(st.session_state.messages)
            st.markdown(response)
            
    # حفظ رد سمسمة في الجلسة كصيغة نصية عادية
    st.session_state.messages.append({"role": "assistant", "content": response})
