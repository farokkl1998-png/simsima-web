import streamlit as st
import base64
import requests
import io
from PIL import Image
from groq import Groq

# 1. إعدادات واجهة منصة رسم سمسمة
st.set_page_config(page_title="ريشة سمسمة الفنية", page_icon="🎨", layout="centered")
st.title("🎨 ريشة سمسمة الفنية")
st.subheader("اكتبي ما يتخيله عقلكِ، ودعي سمسمة تحوله إلى لوحة حقيقية بلمح البصر! ✨")

# 2. تهيئة المفتاح السري لـ Groq بأمان
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
    draw_query = st.text_input("ماذا تريدين أن أرسم لكِ الآن يا أحلام؟ 🌸", placeholder="مثال: قطة رائد فضاء تسبح في مجرة من الحلوى...")
    submit_button = st.form_submit_button(label="🎨 اطلقي ريشة الرسم الآن")
    
    if submit_button and draw_query:
        # توثيق الطلب وعرض خيال أحلام على الشاشة
        with st.chat_message("user"):
            st.markdown(f"🔮 خيال أحلام: **{draw_query}**")
            
        with st.chat_message("assistant"):
            with st.spinner("سمسمة تمزج الألوان وتبهركِ بالرسمة الآن... 🚀"):
                try:
                    # الخطوة السحرية بعد التصحيح: الترجمة المتوافقة 100% مع لاما 4
                    translation_completion = client.chat.completions.create(
                        model="meta-llama/llama-4-scout-17b-16e-instruct",
                        messages=[{"role": "user", "content": f"Translate and enhance this prompt to English for an image generation model, make it cinematic and highly detailed. Output ONLY the English prompt: {draw_query}"}],
                        temperature=0.3
                    )
                    
                    # قراءة رد نموذج لاما 4 الصحيحة لمنع خطأ الـ attribute 'message'
                    english_prompt = translation_completion.choices[0].message.content

                    # استدعاء خادم الرسم الصاروخي والمجاني المباشر من كروك
                    ROUTER_URL = "https://groq.com"
                    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
                    payload = {
                        "model": "black-forest-labs/FLUX.1-schnell",
                        "prompt": english_prompt,
                        "n": 1,
                        "size": "1024x1024"
                    }
                    
                    response = requests.post(ROUTER_URL, json=payload, headers=headers)
                    
                    if response.status_code == 200:
                        img_url = response.json()['data'][0]['url']
                        img_response = requests.get(img_url)
                        
                        if img_response.status_code == 200:
                            image = Image.open(io.BytesIO(img_response.content))
                            st.image(image, caption="تفضلي رسمتي يا أحلام! ✨")
                            
                            # حفظ اللوحة في الذاكرة لكي لا تضيع
                            img_base64 = base64.b64encode(img_response.content).decode('utf-8')
                            st.session_state.drawings.append({"prompt": draw_query, "img_base64": img_base64})
                            st.rerun()
                    else:
                        # محرك الدعم الرديف المفتوح والمجاني على هاجينج فيس في حال صيانة سيرفر كروك الرئيسي
                        BACKUP_URL = "https://huggingface.co"
                        headers_bf = {"Authorization": f"Bearer {st.secrets['HF_TOKEN']}"}
                        res_backup = requests.post(BACKUP_URL, headers=headers_bf, json={"inputs": english_prompt})
                        
                        if res_backup.status_code == 200:
                            image = Image.open(io.BytesIO(res_backup.content))
                            st.image(image, caption="تفضلي رسمتي يا أحلام! ✨")
                            img_base64 = base64.b64encode(res_backup.content).decode('utf-8')
                            st.session_state.drawings.append({"prompt": draw_query, "img_base64": img_base64})
                            st.rerun()
                        else:
                            st.error("⚠️ واجه سيرفر الرسم ضغطاً مؤقتاً، اضغطي على الزر مجدداً لتوليدها فوراً!")
                            
                except Exception as e:
                    st.error(f"⚠️ واجهت سمسمة مشكلة تقنية: {e}")
