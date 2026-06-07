import streamlit as st
import base64
import requests
import io
from PIL import Image
from groq import Groq

# 1. إعدادات واجهة الصفحة بالكامل لتناسب سمسمة
st.set_page_config(page_title="سمسمة: صديقة أحلام", page_icon="🌸", layout="centered")
st.title("🌸 سمسمة: صديقة أحلام")

# 2. تهيئة المفاتيح السرية بأمان من إعدادات الـ Secrets في Streamlit
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
HF_TOKEN = st.secrets["HF_TOKEN"]

# تهيئة عميل كروك الرسمي لنصوص ورؤية الصور
client = Groq(api_key=GROQ_API_KEY)

# استخدام المحرك العالمي الأحدث والأسرع كلياً (FLUX.1-schnell) لضمان التوليد الفوري للملفات
HF_API_URL = "https://huggingface.co"
headers_hf = {"Authorization": f"Bearer {HF_TOKEN}"}

# دالة ذكية لتوليد الصور سحابياً عبر Hugging Face
def generate_image_cloud(prompt):
    payload = {"inputs": prompt}
    try:
        response = requests.post(HF_API_URL, headers=headers_hf, json=payload)
        if response.status_code == 200:
            return response.content
    except Exception:
        pass
    return None

# 3. إدارة جلسة الذاكرة المؤقتة وتاريخ المحادثة
if "messages" not in st.session_state:
    st.session_state.messages = []

# 4. عرض المحادثات السابقة المخزنة على الشاشة للمستخدم بطريقة متناسقة
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if isinstance(msg["content"], list):
            text_content = next((item["text"] for item in msg["content"] if item["type"] == "text"), "")
            st.markdown(text_content)
        elif isinstance(msg["content"], str) and msg["content"].startswith("IMAGE_BYTES:"):
            img_data = base64.b64decode(msg["content"].split("IMAGE_BYTES:")[1])
            st.image(Image.open(io.BytesIO(img_data)), caption="رسمة سمسمة 🎨")
        else:
            st.markdown(msg["content"])

# 5. عناصر واجهة الاستلام واضحة ومباشرة على شاشة الهاتف بدون قوائم جانبية مفقودة
st.markdown("---")
uploaded_file = st.file_uploader("📸 ارفعي صورة يا أحلام لتقرأها سمسمة...", type=["jpg", "png", "jpeg"])

# تقسيم المدخلات إلى تبويبين مريحين جداً للاستخدام على شاشات الهواتف
tab1, tab2 = st.tabs(["💬 شات ودردشة", "🎨 اطلبي رسمة"])

with tab1:
    user_query = st.chat_input("اكتبي لسمسمة للدردشة العادية...")
    if user_query:
        if uploaded_file:
            image_base64 = base64.b64encode(uploaded_file.getvalue()).decode('utf-8')
            user_content = [
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}},
                {"type": "text", "text": user_query}
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
                try:
                    sys_prompt = "أنتِ سمسمة، الصديقة المقربة لأحلام. كوني عقلانية ولطيفة وتحدثي بالعامية أو الفصحى اللطيفة حسب أسلوبها. أجيبي على ما يلي: "
                    
                    # بناء سريع ومسطح ومحمي كلياً من أخطاء المسافات لتاريخ رسائل كروك
                    payload_msgs = []
                    for i, m in enumerate(st.session_state.messages):
                        if isinstance(m["content"], str) and m["content"].startswith("IMAGE_BYTES:"):
                            continue
                        
                        if isinstance(m["content"], list):
                            payload_msgs.append({"role": m["role"], "content": m["content"]})
                        else:
                            payload_msgs.append({"role": m["role"], "content": [{"type": "text", "text": m["content"]}]})
                    
                    # حقن شخصية سمسمة بأمان في الرسالة الأخيرة
                    if payload_msgs and payload_msgs[-1]["role"] == "user":
                        for item in payload_msgs[-1]["content"]:
                            if item["type"] == "text":
                                item["text"] = sys_prompt + item["text"]

                    chat_completion = client.chat.completions.create(
                        model="meta-llama/llama-4-scout-17b-16e-instruct", 
                        messages=payload_msgs,
                        temperature=0.5
                    )
                    
                    response = chat_completion.choices.message.content
                    st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    st.rerun()
                except Exception as e:
                    st.error(f"⚠️ واجهت سمسمة مشكلة أثناء معالجة الطلب: {e}")

with tab2:
    with st.form(key="drawing_form", clear_on_submit=True):
        draw_query = st.text_input("ماذا تريدين أن أرسم لكِ يا أحلام؟ 🌸", placeholder="مثال: فتاة صغيرة تمسك قطة...")
        submit_button = st.form_submit_button(label="اضغطي هنا للرسم ✨")
        
        if submit_button and draw_query:
            with st.chat_message("user"):
                st.markdown(f"🎨 طلب رسم: {draw_query}")
            st.session_state.messages.append({"role": "user", "content": f"🎨 طلب رسم: {draw_query}"})

            with st.chat_message("assistant"):
                with st.spinner("سمسمة تمسك الألوان وترسم لكِ الآن... 🎨"):
                    try:
                        translation_completion = client.chat.completions.create(
                            model="meta-llama/llama-4-scout-17b-16e-instruct",
                            messages=[{"role": "user", "content": f"Translate and enhance this prompt to English for an image generation model, make it cinematic and highly detailed. Output ONLY the English prompt: {draw_query}"}],
                            temperature=0.3
                        )
                        english_prompt = translation_completion.choices.message.content
                    except Exception:
                        english_prompt = draw_query

                    image_bytes = generate_image_cloud(english_prompt)
                    
                    if image_bytes:
                        image = Image.open(io.BytesIO(image_bytes))
                        st.image(image, caption="تفضلي رسمتي يا أحلام! ✨")
                        
                        img_base64 = base64.b64encode(image_bytes).decode('utf-8')
                        st.session_state.messages.append({"role": "assistant", "content": f"IMAGE_BYTES:{img_base64}"})
                        st.rerun()
                    else:
                        st.error("⚠️ عذراً يا أحلام، يبدو أن سيرفر الرسم مشغول حالياً، حاولي مجدداً بعد ثوانٍ.")
