import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime

# Page Configuration with Professional Styling
st.set_page_config(page_title="INSTAPLAST Leave Portal", page_icon="🏭", layout="wide")

# Custom Professional Theme Colors (Insta Plast Style)
st.markdown("""
    <style>
    .stApp { background-color: #F8FAFC; }
    h1 { color: #1E3A8A !important; font-family: 'Segoe UI', sans-serif; font-weight: 700; }
    .stButton>button { background-color: #1E3A8A !important; color: white !important; border-radius: 6px !important; font-weight: bold !important; }
    .stButton>button:hover { background-color: #1D4ED8 !important; }
    </style>
""", unsafe_allow_html=True)

# 🔴 آپ کا لائیو گوگل ایپس اسکرپٹ یو آر ایل یہاں سیٹ کر دیا گیا ہے
API_URL = "https://script.google.com/macros/s/AKfycbyIvA-XxT1qpezKEU2-DXze6eqEhEGtJmZIM14TbpQVzmhVpVC3pM-DEXT3XJxXNIVf/exec"

# Google Sheet Export Link (For Reading Data Only)
SHEET_ID = "1UjhsblmHa9UoUsbkx9-OYc98rXRcqToTJDdBAHZDciI"
GSHEET_WORKER_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Worker"
GSHEET_REQUESTS_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Requests"

# --- LOAD DATA FROM CLOUD LIVE ---
def load_cloud_data(url, columns):
    try:
        return pd.read_csv(url)
    except Exception:
        return pd.DataFrame(columns=columns)

# --- SEND DATA TO GOOGLE SHEET VIA APPS SCRIPT ---
def send_data_to_sheet(payload_data, sheet_name):
    try:
        payload = {"sheet": sheet_name, "data": payload_data}
        response = requests.post(API_URL, json=payload, headers={"Content-Type": "application/json"})
        if response.status_code == 200 and json.loads(response.text).get("status") == "success":
            st.success("✅ ڈیٹا کامیابی سے گوگل شیٹ میں محفوظ ہو گیا ہے!")
            return True
        else:
            st.error("ڈیٹا سنک کرنے میں مسئلہ آیا ہے۔ ایپس اسکرپٹ چیک کریں۔")
            return False
    except Exception as e:
        st.error(f"نیٹ ورک کا مسئلہ: {str(e)}")
        return False

# Initialize Dataframes
worker_cols = ["name", "id", "cnic", "father_name", "mobile", "salary", "joining_date", "end_date", "department", "password", "photo", "CL", "Sick", "Annual", "CO"]
req_cols = ["id", "worker", "leave_type", "days", "date_from", "date_to", "reason", "applied_on", "status"]

workers_df = load_cloud_data(GSHEET_WORKER_URL, worker_cols)
requests_df = load_cloud_data(GSHEET_REQUESTS_URL, req_cols)

# Clean IDs formatting (.0 removal)
for dataframe in [workers_df, requests_df]:
    if not dataframe.empty and 'id' in dataframe.columns:
        dataframe['id'] = dataframe['id'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()

# Application UI Header
st.markdown("<h1 style='text-align: center;'>🏭 INSTAPLAST Leave Portal</h1>", unsafe_allow_html=True)
st.markdown("---")

# Sidebar - Role Selection
st.sidebar.header("🔒 Gate Panel")
role = st.sidebar.selectbox("Access Role منتخب کریں:", ["Worker", "Admin"])
st.sidebar.markdown("<br><br><small style='color: #94A3B8;'>Powered by INSTAPLAST API v17.0</small>", unsafe_allow_html=True)

# ----------------- WORKER DASHBOARD -----------------
if role == "Worker":
    st.subheader("📋 Worker Leave Application & Profile")
    worker_id_input = st.text_input("اپنا ورکر آئی ڈی درج کریں (e.g., IPL-1020):").strip()
    
    if worker_id_input:
        worker_match = workers_df[workers_df['id'] == worker_id_input]
        
        if not worker_match.empty:
            worker_data = worker_match.iloc[0]
            st.success(f"لاگ ان اسٹیٹس: {worker_data['name']} کا سیشن ایکٹو ہے")
            
            # Display Balances
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("🟢 Casual Leave (CL)", f"{int(worker_data.get('CL', 0))} Days")
            col2.metric("🔴 Sick Leave (SL)", f"{int(worker_data.get('Sick', 0))} Days")
            col3.metric("🔵 Annual Leave (AL)", f"{int(worker_data.get('Annual', 0))} Days")
            col4.metric("🟤 Compensation (CO)", f"{int(worker_data.get('CO', 0))} Days")
            
            col_form, col_profile = st.columns([2, 1])
            
            with col_form:
                st.markdown("### 📝 چھٹی کا فارم (Leave Application)")
                leave_type = st.selectbox("چھٹی کی قسم منتخب کریں:", ["Casual Leave (CL)", "Sick Leave (SL)", "Annual Leave (AL)", "Compensation (CO)"])
                
                c1, c2 = st.columns(2)
                date_from = c1.date_input("کب سے:", min_value=datetime(2010, 1, 1)) # Historical date fix
                date_to = c2.date_input("کب تک:", min_value=datetime(2010, 1, 1))
                
                days_required = st.number_input("کل کتنے دن چھٹی چاہیے:", min_value=1, value=1)
                reason = st.text_area("چھٹی کی وجہ درج کریں:")
                
                if st.button("Apply Now (درخواست بھیجیں)"):
                    new_req_payload = {
                        "id": str(worker_data['id']), "worker": str(worker_data['name']), "leave_type": str(leave_type),
                        "days": int(days_required), "date_from": str(date_from), "date_to": str(date_to),
                        "reason": str(reason), "applied_on": str(datetime.now().date()), "status": "Pending"
                    }
                    if send_data_to_sheet(new_req_payload, "Requests"):
                        st.rerun()
            
            with col_profile:
                st.markdown("### 🌟 ورکر پروفائل")
                st.info(f"**نام:** {worker_data['name']}\n\n**ڈپارٹمنٹ:** {worker_data['department']}\n\n**آئی ڈی:** {worker_data['id']}\n\n**جوائننگ ڈیٹ:** {worker_data['joining_date']}")
        else:
            st.error("یہ ورکر آئی ڈی انسٹا پلاسٹ کے ریکارڈ میں موجود نہیں ہے۔")

# ----------------- ADMIN DASHBOARD -----------------
elif role == "Admin":
    st.subheader("⚙️ Admin Management System")
    menu = st.tabs(["👥 Worker Directory", "📥 Pending Requests", "➕ Add New Worker"])
    
    with menu[0]:
        st.markdown("### ایکٹو ورکرز کا ریکارڈ")
        if not workers_df.empty:
            st.dataframe(workers_df, use_container_width=True)
        else:
            st.info("گوگل شیٹ پر کوئی ورکر ڈیٹا نہیں ملا۔")
            
    with menu[1]:
        st.markdown("### چھٹیوں کی درخواستیں")
        if not requests_df.empty:
            pending_requests = requests_df[requests_df['status'] == "Pending"]
        else:
            pending_requests = pd.DataFrame()
        
        if not pending_requests.empty:
            st.dataframe(pending_requests, use_container_width=True)
        else:
            st.success("سب کلیئر ہے! چھٹی کی کوئی درخواست پینڈنگ نہیں ہے۔")
            
    with menu[2]:
        st.markdown("### نیا ورکر رجسٹر کریں")
        with st.form("add_worker_form"):
            w_name = st.text_input("ورکر کا پورا نام:")
            w_id = st.text_input("مخصوص ورکر آئی ڈی (مثلاً IPL-1025):")
            w_cnic = st.text_input("شناختی کارڈ نمبر (CNIC):")
            w_father = st.text_input("والد کا نام:")
            w_mobile = st.text_input("موبائل نمبر:")
            w_salary = st.number_input("ماہانہ تنخواہ (PKR):", min_value=0, value=25000)
            w_join = st.date_input("تاریخ جوائننگ (Date of Joining):", min_value=datetime(2010, 1, 1)) # Historical date fix
            w_dept = st.selectbox("ڈپارٹمنٹ:", ["PRODUCTION", "STORE", "QUALITY", "MAINTENANCE", "ADMIN"])
            
            st.markdown("#### چھٹیوں کا کوٹا (Initial Quota)")
            q_cl = st.number_input("Casual Leave Balance (CL):", min_value=0, value=0)
            q_sl = st.number_input("Sick Leave Balance (SL):", min_value=0, value=0)
            q_al = st.number_input("Annual Leave Balance (AL):", min_value=0, value=0)
            q_co = st.number_input("Compensation Leave Balance (CO):", min_value=0, value=0)
            
            submitted = st.form_submit_button("رجسٹر کریں اور شیٹ پر بھیجیں")
            
            if submitted and w_name and w_id:
                new_worker_payload = {
                    "name": str(w_name), "id": str(w_id), "cnic": str(w_cnic), "father_name": str(w_father),
                    "mobile": str(w_mobile), "salary": int(w_salary), "joining_date": str(w_join),
                    "end_date": "-", "department": str(w_dept), "password": "123", "photo": "",
                    "CL": int(q_cl), "Sick": int(q_sl), "Annual": int(q_al), "CO": int(q_co)
                }
                if send_data_to_sheet(new_worker_payload, "Worker"):
                    st.rerun()
