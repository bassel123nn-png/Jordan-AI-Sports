import streamlit as st
import requests
import pandas as pd
import urllib.parse

# إعدادات الصفحة
st.set_page_config(page_title="Overtraining AI Predictor", page_icon="🏃‍♂️")
st.title("نظام التنبؤ بالإرهاق الرياضي 🇯🇴")
st.subheader("التحليل المدعوم بالذكاء الاصطناعي لبيانات الرياضيين")

# مفاتيح الربط مع سترافا
CLIENT_ID = "268965"
CLIENT_SECRET = "6a94357c4df6f6d743a72a885a13d132ca911ec1"


REDIRECT_URI = "https://jordan-ai-sports-4n5tndhgkesysquygzwyhg.streamlit.app/"

# دالة لإنشاء رابط المصادقة
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

# واجهة المستخدم وعملية الربط
if "code" not in st.query_params:
    st.info("للبدء، يرجى ربط حسابك لسحب البيانات التدريبية بشكل آمن:")
    st.link_button("Connect with Strava 🔗", create_oauth_url())
else:
    st.success("تمت المصادقة! جاري سحب التمارين الحقيقية...")
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
        access_token = response["access_token"]
        athlete_name = response["athlete"]["firstname"]
        st.write(f"مرحباً كابتن **{athlete_name}**! إليك أحدث بياناتك التدريبية:")
        
        # سحب البيانات الحقيقية
        activities_url = "https://www.strava.com/api/v3/athlete/activities"
        header = {'Authorization': 'Bearer ' + access_token}
        param = {'per_page': 5, 'page': 1}
        
        dataset = requests.get(activities_url, headers=header, params=param).json()
        df = pd.json_normalize(dataset)
        
        # ترتيب الجدول
        cols_to_keep = ['name', 'start_date_local', 'distance', 'moving_time', 'average_heartrate']
        existing_cols = [col for col in cols_to_keep if col in df.columns]
        df_final = df[existing_cols].copy()
        
        if 'moving_time' in df_final.columns:
            df_final['Duration (mins)'] = round(df_final['moving_time'] / 60, 2)
        if 'distance' in df_final.columns:
            df_final['Distance (km)'] = round(df_final['distance'] / 1000, 2)
            
        st.dataframe(df_final)
    else:
        st.error("حدث خطأ في جلب البيانات. يرجى التأكد من المفاتيح السرية والمحاولة لاحقاً.")
