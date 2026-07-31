import streamlit as st
import requests
import pandas as pd
import urllib.parse
from datetime import datetime

# إعدادات الصفحة
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

if "access_token" in st.session_state:
    access_token = st.session_state["access_token"]
    athlete_name = st.session_state["athlete_name"]
    
    st.success(f"مرحباً كابتن {athlete_name}! تم سحب بياناتك بنجاح.")
    
    activities_url = "https://www.strava.com/api/v3/athlete/activities"
    header = {'Authorization': 'Bearer ' + access_token}
    param = {'per_page': 7, 'page': 1} 
    dataset = requests.get(activities_url, headers=header, params=param).json()
    df = pd.json_normalize(dataset)
    
    cols_to_keep = ['name', 'start_date_local', 'distance', 'moving_time', 'average_heartrate']
    existing_cols = [col for col in cols_to_keep if col in df.columns]
    df_final = df[existing_cols].copy()
    
    if 'moving_time' in df_final.columns and 'average_heartrate' in df_final.columns:
        df_final['Duration (mins)'] = round(df_final['moving_time'] / 60, 2)
        df_final['TRIMP'] = round((df_final['Duration (mins)'] * df_final['average_heartrate']) / 100, 1)
        df_final['Date'] = pd.to_datetime(df_final['start_date_local']).dt.date
        
    if 'distance' in df_final.columns:
        df_final['Distance (km)'] = round(df_final['distance'] / 1000, 2)
        
    st.divider()
    st.header("📊 لوحة تحكم المدرب: السجل التاريخي لأحمال التدريب")
    
    if 'TRIMP' in df_final.columns:
        chart_data = df_final[['Date', 'TRIMP']].sort_values(by='Date').set_index('Date')
        st.bar_chart(chart_data)
        
    st.dataframe(df_final[['name', 'Date', 'Duration (mins)', 'average_heartrate', 'TRIMP']])
    
    st.divider()
    st.header("التقييم اليومي للجاهزية")
    
    col1, col2 = st.columns(2)
    with col1:
        sleep = st.slider("جودة النوم (1 سيء - 10 ممتاز)", 1, 10, 5)
        soreness = st.slider("ألم العضلات (1 شديد - 10 لا يوجد)", 1, 10, 5)
    with col2:
        stress = st.slider("مستوى التوتر (1 ضغط - 10 مرتاح)", 1, 10, 5)
        mood = st.slider("المزاج العام (1 سيء - 10 ممتاز)", 1, 10, 5)
        
    # --- العقل المدبر: التحليل الدقيق (Granular Analysis) ---
    if st.button("تحليل الجاهزية واتخاذ القرار 🧠"):
        latest_trimp = df_final.iloc[0]['TRIMP'] if not df_final.empty and 'TRIMP' in df_final.columns else 0
        latest_date_str = df_final.iloc[0]['start_date_local'] if not df_final.empty else None
        
        if latest_date_str:
            latest_date = pd.to_datetime(latest_date_str).tz_localize(None)
            days_since_last_workout = (pd.Timestamp.now() - latest_date).days
        else:
            days_since_last_workout = 9999
            
        st.subheader("نتائج دمج البيانات والتحليل الذكي:")
        st.info(f"آخر تمرين كان منذ: **{days_since_last_workout} أيام** | حمل التدريب السابق (TRIMP): **{latest_trimp}**")
        
        # مصفوفة الأخطاء والملاحظات
        flags = []
        
        # 1. تحليل الألم العضلي مع الزمن
        if soreness <= 4:
            if days_since_last_workout > 14:
                flags.append("⚠️ **ألم عضلي غير مبرر رياضياً:** آخر تمرين كان قبل فترة طويلة جداً. قد يكون هذا الألم نتيجة مجهود بدني خارج التدريب الرياضي أو بداية إصابة. (يُنصح بالحذر).")
            else:
                flags.append("⚠️ **إجهاد عضلي:** العضلات لم تتعافَ بشكل كامل من التدريبات السابقة.")
                
        # 2. تحليل جودة النوم
        if sleep <= 4:
            flags.append("⚠️ **نقص جودة النوم:** التعافي الجسدي وإصلاح الأنسجة غير مكتمل.")
            
        # 3. تحليل الجانب النفسي والعصبي
        if stress <= 4:
            flags.append("⚠️ **ضغط نفسي عالي (توتر):** التدريب العنيف اليوم قد يؤدي إلى إرهاق الجهاز العصبي المركزي (CNS Fatigue).")
        if mood <= 4:
            flags.append("⚠️ **مزاج عام سيء:** قد يؤثر بشكل مباشر على التركيز والأداء الحركي أثناء التمرين.")

        # --- محرك اتخاذ القرار (Decision Engine) ---
        if not flags:
            if days_since_last_workout > 7:
                st.success("🟢 **قرار النظام:** الجاهزية الجسدية والنفسية ممتازة (100%). نظراً للانقطاع، يُنصح بالعودة بحمل تدريبي تصاعدي لتجنب صدمة العضلات المفاجئة.")
            elif latest_trimp > 30:
                st.success("🟢 **قرار النظام:** بالرغم من أن التمرين السابق كان شاقاً، إلا أن مؤشرات التعافي الذاتي لديك ممتازة جداً. أنت جاهز للمنافسة بحمل عالي اليوم!")
            else:
                st.success("🟢 **قرار النظام:** جاهزية تامة ومثالية. يمكنك أداء أي تمرين تخطط له بأمان تام.")
        else:
            if days_since_last_workout > 7:
                st.warning("🟡 **قرار النظام:** جسدك مستريح رياضياً، لكن هناك عوائق حالية تمنع الأداء المثالي:")
                for flag in flags:
                    st.write(flag)
                st.write("**التوصية:** تمارين خفيفة جداً (Active Recovery) حتى تتحسن المؤشرات السلبية.")
            else:
                if latest_trimp > 30:
                    st.error("🔴 **خطر الإرهاق العالي (Overtraining Risk)!** حمل التمرين السابق كان مرتفعاً، وجسدك يرسل إشارات تحذيرية واضحة:")
                    for flag in flags:
                        st.write(flag)
                    st.write("**التوصية:** راحة سلبية تامة فوراً. تجاهل هذه الإشارات قد يؤدي إلى إصابة مؤكدة.")
                else:
                    st.warning("🟡 **قرار النظام:** مستوى الجاهزية متأثر بالمؤشرات التالية، ويحتاج إلى تعديل في خطة التدريب:")
                    for flag in flags:
                        st.write(flag)
                    st.write("**التوصية:** تمرين متوسط الشدة مع تقليل المدة الزمنية والتركيز العالي على الإحماء.")

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

else:
    st.info("للبدء، يرجى ربط حسابك لسحب البيانات التدريبية بشكل آمن:")
    st.link_button("Connect with Strava 🔗", create_oauth_url())
