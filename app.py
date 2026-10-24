import streamlit as st
import pandas as pd
from google import genai
import io
import time

API_KEY = "AQ.Ab8RN6IOwIHD_HyXjhlGqVdDmJmYFggVzgTVs2FhbmTXLUa4Jg"
client = genai.Client(api_key=API_KEY)

def check_name_match(ar_name, en_name):
    if pd.isna(ar_name) or pd.isna(en_name):
        return "غير مكتمل", ""
    
    prompt = f"""
    قارن بين هذين الاسمين وحدد ما إذا كان الاسم الإنجليزي يمثل النطق والتهجئة الصحيحة للاسم العربي أم لا:
    - الاسم العربي: {ar_name}
    - الاسم الإنجليزي: {en_name}

    القواعد:
    1. تقبّل اختلافات التهجئة الشائعة.
    2. إذا كان الاسمان لنفس الشخص مع اختلاف تهجئة بسيط ومقبول، أجب بكلمة: صحيح
    3. إذا كانت الترجمة خاطئة تماماً، أجب بكلمة: خاطئ متبوعة بعلامة (-) ثم اكتب الترجمة الإنجليزية الصحيحة.

    أمثلة صارمة للإجابة (لا تكتب أي تفاصيل أخرى):
    - صحيح
    - خاطئ - Mohamed Ahmed
    """
    try:
        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=prompt,
        )
        result = response.text.strip()
        
        if "صحيح" in result:
            return "صحيح", ""
        elif "خاطئ" in result:
            parts = result.split('-')
            if len(parts) > 1:
                return "خاطئ", parts[1].strip()
            else:
                return "خاطئ", "تعذر استخراج الاقتراح"
        else:
            return "حالة غير معروفة", ""
            
    except Exception as e:
        return f"خطأ: {str(e)}", ""

st.markdown("""
<div style='text-align: right; direction: rtl;'>
    <h1 style='color: #FF4B4B;'>🚨 الأستاذ مرتضى وصل يا موقع! 💼</h1>
    <p style='font-size: 22px;'><b>⚡ أنا الموظف الجديد هنا.. وأعوذ بالله من كلمة أنا 🧙‍♂️</b></p>
    <p style='font-size: 20px;'>الوكيل المعتمد للذكاء الاصطناعي والمتخصص في <b>صيد وفحص صحة الأسماء الإنجليزية!</b> 🎯👀</p>
    <p style='font-size: 20px;'>🔍 <i>أي اسم مترجم غلط.. هيتعمل معاه السليمة فوراً وهنكتبلك الترجمة الصح!</i> 🥊❌</p>
</div>
<hr>
""", unsafe_allow_html=True)

st.warning("⚠️ **تنبيه هام:** الفحص بياخد شوية وقت عشان براجع اسم اسم بضمير ومبنحبش الكروتة.. فاعمل كوباية شاي واصبر عليا شوية لحد ما أخلص! ☕⏳", icon="⏳")
uploaded_file = st.file_uploader("اختر ملف الإكسل (بصيغة xlsx)", type=["xlsx"])

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)
    st.success("تم قراءة الملف بنجاح!")
    
    if st.button("🚀 بدء الفحص الآن"):
        match_statuses = []
        correct_translations = []
        total_names = len(df)
        
        progress_bar = st.progress(0)
        status_text = st.empty()

        for index, row in df.iterrows():
            status_text.text(f"جاري فحص الاسم {index + 1} من {total_names}... (بذمة وضمير)")
            
            status, correct_name = check_name_match(row['الاسم'], row['الاسم باللغة الانجليزية'])
            
            match_statuses.append(status)
            correct_translations.append(correct_name)
            
            progress_bar.progress((index + 1) / total_names)
            time.sleep(3) # تأخير لتجنب حظر الطلبات
            
        df['حالة المطابقة'] = match_statuses
        df['الترجمة الصحيحة (إن وجدت)'] = correct_translations
        
        status_text.text("✅ الأستاذ مرتضى خلص شغل.. استلم ملفك!")
        
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
        processed_data = output.getvalue()
        
        st.download_button(
            label="📥 تحميل ملف الإكسل المُراجع",
            data=processed_data,
            file_name="الأسماء_بعد_المراجعة.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
