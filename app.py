import streamlit as st
import base64
import requests
import io
import time  # استيراد مكتبة الوقت لإدارة فترات الانتظار الذكية
from PIL import Image
import translators as ts

# 1. إعدادات واجهة منصة رسم سمسمة
st.set_page_config(page_title="ريشة سمسمة الفنية", page_icon="🎨", layout="centered")
st.title("🎨 ريشة سمسمة الفنية")
st.subheader("اكتبي ما يتخيله عقلكِ، ودعي سمسمة تحوله إلى لوحة حقيقية بلمح البصر! ✨")

# 2. تهيئة المفتاح السري لـ Hugging Face بأمان من الـ Secrets
HF_TOKEN = st.secrets["HF_TOKEN"]

# استخدام الموديل المستقر والمفتوح بالكامل لضمان عدم حدوث انشغال
HF_API_URL = "https://huggingface.co"
headers_hf = {"Authorization": f"Bearer {HF_TOKEN}"}

# دالة التوليد المفتوحة والمطورة بنظام الحلقات الذكية (Retry Loop)
def generate_image_cloud(prompt):
    payload = {"inputs": prompt}
    
    # محاولة إرسال الطلب 5 مرات متتالية تلقائياً في الخلفية عند وجود ضغط
    for attempt in range(5):
        try:
            response = requests.post(HF_API_URL, headers=headers_hf, json=payload)
            if response.status_code == 200:
                return response.content  # نجاح جلب بايتات الصورة
            elif response.status_code == 503:
                # كود 503 يعني أن الموديل يحمل في السيرفر حالياً، ننتظر ثانيتين ونعيد المحاولة
                time.sleep(2)
            else:
                time.sleep(1)
        except Exception:
            time.sleep(1)
            
    return None  # يعود بفشل فقط إذا استنفذ كافة المحاولات الخمسة

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
    draw_query = st.text_input("ماذا تريدين أن أرسم لكِ الآن يا أحلام؟ 🌸", placeholder="مثال: قطة صغيرة تمسك وردة حمراء...")
    submit_button = st.form_submit_button(label="🎨 اطلقي ريشة الرسم الآن")
    
    if submit_button and draw_query:
        with st.chat_message("user"):
            st.markdown(f"🔮 خيال أحلام: **{draw_query}**")
            
        with st.chat_message("assistant"):
            with st.spinner("سمسمة تترجم خيالكِ وتمسك الألوان الآن... 🚀"):
                
                try:
                    # ترجمة فورية وتلقائية من العربية إلى الإنجليزية ليفهمها الرسام السحابي
                    english_prompt = ts.translate_text(draw_query, from_language='ar', to_language='en')
                    full_prompt = f"{english_prompt}, high quality, cinematic, detailed masterpiece, digital art"
                except Exception:
                    full_prompt = draw_query

                # استدعاء السيرفر المطور بنظام الحلقات المقاوم للضغط والمفتاح الجديد
                image_bytes = generate_image_cloud(full_prompt)
                
                if image_bytes:
                    try:
                        image = Image.open(io.BytesIO(image_bytes))
                        st.image(image, caption="تفضلي رسمتي يا أحلام! ✨")
                        
                        img_base64 = base64.b64encode(image_bytes).decode('utf-8')
                        st.session_state.drawings.append({"prompt": draw_query, "img_base64": img_base64})
                        st.rerun()
                    except Exception:
                        st.error("⚠️ حدث خطأ أثناء معالجة الصورة، اضغطي مجدداً.")
                else:
                    st.error("⚠️ خوادم الرسم العامة مزدحمة جداً في هذه اللحظة، اضغطي على زر الإطلاق مجدداً لتخطي الطابور!")
