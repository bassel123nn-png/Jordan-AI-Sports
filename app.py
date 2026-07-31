import streamlit as st
import requests
import pandas as pd
import urllib.parse
from datetime import datetime

# إعدادات الصفحة - استخدمنا وضع الشاشة العريضة للرسوم البيانية
st.set_page_config(page_title="Overtraining AI Predictor", page_icon="🏃‍♂️", layout="wide")
st.title("نظام التنبؤ بالإرهاق الرياضي 🇯🇴")
st.subheader("التحليل المدعوم بالذكاء الاصطناعي لبيانات الرياضيين")

# مفاتيح الربط
CLIENT_ID = "268965"
CLIENT_SECRET = "6a94357c4df6f6d743a72a885a13d132ca911ec1"
REDIRECT_URI = "https://jordan-ai-sports-4n5tndhgkesysquygzwyhg.streamlit.app/"

def create_oauth_url():
    auth_url = "https://www.strava.com/oauth/authorize"
    params = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "approval_prompt": "force",
        "scope": "activity:read_all"
    }
    return f"{auth_url}?{urllib.parse.urlencode(params)}"

# 1. قسم النظام في حال وجود البيانات
if "access_token" in st.session_state:
    access_token = st.session_state["access_token"]
    athlete_name = st.session_state["athlete_name"]
    
    st.success(f"مرحباً كابتن {athlete_name}! تم سحب بياناتك بنجاح.")
    
    # سحب البيانات لآخر 7 تمارين لبناء الرسم البياني
    activities_url = "https://www.strava.com/api/v3/athlete/activities"
    header = {'Authorization': 'Bearer ' + access_token}
    param = {'per_page': 7, 'page': 1} 
    dataset = requests.get(activities_url, headers=header, params=param).json()
    df = pd.json_normalize(dataset)
    
    # هندسة الميزات (Feature Engineering)
    cols_to_keep = ['name', 'start_date_local', 'distance', 'moving_time', 'average_heartrate']
    existing_cols = [col for col in cols_to_keep if col in df.columns]
    df_final = df[existing_cols].copy()
    
    if 'moving_time' in df_final.columns and 'average_heartrate' in df_final.columns:
        df_final['Duration (mins)'] = round(df_final['moving_time'] / 60, 2)
        # حساب حمل التدريب (TRIMP)
        df_final['TRIMP'] = round((df_final['Duration (mins)'] * df_final['average_heartrate']) / 100, 1)
        # تجهيز التاريخ للرسم البياني
        df_final['Date'] = pd.to_datetime(df_final['start_date_local']).dt.date
        
    if 'distance' in df_final.columns:
        df_final['Distance (km)'] = round(df_final['distance'] / 1000, 2)
        
    # --- قسم الرسوم البيانية للمدرب (Data Visualization) ---
    st.divider()
    st.header("📊 لوحة تحكم المدرب: السجل التاريخي لأحمال التدريب")
    st.write("يوضح هذا الرسم البياني تدرج الأحمال التدريبية (TRIMP) للاعب في التمارين الأخيرة، مما يساعد المدرب على رؤية الإرهاق التراكمي بوضوح:")
    
    if 'TRIMP' in df_final.columns:
        # ترتيب البيانات زمنياً من الأقدم للأحدث للرسم البياني
        chart_data = df_final[['Date', 'TRIMP']].sort_values(by='Date').set_index('Date')
        st.bar_chart(chart_data)
        
    st.write("التفاصيل الرقمية لأحدث التمارين:")
    st.dataframe(df_final[['name', 'Date', 'Duration (mins)', 'average_heartrate', 'TRIMP']])
    
    # --- قسم التقييم اليومي (Subjective Data) ---
    st.divider()
    st.header("التقييم اليومي للجاهزية")
    st.write("يرجى إدخال الحالة النفسية والجسدية للاعب اليوم:")
    
    col1, col2 = st.columns(2)
    with col1:
        sleep = st.slider("جودة النوم (1 سيء - 10 ممتاز)", 1, 10, 5)
        soreness = st.slider("ألم العضلات (1 شديد - 10 لا يوجد)", 1, 10, 5)
    with col2:
        stress = st.slider("مستوى التوتر (1 ضغط - 10 مرتاح)", 1, 10, 5)
        mood = st.slider("المزاج العام (1 سيء - 10 ممتاز)", 1, 10, 5)
        
    # --- العقل المدبر: دمج البيانات (Data Fusion & AI Logic) ---
    if st.button("تحليل الجاهزية واتخاذ القرار 🧠"):
        subjective_score = sleep + soreness + stress + mood
        
        # استخراج بيانات آخر تمرين وحساب الفجوة الزمنية
        latest_trimp = df_final.iloc[0]['TRIMP'] if not df_final.empty and 'TRIMP' in df_final.columns else 0
        latest_date_str = df_final.iloc[0]['start_date_local']
        latest_date = pd.to_datetime(latest_date_str).tz_localize(None)
        days_since_last_workout = (pd.Timestamp.now() - latest_date).days
        
        st.subheader("نتائج دمج البيانات (Data Fusion):")
        st.info(f"آخر تمرين كان منذ: **{days_since_last_workout} أيام** | حمل التدريب السابق (TRIMP): **{latest_trimp}** | التقييم الذاتي: **{subjective_score}/40**")
        
        # خوارزمية اتخاذ القرار
        if days_since_last_workout > 7:
            if subjective_score >= 25:
                st.success("🟢 قرار النظام: اللاعب لم يتدرب منذ فترة (الإرهاق التراكمي = 0) وحالته النفسية ممتازة. جاهز للعودة بحمل تدريبي عالي.")
            else:
                st.warning("🟡 قرار النظام: اللاعب لم يتدرب منذ فترة ولكن تقييمه الذاتي منخفض (توتر/قلة نوم). يُنصح بتمارين خفيفة (Active Recovery) للتهيئة.")
        else:
            if latest_trimp > 30 and subjective_score < 20:
                st.error("🔴 قرار النظام: خطر الإرهاق والإصابة عالي جداً! (حمل سابق مرتفع + عدم تعافي ذاتي). يُنصح بالراحة التامة فوراً.")
            elif latest_trimp > 30 and subjective_score >= 20:
                st.warning("🟡 قرار النظام: حالة مقبولة. اللاعب يتعافى جيداً من الجهد السابق. يُنصح بتمرين متوسط الشدة اليوم.")
            else:
                st.success("🟢 قرار النظام: جاهزية ممتازة. الحمل التراكمي آمن والتعافي الذاتي ممتاز. جاهز لكسر الأرقام بحمل عالي.")

# 2. المصادقة واستقبال الكود
elif "code" in st.query_params:
    auth_code = st.query_params["code"]
    token_url = "https://www.strava.com/oauth/token"
    payload = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": auth_code,
        "grant_type": "authorization_code"
    }
    
    response = requests.post(token_url, data=payload).json()
    
    if "access_token" in response:
        st.session_state["access_token"] = response["access_token"]
        st.session_state["athlete_name"] = response["athlete"]["firstname"]
        st.query_params.clear()
        st.rerun()
    else:
        st.error("الكود منتهي الصلاحية، يرجى العودة للرابط الأساسي والمحاولة.")

# 3. واجهة البداية
else:
    st.info("للبدء، يرجى ربط حسابك لسحب البيانات التدريبية بشكل آمن:")
    st.link_button("Connect with Strava 🔗", create_oauth_url())
