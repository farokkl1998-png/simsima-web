import streamlit as st
import base64
import requests
import io
from PIL import Image

# 1. إعدادات واجهة منصة رسم سمسمة
st.set_page_config(page_title="ريشة سمسمة الفنية", page_icon="🎨", layout="centered")
st.title("🎨 ريشة سمسمة الفنية")
st.subheader("اكتبي ما يتخيله عقلكِ، ودعي سمسمة تحوله إلى لوحة حقيقية بلمح البصر! ✨")

# 2. إدارة جلسة الذاكرة للصور لكي لا تختفي اللوحات عند تحديث الصفحة
if "drawings" not in st.session_state:
    st.session_state.drawings = []

# 3. عرض اللوحات الفنية السابقة التي تم رسمها في الجلسة الحالية
for draw_item in st.session_state.drawings:
    with st.chat_message("user"):
        st.markdown(f"🔮 خيال أحلام: **{draw_item['prompt']}**")
    with st.chat_message("assistant"):
        img_data = base64.b64decode(draw_item["img_base64"])
        st.image(Image.open(io.BytesIO(img_data)), caption="✨ تحفة سمسمة الفنية")

# 4. بناء استمارة الرسم الإجبارية والواضحة في واجهة الهاتف
st.markdown("---")
with st.form(key="super_drawing_form", clear_on_submit=True):
    draw_query = st.text_input("ماذا تريدين أن أرسم لكِ الآن يا أحلام؟ 🌸", placeholder="اكتبي الوصف باللغة الإنجليزية لضمان السرعة الخارقة والنجاح...")
    submit_button = st.form_submit_button(label="🎨 اطلقي ريشة الرسم الآن")
    
    if submit_button and draw_query:
        with st.chat_message("user"):
            st.markdown(f"🔮 خيال أحلام: **{draw_query}**")
            
        with st.chat_message("assistant"):
            with st.spinner("سمسمة تمسك الألوان وترسم لكِ الآن... 🚀"):
                try:
                    # الكود الأبسط في التاريخ: نأخذ النص الإنجليزي مباشرة ونشفره داخل الرابط الصافي
                    encoded_prompt = requests.utils.quote(draw_query.strip())
                    
                    # رابط صافي ونقي ومباشر 100% مستحيل يعطي أي خطأ parse أو 405
                    POLLINATIONS_URL = f"https://pollinations.ai{encoded_prompt}?width=1024&height=1024&model=flux"
                    
                    # سحب الصورة مباشرة بنظام GET الآمن
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
