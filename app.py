import streamlit as st
import base64
import requests
import io
from PIL import Image
from groq import Groq

# 1. إعدادات واجهة منصة رسم سمسمة
st.set_page_config(page_title="ريشة سمسمة الفنية", page_icon="🎨", layout="centered")
st.title("🎨 ريشة سمسمة الفنية")
st.subheader("اكتبي ما يتخيله عقلكِ Network، ودعي سمسمة تحوله إلى لوحة حقيقية بلمح البصر! ✨")

# 2. تهيئة المفتاح السري لـ Groq بأمان (نستخدمه للترجمة فقط)
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
client = Groq(api_key=GROQ_API_KEY)

# 3. إدارة جلسة الذاكرة للصور لكي لا تختفي اللوحات عند تحديث الصفحة
if "drawings" not in st.session_state:
    st.session_state.drawings = []

# 4. عرض اللوحات الفنية السابقة التي تم رسمها في الجلسة الحالية
for draw_item in st.session_state.drawings:
    with st.chat_message("user"):
        st.markdown(f"🔮 خيال أحلام: **{draw_item['prompt']}**")
    with st.chat_message("assistant"):
        img_data = base64.b64decode(draw_item["img_base64"])
        st.image(Image.open(io.BytesIO(img_data)), caption="✨ تحفة سمسمة الفنية")

# 5. بناء استمارة الرسم الإجبارية والواضحة في واجهة الهاتف
st.markdown("---")
with st.form(key="super_drawing_form", clear_on_submit=True):
    draw_query = st.text_input("ماذا تريدين أن أرسم لكِ الآن يا أحلام؟ 🌸", placeholder="مثال: قطة صغيرة لطيفة تمسك وردة زرقاء...")
    submit_button = st.form_submit_button(label="🎨 اطلقي ريشة الرسم الآن")
    
    if submit_button and draw_query:
        # توثيق الطلب وعرض خيال أحلام على الشاشة
        with st.chat_message("user"):
            st.markdown(f"🔮 خيال أحلام: **{draw_query}**")
            
        with st.chat_message("assistant"):
            with st.spinner("سمسمة تمزج الألوان وتبهركِ بالرسمة الآن... 🚀"):
                try:
                    # الخطوة الأولى: نطلب من نموذج كروك ترجمة وتحسين الوصف إلى الإنجليزية بدقة عالية
                    translation_completion = client.chat.completions.create(
                        model="meta-llama/llama-4-scout-17b-16e-instruct",
                        messages=[{"role": "user", "content": f"Translate and enhance this prompt to English for an image generation model, make it cinematic and highly detailed. Output ONLY the final English prompt text, DO NOT include any website names, prefixes, or links: {draw_query}"}],
                        temperature=0.3
                    )
                    
                    # قراءة رد الترجمة الصافي
                    english_prompt = translation_completion.choices.message.content
                    
                    # تنظيف جذري وصارم للنص لتفادي خطأ Failed to parse نهائياً
                    english_prompt = english_prompt.replace('"', '').replace("'", "").strip()
                    if "pollinations.ai" in english_prompt.lower():
                        english_prompt = english_prompt.lower().replace("pollinations.ai", "").strip()
                    if english_prompt.startswith("/") or english_prompt.startswith(":"):
                        english_prompt = english_prompt[1:].strip()

                    # الخطوة الثانية: تشفير النص الآمن ودمجه في المسار النقي لموقع الرسم
                    encoded_prompt = requests.utils.quote(english_prompt)
                    POLLINATIONS_URL = f"https://pollinations.ai{encoded_prompt}?width=1024&height=1024&model=flux"
                    
                    # سحب الصورة مباشرة كملف آمن بنظام GET
                    img_response = requests.get(POLLINATIONS_URL)
                    
                    if img_response.status_code == 200:
                        image = Image.open(io.BytesIO(img_response.content))
                        st.image(image, caption="تفضلي رسمتي يا أحلام! ✨")
                        
                        # حفظ اللوحة في الذاكرة لكي لا تضيع عند التحديث
                        img_base64 = base64.b64encode(img_response.content).decode('utf-8')
                        st.session_state.drawings.append({"prompt": draw_query, "img_base64": img_base64})
                        st.rerun()
                    else:
                        st.error(f"⚠️ واجه سيرفر الرسم مشكلة مؤقتة (رمز {img_response.status_code})، اضغطي على الزر مجدداً.")
                            
                except Exception as e:
                    st.error(f"⚠️ واجهت سمسمة مشكلة تقنية أثناء معالجة الطلب: {e}")
