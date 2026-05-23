import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime

# Page Configuration & Professional Theme (Insta Plast Branding)
st.set_page_config(page_title="INSTAPLAST Leave Portal", page_icon="🏭", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #F8FAFC; }
    h1, h2, h3 { color: #1E3A8A !important; font-family: 'Segoe UI', sans-serif; font-weight: 700; }
    .stButton>button { background-color: #1E3A8A !important; color: white !important; border-radius: 6px !important; font-weight: bold !important; width: 100%; }
    .stButton>button:hover { background-color: #1D4ED8 !important; }
    .balance-box { background-color: white; padding: 15px; border-radius: 8px; border-left: 5px solid #1E3A8A; box-shadow: 0 2px 4px rgba(0,0,0,0.05); text-align: center; }
    </style>
""", unsafe_allow_html=True)

# 🔴 لائیو گوگل ایپس اسکرپٹ یو آر ایل
API_URL = "https://script.google.com/macros/s/AKfycbyIvA-XxT1qpezKEU2-DXze6eqEhEGtJmZIM14TbpQVzmhVpVC3pM-DEXT3XJxXNIVf/exec"

# Google Sheet CSV Reading Links
SHEET_ID = "1UjhsblmHa9UoUsbkx9-OYc98rXRcqToTJDdBAHZDciI"
GSHEET_WORKER_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Worker"
GSHEET_REQUESTS_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Requests"

# --- CLOUD DATA FETCHING ---
def load_cloud_data(url, columns):
    try:
        return pd.read_csv(url)
    except Exception:
        return pd.DataFrame(columns=columns)

# --- SEND DATA TO GOOGLE SHEET ---
def send_data_to_sheet(payload_data, sheet_name):
    try:
        payload = {"sheet": sheet_name, "data": payload_data}
        response = requests.post(API_URL, json=payload, headers={"Content-Type": "application/json"})
        if response.status_code == 200 and json.loads(response.text).get("status") == "success":
            st.success("✅ ڈیٹا کامیابی سے منتقل ہو گیا ہے! / Data Sync Successful!")
            return True
        else:
            st.error("❌ ایپس اسکرپٹ سنک میں مسئلہ ہے۔")
            return False
    except Exception as e:
        st.error(f"❌ نیٹ ورک ایرر: {str(e)}")
        return False

# Initialize Schemas
worker_cols = ["name", "id", "cnic", "father_name", "mobile", "salary", "joining_date", "end_date", "department", "password", "photo", "CL", "Sick", "Annual", "CO"]
req_cols = ["id", "worker", "leave_type", "days", "date_from", "date_to", "reason", "applied_on", "status"]

workers_df = load_cloud_data(GSHEET_WORKER_URL, worker_cols)
requests_df = load_cloud_data(GSHEET_REQUESTS_URL, req_cols)

# Clean ID Strings
for df in [workers_df, requests_df]:
    if not df.empty and 'id' in df.columns:
        df['id'] = df['id'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()

# Header
st.markdown("<h1 style='text-align: center;'>🏭 INSTAPLAST LEAVE MANAGEMENT SYSTEM</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #64748B;'>انسٹا پلاسٹ ورکرز پورٹل</p>", unsafe_allow_html=True)
st.markdown("---")

# Sidebar Role Selector
role = st.sidebar.selectbox("🔒 اپنا لاگ ان رول منتخب کریں (Select Role):", ["Worker Panel (ورکر پورٹل)", "Admin Dashboard (ایڈمن کنٹرول)"])

# ----------------- WORKER PANEL -----------------
if "Worker Panel" in role:
    st.subheader("👤 ورکر لاگ ان اور چھٹی کی درخواست")
    
    worker_id_input = st.text_input("🔑 اپنا ورکر آئی ڈی درج کریں (Search Worker ID):", placeholder="e.g., IPL-1020").strip()
    
    if worker_id_input:
        worker_match = workers_df[workers_df['id'] == worker_id_input]
        
        if not worker_match.empty:
            worker_data = worker_match.iloc[0]
            st.success(f"🔓 خوش آمدید (Welcome): {worker_data['name']}")
            
            # Leave Balances Visual Grid
            st.markdown("### 📊 آپ کی چھٹیوں کا بیلنس (Your Leave Balances)")
            b1, b2, b3, b4 = st.columns(4)
            with b1: st.markdown(f"<div class='balance-box'><h4>Casual Leave (CL)</h4><h2>{int(worker_data.get('CL', 0))}</h2><p>دن باقی</p></div>", unsafe_allow_html=True)
            with b2: st.markdown(f"<div class='balance-box'><h4>Sick Leave (SL)</h4><h2>{int(worker_data.get('Sick', 0))}</h2><p>دن باقی</p></div>", unsafe_allow_html=True)
            with b3: st.markdown(f"<div class='balance-box'><h4>Annual Leave (AL)</h4><h2>{int(worker_data.get('Annual', 0))}</h2><p>دن باقی</p></div>", unsafe_allow_html=True)
            with b4: st.markdown(f"<div class='balance-box'><h4>Compensation (CO)</h4><h2>{int(worker_data.get('CO', 0))}</h2><p>دن باقی</p></div>", unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            col_form, col_profile = st.columns([2, 1])
            
            with col_form:
                st.markdown("### 📝 چھٹی کا فارم / Leave Request")
                leave_type = st.selectbox("چھٹی کی قسم منتخب کریں (Leave Type):", ["Casual Leave (CL)", "Sick Leave (SL)", "Annual Leave (AL)", "Compensation (CO)"])
                
                c1, c2 = st.columns(2)
                date_from = c1.date_input("کب سے (From Date):", min_value=datetime(2010, 1, 1))
                date_to = c2.date_input("کب تک (To Date):", min_value=datetime(2010, 1, 1))
                
                days_required = st.number_input("کل مطلوبہ دن (Total Days Required):", min_value=1, value=1, step=1)
                reason = st.text_area("چھٹی کی وجہ (Reason for Leave):")
                
                if st.button("Submit Application (درخواست جمع کریں)"):
                    new_req = {
                        "id": str(worker_data['id']), "worker": str(worker_data['name']), "leave_type": str(leave_type),
                        "days": int(days_required), "date_from": str(date_from), "date_to": str(date_to),
                        "reason": str(reason), "applied_on": str(datetime.now().date()), "status": "Pending"
                    }
                    if send_data_to_sheet(new_req, "Requests"):
                        st.rerun()
                        
            with col_profile:
                st.markdown("### 📋 ورکر پروفائل کارڈ")
                st.info(f"""
                **نام (Name):** {worker_data['name']}  
                **والد کا نام (Father Name):** {worker_data['father_name']}  
                **ڈپارٹمنٹ (Department):** {worker_data['department']}  
                **تاریخ جوائننگ (Joining Date):** {worker_data['joining_date']}  
                """)
        else:
            st.error("❌ یہ ورکر آئی ڈی ریکارڈ میں موجود نہیں ہے۔ براہ کرم درست آئی ڈی درج کریں۔")

# ----------------- ADMIN DASHBOARD -----------------
elif "Admin Dashboard" in role:
    st.subheader("⚙️ کمپنی ایڈمن کنٹرول پینل")
    
    tab1, tab2, tab3 = st.tabs(["👥 ورکرز ڈائریکٹری (Worker Directory)", "📥 موصول شدہ درخواستیں (Pending Requests)", "➕ نیا ورکر رجسٹر کریں (Add Worker)"])
    
    with tab1:
        st.markdown("### 🔍 ورکرز ڈیٹا سرچ اور فلٹر")
        search_query = st.text_input("ورکر کا نام یا آئی ڈی لکھیں (Search by Name/ID):").strip().lower()
        
        if not workers_df.empty:
            if search_query:
                filtered_df = workers_df[workers_df['name'].astype(str).str.lower().str.contains(search_query) | workers_df['id'].astype(str).str.lower().str.contains(search_query)]
                st.dataframe(filtered_df, use_container_width=True)
            else:
                st.dataframe(workers_df, use_container_width=True)
        else:
            st.info("کوئی ڈیٹا دستیاب نہیں ہے۔")
            
    with tab2:
        st.markdown("### 📥 چھٹیوں کی پینڈنگ درخواستیں")
        st.caption("نوٹ: یہاں منظور کرنے پر ہی ورکر کے بیلنس سے چھٹی کٹے گی (کوئی ڈبل کٹنگ نہیں ہوگی)۔")
        
        if not requests_df.empty:
            pending_df = requests_df[requests_df['status'] == "Pending"]
            if not pending_df.empty:
                st.dataframe(pending_df, use_container_width=True)
            else:
                st.success("🎉 تمام درخواستیں نمٹائی جا چکی ہیں! کوئی پینڈنگ چھٹی نہیں ہے۔")
        else:
            st.info("درخواستوں کا ریکارڈ خالی ہے۔")
            
    with tab3:
        st.markdown("### ➕ نیا ورکر فارم")
        with st.form("new_worker_form"):
            col_a, col_b = st.columns(2)
            w_name = col_a.text_input("ورکر کا نام (Worker Name):")
            w_id = col_b.text_input("ورکر آئی ڈی (Worker ID):", placeholder="e.g., IPL-1025")
            w_father = col_a.text_input("والد کا نام (Father's Name):")
            w_cnic = col_b.text_input("CNIC نمبر:")
            w_mobile = col_a.text_input("موبائل نمبر (Mobile):")
            w_dept = col_b.selectbox("ڈپارٹمنٹ منتخب کریں:", ["PRODUCTION", "STORE", "QUALITY", "MAINTENANCE", "ADMIN"])
            w_salary = col_a.number_input("تنخواہ (Salary):", min_value=0, value=25000)
            w_join = col_b.date_input("تاریخ جوائننگ (Date of Joining):", min_value=datetime(2010, 1, 1))
            
            st.markdown("#### initial Leaves Quota (چھٹیوں کا کوٹا)")
            c_l1, c_l2, c_l3, c_l4 = st.columns(4)
            q_cl = c_l1.number_input("CL Quota:", min_value=0, value=12)
            q_sl = c_l2.number_input("Sick Quota:", min_value=0, value=8)
            q_al = c_l3.number_input("Annual Quota:", min_value=0, value=14)
            q_co = c_l4.number_input("CO Quota:", min_value=0, value=0)
            
            submit_btn = st.form_submit_button("رجسٹر کریں (Save Worker)")
            
            if submit_btn and w_name and w_id:
                worker_payload = {
                    "name": str(w_name), "id": str(w_id), "cnic": str(w_cnic), "father_name": str(w_father),
                    "mobile": str(w_mobile), "salary": int(w_salary), "joining_date": str(w_join),
                    "end_date": "-", "department": str(w_dept), "password": "123", "photo": "",
                    "CL": int(q_cl), "Sick": int(q_sl), "Annual": int(q_al), "CO": int(q_co)
                }
                if send_data_to_sheet(worker_payload, "Worker"):
                    st.rerun()
