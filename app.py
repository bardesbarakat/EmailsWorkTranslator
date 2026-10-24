import streamlit as st
import pandas as pd
from google import genai
import io
import time

# إعداد الاتصال بالذكاء الاصطناعي بشكل آمن ومخفي
API_KEY = st.secrets["GEMINI_API_KEY"]
client = genai.Client(api_key=API_KEY)

def check_name_match(ar_name, en_name):
    if pd.isna(ar_name) or pd.isna(en_name):
        return "غير مكتمل", ""
    
    prompt = f"""
    أنت خبير لغوي متخصص في مطابقة الأسماء العربية مع ترجمتها الإنجليزية.
    مهمتك: مقارنة الاسم العربي بالاسم الإنجليزي بدقة.

    - الاسم العربي: {ar_name}
    - الاسم الإنجليزي: {en_name}

    القواعد الصارمة:
    1. تجاهل حالة الأحرف (Capital/Small) والمسافات الزائدة تماماً.
    2. تقبل الاختلافات الشائعة والمقبولة، مثل:
       - أل التعريف (Al/El) والأسماء المركبة (Abdel/Abd El/Abdal/Abdul).
       - التهجئات المتعددة (Mohamed/Mohammed/Muhammad) و (Mostafa/Moustafa/Mustafa).
       - الحروف المتقاربة (ق = K/Q)، (خ = Kh)، (غ = Gh)، (ع = A/E).
       - التاء المربوطة في نهاية الاسم (Osama/Usama/Osamah).
       - الحروف المتحركة (a/e/i/o/u) قابلة للتبديل طالما النطق الأساسي صحيح.
    3. يجب أن يكون عدد المقاطع متطابقاً (إذا كان العربي 4 مقاطع والإنجليزي 3، يعتبر خطأ).
    4. إذا كان الاسمان لنفس الشخص مع اختلاف تهجئة مقبول، أجب بكلمة: صحيح
    5. إذا كان هناك اختلاف جذري، نقص في المقاطع، أو خطأ فادح، أجب بكلمة: خاطئ متبوعة بعلامة (-) ثم اكتب الترجمة الإنجليزية الصحيحة.

    أمثلة للإجابة فقط:
    - صحيح
    - خاطئ - Gehad Ramadan Hamed
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
        # هنا التعديل الجديد لرسالة الخطأ بشخصية مرتضى
        return "مرتضى زعلان 😤", "السيستم مهنج.. اعملي كوباية شاي وجربي تاني!"

# تصميم واجهة الموقع بأسلوب الأستاذ مرتضى
st.markdown("""
<div style='text-align: right; direction: rtl;'>
    <h1 style='color: #FF4B4B;'>🚨 الأستاذ مرتضى وصل يا موقع! 💼</h1>
    <p style='font-size: 22px;'><b>⚡ أنا الموظف الجديد هنا.. وأعوذ بالله من كلمة أنا 🧙‍♂️</b></p>
    <p style='font-size: 20px;'>الوكيل المعتمد للذكاء الاصطناعي والمتخصص في <b>صيد وفحص صحة الأسماء الإنجليزية!</b> 🎯👀</p>
    <p style='font-size: 20px;'>🔍 <i>أي اسم مترجم غلط.. هيتعمل معاه السليمة فوراً وهنكتبلك الترجمة الصح!</i> 🥊❌</p>
</div>
<hr>
""", unsafe_allow_html=True)

st.markdown("""
<div style="background-color: rgba(255, 215, 0, 0.15); padding: 16px; border-radius: 8px; font-size: 18px; direction: rtl; text-align: right; border-right: 5px solid #ffc107; margin-bottom: 20px;">
    ⏳ <b>تنبيه هام:</b> الفحص بياخد شوية وقت عشان براجع اسم اسم بضمير ومبنحبش الكروتة.. فاعمل كوباية شاي واصبر عليا شوية لحد ما أخلص! ☕
</div>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader("اختر ملف الإكسل (بصيغة xlsx)", type=["xlsx"])

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)
    df.columns = df.columns.str.strip() # لحذف المسافات الزائدة تلقائياً من العناوين
    
    # التحقق من وجود الأعمدة المطلوبة
    if 'الاسم' not in df.columns or 'الاسم باللغة الانجليزية' not in df.columns:
        st.error("🛑 ستوب عندك! الأستاذ مرتضى مبيعرفش يشتغل كدا.. عناوين العواميد مش مظبوطة!")
        st.warning(
            "عشان أقدر أفحص الملف، لازم تتأكد إن الصف الأول في الإكسل مكتوب فيه العنوانين دول بالحرف:\n"
            "- **الاسم**\n"
            "- **الاسم باللغة الانجليزية**\n\n"
            "ظبط أسماء العواميد في ملفك وارفعه تاني يا ريس!"
        )
    else:
        st.success("✅ تم قراءة الملف بنجاح! العواميد مظبوطة وجاهزين للشغل.")
        
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
                time.sleep(3) # تأخير 3 ثواني لمنع حظر الطلبات
                
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
