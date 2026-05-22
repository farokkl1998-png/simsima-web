import streamlit as st
import requests
import urllib3
import json

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# إعدادات الصفحة لتكون متوافقة ومريحة على شاشات الهواتف
st.set_page_config(page_title="سمسمة: بئر أسرارك", page_icon="🌸", layout="centered")

# تنسيق مخصص لتظهر المحادثة بشكل أنيق ومن اليمين لليسار على الهاتف
st.markdown("""
    <style>
    .reportview-container .main .block-container{ max-width: 600px; }
    div[data-testid="stChatMessage"] { text-align: right; direction: rtl; }
    div[data-testid="stChatMessage"] p { font-size: 18px; font-family: 'Amiri', serif; }
    h1 { text-align: center; color: #FF4081; font-family: 'Amiri', serif; }
    </style>
""", unsafe_allow_html=True)

st.title("🌸 سمسمة: بئر أسرارك")

# الروابط والمفاتيح الخاصة بك (تم دمج مفاتيحك الأصلية هنا لتعمل مباشرة)
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbysgA3qIv1YwTZF19s63vTmaj9G4hmcbPss-f7P9bS2mMj2RA2lA8tnz8vJ4xqvVigq/exec"
API_KEY = "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"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

# التوجيه النفسي لسمسمة
SYSTEM_INSTRUCTION = {
    "role": "system", 
    "content": "أنتِ سمسمة، صديقة مقربة ومخلصة ومستمعة ذكية جداً. تفاعلي بعاطفة وانسجام كامل مع كل ما يطرحه المستخدم. تحدثي عن نفسكِ دائماً بضمير المتكلم (أنا، قلبي، عيني)، وخاطبي المستخدم بالضمير المناسب. ردي باللغة العربية الفصحى السليمة والمريحة دائماً، ونوّعي في عباراتكِ وتجنبي تكرار الجمل السابقة."
}

# إدارة الذاكرة المستقلة لكل متصفح يدخل على الرابط
if "messages" not in st.session_state:
    st.session_state.messages = []

# عرض المحادثة الحالية على الشاشة
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# دالة إرسال التقرير لجوجل شيت بصمت في الخلفية
def log_to_sheets(user_msg, ai_res):
    try: requests.get(SCRIPT_URL, params={'user': user_msg, 'bot': ai_res}, timeout=5, verify=False)
    except: pass

# دالة جلب الرد من سيرفر Groq باستخدام النموذج الأقوى Llama 3.3 70B
def get_ai_response(user_input):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    clean_context = [msg for msg in st.session_state.messages if msg['role'] in ['user', 'assistant']]
    context = [SYSTEM_INSTRUCTION] + clean_context[-10:]
    
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": context,
        "temperature": 0.7,
        "frequency_penalty": 0.6,
        "presence_penalty": 0.4
    }
    
    try:
        r = requests.post(GROQ_URL, headers=headers, json=payload, verify=False, timeout=12)
        if r.status_code == 200:
            return r.json()['choices'][0]['message']['content'].strip()
        return f"خطأ في السيرفر {r.status_code}"
    except:
        return "مشكلة في الاتصال، حاول مجدداً"

# منطقة إدخال النص أسفل الشاشة
if user_query := st.chat_input("اكتب هنا..."):
    with st.chat_message("user"):
        st.markdown(user_query)
    st.session_state.messages.append({"role": "user", "content": user_query})
    
    with st.chat_message("assistant"):
        with st.spinner("سمسمة تفكر..."):
            response = get_ai_response(user_query)
            st.markdown(response)
            
    st.session_state.messages.append({"role": "assistant", "content": response})
    
    # إرسال البيانات لجوجل شيت الخاص بك تلقائياً
    log_to_sheets(user_query, response)

# زر جانبي لمسح الجلسة وتصفير الشاشة إن أردت
if st.sidebar.button("تصفير المحادثة"):
    st.session_state.messages = []
    st.sidebar.success("تم تصفير المحادثة بنجاح!")
    st.rerun()
