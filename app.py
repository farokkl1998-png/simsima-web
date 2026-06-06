import streamlit as st
import requests
import base64

# إعدادات الصفحة
st.set_page_config(page_title="سمسمة: صديقة أحلام", page_icon="🌸")

st.title("🌸 سمسمة: صديقة أحلام")

# إعداد المفاتيح (يجب إضافتها في Streamlit Secrets)
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
HF_TOKEN = st.secrets["HF_TOKEN"]

# دالة تحليل الصورة باستخدام Hugging Face
def analyze_image(image_bytes):
    API_URL = "https://api-inference.huggingface.co/models/Salesforce/blip-image-captioning-large"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    response = requests.post(API_URL, headers=headers, data=image_bytes)
    if response.status_code == 200:
        return response.json()[0]['generated_text']
    return None

# دالة الرد من Groq (نصي فقط - لضمان الاستقرار)
def get_groq_response(prompt):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": prompt}]
    }
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content']
    return "عذراً، لم أستطع فهم الصورة."

# واجهة المستخدم
uploaded_file = st.file_uploader("ارفعي صورة يا أحلام...", type=["jpg", "jpeg", "png"])
user_text = st.chat_input("اكتبي لسمسمة...")

if uploaded_file:
    st.image(uploaded_file)
    with st.spinner("سمسمة تقرأ الصورة..."):
        image_bytes = uploaded_file.getvalue()
        caption = analyze_image(image_bytes)
        
        if caption:
            prompt = f"الصورة تحتوي على: {caption}. المستخدم يقول: {user_text or 'ما رأيك في هذه الصورة؟'}"
            response = get_groq_response(prompt)
            st.write("سمسمة تقول:", response)
        else:
            st.error("تعذر تحليل الصورة.")
