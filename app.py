import streamlit as st
import pandas as pd
from google import genai
import io
import time

API_KEY = "AQ.Ab8RN6IOwIHD_HyXjhlGqVdDmJmYFggVzgTVs2FhbmTXLUa4Jg"
client = genai.Client(api_key=API_KEY)

def check_name_match(ar_name, en_name):
    if pd.isna(ar_name) or pd.isna(en_name):
        return "غير مكتمل"
    
    prompt = f"""
    قارن بين هذين الاسمين وحدد ما إذا كان الاسم الإنجليزي يمثل النطق والتهجئة الصحيحة للاسم العربي أم لا:
    - الاسم العربي: {ar_name}
    - الاسم الإنجليزي: {en_name}

    القواعد:
    1. تقبّل اختلافات التهجئة الشائعة.
    2. إذا كان الاسمان لنفس الشخص مع اختلاف تهجئة بسيط ومقبول، أجب بـ: صحيح
    3. إذا كان الاسمان لشخصين مختلفين أو الترجمة خاطئة تماماً، أجب بـ: خاطئ

    أجب بكلمة واحدة فقط: إما (صحيح) أو (خاطئ).
    """
    try:
        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=prompt,
        )
        result = response.text.strip()
        return "صحيح" if "صحيح" in result else "خاطئ"
    except Exception as e:
        return f"خطأ: {str(e)}"

st.title("🤖 وكيل الذكاء الاصطناعي لفحص مطابقة الأسماء")
st.write("ارفع ملف الإكسل، وسيقوم النظام بفحصه وإصدار ملف النتيجة جاهزاً للتحميل.")

uploaded_file = st.file_uploader("اختر ملف الإكسل (بصيغة xlsx)", type=["xlsx"])

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)
    st.success("تم قراءة الملف بنجاح!")
    
    if st.button("🚀 بدء الفحص الآن"):
        results = []
        total_names = len(df)
        progress_bar = st.progress(0)
        status_text = st.empty()

        for index, row in df.iterrows():
            status_text.text(f"جاري فحص الاسم {index + 1} من {total_names}...")
            match_status = check_name_match(row['الاسم'], row['الاسم باللغة الانجليزية'])
            results.append(match_status)
            progress_bar.progress((index + 1) / total_names)
            
            # تأخير 4 ثوانٍ لتجنب حظر الطلبات السريعة
            time.sleep(4)
            
        df['حالة المطابقة'] = results
        status_text.text("✅ تم الانتهاء من الفحص بنجاح!")
        
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
