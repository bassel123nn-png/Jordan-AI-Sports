import streamlit as st
import pandas as pd

# إعدادات الصفحة
st.set_page_config(page_title="Overtraining AI Predictor", page_icon="🏃‍♂️")

st.title("نظام التنبؤ بالإرهاق الرياضي 🇯🇴")
st.subheader("التحليل المدعوم بالذكاء الاصطناعي لبيانات الرياضيين")

st.info("هذه النسخة التجريبية الأولى (Proof of Concept) لمقترح الدكتوراه.")

# الزر المؤقت للتجربة
if st.button("Connect with Strava 🔗"):
    st.success("تمت محاكاة الاتصال بنجاح! سيتم سحب البيانات في النسخة النهائية.")
    
    # بيانات وهمية سريعة لعرض شكل الجدول النهائي للجنة
    mock_data = pd.DataFrame({
        'Date': ['2026-07-28', '2026-07-29', '2026-07-30'],
        'Duration (mins)': [45, 60, 90],
        'Avg Heart Rate': [140, 155, 172],
        'Training Load': [270, 420, 810],
        'Overtraining Risk': ['Safe 🟢', 'Safe 🟢', 'Risk 🔴']
    })
    
    st.write("آخر 3 تمارين تم سحبها:")
    st.dataframe(mock_data)