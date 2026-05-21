import streamlit as st
from datetime import datetime, date
import json
import os

# Page Setup using native features
st.set_page_config(page_title="INSTAPLAST Leave Portal", page_icon="🏭", layout="wide")

DATA_FILE = "workers_data.json"

def load_permanent_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                data = json.load(f)
                if "workers" not in data: data["workers"] = {}
                if "requests" not in data: data["requests"] = []
                return data
        except:
            return {"workers": {}, "requests": []}
    return {"workers": {}, "requests": []}

def save_permanent_data():
    try:
        data_to_save = {
            "workers": st.session_state.workers_dict,
            "requests": st.session_state.leave_requests
        }
        with open(DATA_FILE, "w") as f:
            json.dump(data_to_save, f, indent=4)
    except Exception as e:
        st.error(f"Data Saving Error: {e}")

if "db_loaded" not in st.session_state:
    db = load_permanent_data()
    st.session_state.workers_dict = db["workers"]
    st.session_state.leave_requests = db["requests"]
    st.session_state.db_loaded = True

# Native App Headers (100% Safe from crashes)
st.title("🏭 INSTAPLAST PVT LTD")
st.subheader("Time Management & Leave Allocation System")
st.divider()

# Sidebar Setup
st.sidebar.title("🔒 Gate Panel")
access_role = st.sidebar.selectbox("Select Access Role:", ["Worker", "Admin Portal"])
st.sidebar.divider()
st.sidebar.caption("⚡ Powered by INSTAPLAST Engine v6.0")

# ==========================================
# WORKER PORTAL
# ==========================================
if access_role == "Worker":
    st.header("👤 Employee Identity Verification & Leave Application")
    
    with st.container(border=True):
        if not st.session_state.workers_dict:
            st.warning("⚠️ ڈیش بورڈ پر کوئی ورکر موجود نہیں ہے۔ برائے مہربانی ایڈمن پینل سے پہلے ورکرز کا ڈیٹا داخل کریں۔")
        else:
            worker_list = list(st.session_state.workers_dict.keys())
            
            col_sel1, col_sel2 = st.columns(2)
            with col_sel1:
                selected_worker = st.selectbox("Profile Name:", worker_list)
            with col_sel2:
                cnic_token = st.text_input("Enter Identity Token (CNIC):", type="password")
            
            if cnic_token:
                actual_cnic = st.session_state.workers_dict[selected_worker].get("cnic", "")
                if cnic_token == actual_cnic:
                    st.success(f"🔓 Welcome, {selected_worker}!")
                    st.divider()
                    
                    w_data = st.session_state.workers_dict[selected_worker]
                    cl_val = int(w_data.get("CL", 0))
                    sl_val = int(w_data.get("Sick", 0))
                    al_val = int(w_data.get("Annual", 0))
                    co_val = int(w_data.get("CO", 0))
                    
                    col_left_form, col_right_cards = st.columns([1.1, 0.9])
                    
                    with col_left_form:
                        st.subheader("📝 Leave Application Form")
                        leave_type = st.selectbox("Select Leave Type:", ["Casual Leave (CL)", "Sick Leave", "Annual Leave", "Compensation (CO)"])
                        leave_days = st.number_input("Number of Days:", min_value=1, max_value=30, value=1)
                        reason = st.text_area("State Reason:")
                        
                        if st.button("Apply Now (Submit Request)", use_container_width=True):
                            leave_key = "CL" if "Casual" in leave_type else "Sick" if "Sick" in leave_type else "Annual" if "Annual" in leave_type else "CO"
                            current_balance = int(w_data.get(leave_key, 0))
                            
                            if current_balance >= leave_days:
                                req_id = len(st.session_state.leave_requests) + 1
                                new_req = {
                                    "id": req_id,
                                    "worker": selected_worker,
                                    "leave_type": leave_key,
                                    "days": leave_days,
                                    "reason": reason,
                                    "date": str(date.today()),
                                    "status": "Pending"
                                }
                                st.session_state.leave_requests.append(new_req)
                                save_permanent_data()
                                st.success("✅ درخواست ایڈمن پینل کو بھیج دی گئی ہے۔")
                                st.rerun()
                            else:
                                st.error("❌ Request Rejected: Insufficient balance!")
                    
                    with col_right_cards:
                        st.subheader("📊 Available Leave Tracks")
                        
                        # Native colorful blocks using Streamlit's built-in badge alerts
                        st.success(f"🟢 **Casual Leave (CL):** {cl_val} Days Available")
                        st.warning(f"🟠 **Sick Leave:** {sl_val} Days Available")
                        st.info(f"🔵 **Annual Leave:** {al_val} Days Available")
                        st.error(f"🔴 **Compensation (CO):** {co_val} Days Available")
                else:
                    st.error("❌ Incorrect Identity Token.")

# ==========================================
# ADMIN PORTAL
# ==========================================
else:
    st.header("🛠️ Admin Management Control Panel")
    
    with st.container(border=True):
        admin_tab, requests_tab = st.tabs(["👥 Manage Workers Profiles", "📥 Pending Leave Requests"])
        
        with admin_tab:
            st.markdown("#### ➕ Register New Factory Worker")
            col_inp1, col_inp2 = st.columns(2)
            with col_inp1:
                w_name = st.text_input("Worker Full Name:")
                w_cnic = st.text_input("ID Card Number / CNIC:")
            with col_inp2:
                w_mobile = st.text_input("Mobile Number:")
                w_joining = st.date_input("Date of Joining:", value=date.today())
            
            bal1, bal2, bal3, bal4 = st.columns(4)
            with bal1: c_cl = st.number_input("Casual (CL):", min_value=0, value=10)
            with bal2: c_sl = st.number_input("Sick:", min_value=0, value=8)
            with bal3: c_al = st.number_input("Annual:", min_value=0, value=14)
            with bal4: c_co = st.number_input("Compensation (CO):", min_value=0, value=0)
            
            if st.button("Save Profile & Commit Registry", use_container_width=True):
                if w_name and w_cnic:
                    st.session_state.workers_dict[w_name] = {
                        "cnic": w_cnic,
                        "mobile": w_mobile,
                        "joining_date": str(w_joining),
                        "CL": int(c_cl),
                        "Sick": int(c_sl),
                        "Annual": int(c_al),
                        "CO": int(c_co)
                    }
                    save_permanent_data()
                    st.success(f"💾 Profile for '{w_name}' saved!")
                    st.rerun()
                    
            if st.session_state.workers_dict:
                st.divider()
                worker_to_delete = st.selectbox("Select Worker to Remove:", ["Select Worker"] + list(st.session_state.workers_dict.keys()))
                if worker_to_delete != "Select Worker":
                    if st.button(f"Permanently Delete {worker_to_delete}", use_container_width=True):
                        del st.session_state.workers_dict[worker_to_delete]
                        st.session_state.leave_requests = [r for r in st.session_state.leave_requests if r["worker"] != worker_to_delete]
                        save_permanent_data()
                        st.success(f"🗑️ Profile '{worker_to_delete}' wiped.")
                        st.rerun()

        with requests_tab:
            st.markdown("#### 📥 Incoming Leave Applications")
            pending_reqs = [r for r in st.session_state.leave_requests if r["status"] == "Pending"]
            
            if not pending_reqs:
                st.info("🛋️ No pending leave applications.")
            else:
                for req in pending_reqs:
                    with st.container(border=True):
                        st.write(f"👤 **Worker:** {req['worker']} | 📅 **Leave Type:** {req['leave_type']}")
                        st.write(f"⏳ **Days:** {req['days']} | 📝 **Reason:** {req['reason']}")
                        
                        col_app, col_rej = st.columns(2)
                        with col_app:
                            if st.button(f"✅ Approve (ID: {req['id']})", key=f"app_{req['id']}", use_container_width=True):
                                w_name = req['worker']
                                l_key = req['leave_type']
                                days_to_cut = int(req['days'])
                                if w_name in st.session_state.workers_dict:
                                    st.session_state.workers_dict[w_name][l_key] -= days_to_cut
                                    req["status"] = "Approved"
                                    save_permanent_data()
                                    st.success("Approved!")
                                    st.rerun()
                        with col_rej:
                            if st.button(f"❌ Reject (ID: {req['id']})", key=f"rej_{req['id']}", use_container_width=True):
                                req["status"] = "Rejected"
                                save_permanent_data()
                                st.warning("Rejected.")
                                st.rerun()
