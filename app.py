import streamlit as st
from datetime import datetime, date, timedelta
import base64
import json
import requests
import pandas as pd
import calendar

# Page Setup
st.set_page_config(page_title="INSTAPLAST Leave Portal", page_icon="🏭", layout="wide")

ADMIN_PASSWORD = "admin123"  

# --- 🌐 LIVE GOOGLE APPS SCRIPT API CONFIGURATION ---
API_URL = "https://script.google.com/macros/s/AKfycbwuE4FtMg-hpiQm_HHFetdXEsIXTXTKNuauHQi0RCFAXd9mqfN034KI50EYRxxXxBKl/exec"
SHEET_ID = "1UjhsblmHa9UoUsbkx9-OYc98rXRcqToTJDdBAHZDciI"
GSHEET_WORKER_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Worker"
GSHEET_REQUESTS_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Requests"

# --- 📥 CLOUD DATA LOADING LOGIC ---
def load_cloud_database(force_refresh=False):
    if force_refresh or "workers_dict" not in st.session_state:
        try:
            workers_df = pd.read_csv(GSHEET_WORKER_URL)
            temp_workers = {}
            if not workers_df.empty:
                for _, row in workers_df.iterrows():
                    w_name = row.get('name')
                    if pd.notna(w_name) and str(w_name).strip() != "" and str(w_name).strip().lower() != "nan":
                        w_name_str = str(w_name).strip()
                        temp_workers[w_name_str] = {
                            "id": str(row.get('id', '')).split('.')[0].strip(),
                            "cnic": str(row.get('cnic', '')).split('.')[0].strip(),
                            "father_name": str(row.get('father_name', 'N/A')).strip(),
                            "mobile": str(row.get('mobile', '')).split('.')[0].strip(),
                            "salary": str(row.get('salary', '0')).strip(),
                            "joining_date": str(row.get('joining_date', '')).strip(),
                            "end_date": str(row.get('end_date', '-')).strip(),
                            "department": str(row.get('department', 'STORE')).strip(),
                            "password": str(row.get('password', '123')).strip(),
                            "photo": str(row.get('photo', '')) if pd.notna(row.get('photo')) else "",
                            "CL": int(row.get('CL', 0)) if pd.notna(row.get('CL')) else 0,
                            "Sick": int(row.get('Sick', 0)) if pd.notna(row.get('Sick')) else 0,
                            "Annual": int(row.get('Annual', 0)) if pd.notna(row.get('Annual')) else 0,
                            "CO": int(row.get('CO', 0)) if pd.notna(row.get('CO')) else 0
                        }
            st.session_state.workers_dict = temp_workers
        except: st.session_state.workers_dict = {}

    if force_refresh or "leave_requests" not in st.session_state:
        try:
            requests_df = pd.read_csv(GSHEET_REQUESTS_URL)
            temp_reqs = []
            if not requests_df.empty:
                for idx, row in requests_df.iterrows():
                    w_name = row.get('worker')
                    if pd.notna(w_name) and str(w_name).strip() != "" and str(w_name).strip().lower() != "nan":
                        temp_reqs.append({
                            "id": str(row.get('id', idx+1)).split('.')[0].strip(),
                            "worker": str(w_name).strip(),
                            "leave_type": str(row.get('leave_type', 'CL')).strip(),
                            "days": int(row.get('days', 1)) if pd.notna(row.get('days')) else 1,
                            "date_from": str(row.get('date_from', '')).strip(),
                            "date_to": str(row.get('date_to', '')).strip(),
                            "reason": str(row.get('reason', '-')).strip(),
                            "applied_on": str(row.get('applied_on', '')).strip(),
                            "status": str(row.get('status', 'Pending')).strip()
                        })
            st.session_state.leave_requests = temp_reqs
        except: st.session_state.leave_requests = []

# --- 📤 CLOUD DATA SYNC LOGIC (UPDATED FOR UPDATE/APPEND) ---
def sync_data_to_sheet(payload_data, sheet_name, action="APPEND"):
    try:
        # Action 'UPDATE' کا اضافہ کر دیا گیا ہے تاکہ پرانی لائن ہی اپ ڈیٹ ہو
        payload = {"sheet": sheet_name, "data": payload_data, "action": action}
        response = requests.post(API_URL, json=payload, headers={"Content-Type": "application/json"})
        return response.status_code == 200
    except: return False

load_cloud_database()

# [CSS Styles and Profile functions remain same as your file...]
# (باقی ڈیزائن اور فنکشنز آپ کی فائل والے ہی ہیں، صرف اوپر والا sync فنکشن تبدیل ہوا ہے)

# --- TAB 3: LEAVE REQUESTS QUEUE (UPDATED) ---
# (یہ حصہ اپنے کوڈ میں ریپلیس کر لیں)
with requests_tab:
    st.html("<h4>📥 Incoming Leave Applications Queue</h4>")
    if st.button("🔄 Refresh Data From Cloud", use_container_width=True):
        load_cloud_database(force_refresh=True)
        st.rerun()
        
    pending_reqs = [r for r in st.session_state.leave_requests if str(r.get("status", "Pending")).strip().lower() == "pending"]
    
    if not pending_reqs: 
        st.info("🛋️ No pending leave applications.")
    else:
        for idx, req in enumerate(pending_reqs):
            with st.container(border=True):
                st.write(f"👤 **Worker Name:** {req['worker']} | 📋 **Leave Category:** {req['leave_type']} ({req['days']} Days)")
                col_app, col_rej = st.columns(2)
                
                with col_app:
                    if st.button(f"✅ Approve {req['worker']}", key=f"app_{idx}"):
                        if req['worker'] in st.session_state.workers_dict:
                            w_info = st.session_state.workers_dict[req['worker']]
                            w_info[req['leave_type']] = int(w_info.get(req['leave_type'], 0)) - int(req['days'])
                            sync_data_to_sheet(w_info, "Worker", action="UPDATE")
                        
                        req["status"] = "Approved"
                        # یہاں action='UPDATE' استعمال ہو رہا ہے
                        if sync_data_to_sheet(req, "Requests", action="UPDATE"):
                            load_cloud_database(force_refresh=True)
                            st.rerun()
                        
                with col_rej:
                    if st.button(f"❌ Reject {req['worker']}", key=f"rej_{idx}"):
                        req["status"] = "Rejected"
                        if sync_data_to_sheet(req, "Requests", action="UPDATE"):
                            load_cloud_database(force_refresh=True)
                            st.rerun()
