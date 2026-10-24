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
<div style="background-color: rgba(255, 215, 0, 0.15); padding: 16px; border-radius: 8px; font-size: 18px;
