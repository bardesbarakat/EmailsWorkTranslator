if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)
    df.columns = df.columns.str.strip() # لحذف المسافات الزائدة تلقائياً
    
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
                time.sleep(3) 
                
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
