import pandas as pd
from google import genai
from google.genai import types

# 1. إعداد الاتصال بنموذج الذكاء الاصطناعي
# استبدل YOUR_API_KEY_HERE بمفتاحك الخاص
API_KEY = "AQ.Ab8RN6IOwIHD_HyXjhlGqVdDmJmYFggVzgTVs2FhbmTXLUa4Jg"
client = genai.Client(api_key=API_KEY)

# 2. قراءة ملف الإكسل
# تأكد من كتابة اسم الملف والامتداد بدقة
input_file = "File1.xlsx"
output_file = "انشاء_بريد_الكتروني_مُراجع.xlsx"

df = pd.read_excel(input_file)

# 3. دالة فحص مطابقة الاسم
def check_name_match(ar_name, en_name):
    # تخطي الصفوف الفارغة إن وجدت
    if pd.isna(ar_name) or pd.isna(en_name):
        return "غير مكتمل"
    
    prompt = f"""
    قارن بين هذين الاسمين وحدد ما إذا كان الاسم الإنجليزي يمثل النطق والتهجئة الصحيحة للاسم العربي أم لا:
    - الاسم العربي: {ar_name}
    - الاسم الإنجليزي: {en_name}

    القواعد:
    1. تقبّل اختلافات التهجئة الشائعة (مثل Mohamed, Muhammad, Elsayed, Al-Sayed).
    2. إذا كان الاسمان لنفس الشخص مع اختلاف تهجئة بسيط ومقبول، أجب بـ: صحيح
    3. إذا كان الاسمان لشخصين مختلفين أو الترجمة خاطئة تماماً، أجب بـ: خاطئ

    أجب بكلمة واحدة فقط: إما (صحيح) أو (خاطئ).
    """
    
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        result = response.text.strip()
        return "صحيح" if "صحيح" in result else "خاطئ"
    except Exception as e:
        print(f"حدث خطأ أثناء معالجة: {ar_name} - {e}")
        return "خطأ في الفحص"

# 4. تنفيذ الفحص على كل صف وإضافة عمود النتيجة
print("جاري فحص الأسماء، يرجى الانتظار...")

# تأكد من مطابقة أسماء الأعمدة كما هي في ملفك
df['حالة المطابقة'] = [
    check_name_match(row['الاسم'], row['الاسم باللغة الانجليزية'])
    for _, row in df.iterrows()
]

# 5. حفظ الملف بعد إضافة عمود النتائج
df.to_excel(output_file, index=False)
print(f"تم الانتهاء بنجاح! تم حفظ الملف باسم: {output_file}")