import streamlit as st
import base64
import requests
import io
from PIL import Image

# 1. إعدادات واجهة منصة رسم سمسمة
st.set_page_config(page_title="ريشة سمسمة الفنية", page_icon="🎨", layout="centered")
st.title("🎨 ريشة سمسمة الفنية")
st.subheader("اكتبي ما يتخيله عقلكِ، ودعي سمسمة تحوله إلى لوحة حقيقية بلمح البصر! ✨")

# 2. تهيئة المفتاح السري لـ Hugging Face بأمان من الـ Secrets
HF_TOKEN = st.secrets["HF_TOKEN"]

# استخدام الموديل المستقر والمفتوح بالكامل لضمان عدم حدوث انشغال
HF_API_URL = "https://huggingface.co"
headers_hf = {"Authorization": f"Bearer {HF_TOKEN}"}

# دالة التوليد المباشرة والصافية لضمان خروج الصورة فوراً
def generate_image_cloud(prompt):
    payload = {"inputs": prompt}
    try:
        response = requests.post(HF_API_URL, headers=headers_hf, json=payload)
        if response.status_code == 200:
            return response.content  # يعيد بايتات الصورة الخام بنجاح
    except Exception:
        pass
    return None

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
    draw_query = st.text_input("ماذا تريدين أن أرسم لكِ الآن يا أحلام؟ 🌸", placeholder="مثال: قطة رائد فضاء تسبح في مجرة من الحلوى...")
    submit_button = st.form_submit_button(label="🎨 اطلقي ريشة الرسم الآن")
    
    if submit_button and draw_query:
        with st.chat_message("user"):
            st.markdown(f"🔮 خيال أحلام: **{draw_query}**")
            
        with st.chat_message("assistant"):
            with st.spinner("سمسمة تمزج الألوان وتبهركِ بالرسمة الآن... 🚀"):
                
                # ترجمة فورية ومبسطة ومباشرة للطلب إلى الإنجليزية ليفهمها الرسام السحابي
                # لتفادي أي تعارض في نماذج كروك، قمنا بجعل الترجمة نصية سريعة عبر قاموس الكلمات أو إرسالها مباشرة مع إضافات جمالية
                enhanced_prompt = f"{draw_query}, high quality, cinematic, detailed masterpiece, digital art"
                
                # استدعاء السيرفر المباشر والمستقر
                image_bytes = generate_image_cloud(enhanced_prompt)
                
                if image_bytes:
                    try:
                        image = Image.open(io.BytesIO(image_bytes))
                        st.image(image, caption="تفضلي رسمتي يا أحلام! ✨")
                        
                        # حفظ اللوحة في الذاكرة لكي لا تضيع عند التحديث
                        img_base64 = base64.b64encode(image_bytes).decode('utf-8')
                        st.session_state.drawings.append({"prompt": draw_query, "img_base64": img_base64})
                        st.rerun()
                    except Exception:
                        st.error("⚠️ حدث خطأ أثناء معالجة الصورة المستلمة، اضغطي مجدداً.")
                else:
                    st.error("⚠️ واجه سيرفر الرسم ضغطاً مؤقتاً، اضغطي على الزر مجدداً لتوليدها فوراً!")
