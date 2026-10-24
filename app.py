import streamlit as st
import pandas as pd
from google import genai
import io
import time

API_KEY = st.secrets["GEMINI_API_KEY"]
client = genai.Client(api_key=API_KEY)

def check_names_batch(batch_df):
    names_text = "\n".join([f"{idx} | {row['الاسم']} | {row['الاسم باللغة الانجليزية']}" for idx, row in batch_df.iterrows()])
    
    prompt = f"""
    أنت خبير لغوي متخصص. راجع قائمة الأسماء التالية وطابق العربي مع الإنجليزي.
    القواعد الصارمة:
    1. تجاهل حالة الأحرف والمسافات الزائدة.
    2. تقبل الاختلافات الشائعة للأسماء العادية.
    3. يجب تطابق عدد المقاطع.
    4. ⚠️ شروط إجبارية (أي تهجئة مختلفة لهذه الأسماء تعتبر خطأ فوراً):
       - أي اسم "محمد" يجب أن يُكتب "Mohamed" فقط.
       - أي اسم "هشام" يجب أن يُكتب "Hisham" فقط.
       - أي اسم "سمر" يجب أن يُكتب "Samar" فقط.
       - أي اسم "عياد" يجب أن يُكتب "Ayad" فقط.
    
    الأسماء المطلوب فحصها (الرقم المرجعي | الاسم العربي | الاسم الإنجليزي):
    {names_text}

    يجب أن يكون الرد عبارة عن سطر لكل اسم، بنفس الرقم المرجعي، بهذا التنسيق الصارم (استخدم علامة | كفاصل):
    الرقم المرجعي | صحيح أو خاطئ | الترجمة الصحيحة (إن وجدت)
    """
    
    try:
        response = client.models.generate_content(
        model="gemini-1.5-flash-latest",
            contents=prompt,
        )
        lines = response.text.strip().split('\n')
        
        results_dict = {}
        for line in lines:
            parts = [p.strip() for p in line.split('|')]
            if len(parts) >= 2 and parts[0].isdigit():
                idx = int(parts[0])
                status = "صحيح" if "صحيح" in parts[1] else "خاطئ"
                correct = parts[2] if len(parts) > 2 and status == "خاطئ" else ""
                results_dict[idx] = (status, correct)
        return results_dict
    except Exception as e:
        # طباعة الخطأ الفعلي القادم من جوجل في عمود الترجمة لمعرفة السبب
        return {idx: ("مرتضى زعلان 😤", f"الخطأ التقني: {str(e)}") for idx, row in batch_df.iterrows()}

st.markdown("""
<div style='text-align: right; direction: rtl;'>
    <h1 style='color: #FF4B4B;'>🚨 الأستاذ مرتضى وصل يا موقع! 💼</h1>
    <p style='font-size: 22px;'><b>⚡ أنا الموظف الجديد هنا.. وأعوذ بالله من كلمة أنا 🧙‍♂️</b></p>
    <p style='font-size: 20px;'>الوكيل المعتمد للذكاء الاصطناعي والمتخصص في <b>صيد وفحص صحة الأسماء الإنجليزية!</b> 🎯👀</p>
</div>
<hr>
""", unsafe_allow_html=True)

st.markdown("""
<div style="background-color: rgba(255, 215, 0, 0.15); padding: 16px; border-radius: 8px; font-size: 18px; direction: rtl; text-align: right; border-right: 5px solid #ffc107; margin-bottom: 20px;">
    🚀 <b>تحديث جديد:</b> الفحص بيتم بنظام الدفعات السريعة، ومحمد وهشام وسمر وعياد ليهم معاملة خاصة.
</div>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader("اختر ملف الإكسل (بصيغة xlsx)", type=["xlsx"])

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)
    df.columns = df.columns.str.strip()
    
    if 'الاسم' not in df.columns or 'الاسم باللغة الانجليزية' not in df.columns:
        st.error("🛑 عناوين العواميد مش مظبوطة! لازم تكون 'الاسم' و 'الاسم باللغة الانجليزية'.")
    else:
        st.success("✅ تم قراءة الملف بنجاح!")
        
        if st.button("🚀 بدء الفحص السريع"):
            total_names = len(df)
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            df['حالة المطابقة'] = "جاري الفحص..."
            df['الترجمة الصحيحة (إن وجدت)'] = ""
            
            # تقليل الدفعة إلى 10 لتخفيف الضغط على الخادم
            batch_size = 10 
            
            for i in range(0, total_names, batch_size):
                status_text.text(f"جاري فحص الدفعة {(i//batch_size)+1}...")
                batch_df = df.iloc[i:i+batch_size]
                
                batch_results = check_names_batch(batch_df)
                
                if batch_results:
                    for idx, (status, correct) in batch_results.items():
                        if idx in df.index:
                            df.at[idx, 'حالة المطابقة'] = status
                            df.at[idx, 'الترجمة الصحيحة (إن وجدت)'] = correct
                
                progress_bar.progress(min((i + batch_size) / total_names, 1.0))
                time.sleep(4) # تأخير 4 ثوانٍ أمان
                
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
