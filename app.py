import streamlit as st
from datetime import datetime, date
import json
import os

# 1. Page Config
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

# Main Header Banner (Exact match to your image template)
st.markdown("""
    <div style="background-color: #0f3994; padding: 20px; border-radius: 8px; text-align: center; border-bottom: 6px solid #e0a924; margin-bottom: 20px;">
        <h1 style="color: white; margin: 0; font-size: 38px; font-weight: bold; font-family: 'Arial';">🏭 INSTAPLAST PVT LTD</h1>
        <p style="color: #e0a924; margin: 5px 0 0 0; font-size: 18px; font-weight: bold; font-family: 'Arial';">Time Management & Leave Allocation System</p>
    </div>
""", unsafe_allowed_html=True)

# System Broadcast Dashboard (Green Notification Strip from your template)
st.markdown("""
    <div style="background-color: #00965e; padding: 12px; border-radius: 6px; color: white; font-weight: bold; margin-bottom: 25px; border-left: 5px solid #004d31;">
        📢 System Broadcast Dashboard: <span style="font-weight: normal; opacity: 0.9;">Permanent database registry synced successfully.</span>
    </div>
""", unsafe_allowed_html=True)

# Sidebar (Gate Panel Custom Styling)
st.sidebar.markdown("""
    <div style="background-color: #0f3994; padding: 12px; border-radius: 6px; text-align: center; color: white; font-weight: bold; border-bottom: 3px solid #e0a924; margin-bottom: 15px;">
        🔒 INSTAPLAST<br>Gate Panel
    </div>
""", unsafe_allowed_html=True)
access_role = st.sidebar.selectbox("Select Access Role:", ["Worker", "Admin Portal"])
st.sidebar.markdown("---")
st.sidebar.caption("⚡ Powered by INSTAPLAST Engine v5.0")

# ==========================================
# WORKER PORTAL
# ==========================================
if access_role == "Worker":
    # Main Container Header
    st.markdown("""
        <div style="background-color: #1d70b8; padding: 10px 15px; border-radius: 6px 6px 0px 0px; color: white; font-weight: bold; font-size: 18px;">
            👤 Employee Identity Verification & Leave Application
        </div>
    """, unsafe_allowed_html=True)
    
    # Outer light blue card wrapper box
    with st.container(border=True):
        if not st.session_state.workers_dict:
            st.warning("⚠️ ڈیش بورڈ پر کوئی ورکر موجود نہیں ہے۔ برائے مہربانی ایڈمن پینل سے پہلے ورکرز کا ڈیٹا داخل کریں۔")
        else:
            worker_list = list(st.session_state.workers_dict.keys())
            
            col_sel1, col_sel2 = st.columns(2)
            with col_sel1:
                selected_worker = st.selectbox("Profile / Select Profile Name:", worker_list)
            with col_sel2:
                cnic_token = st.text_input("Enter Identity Token (CNIC without dashes):", type="password")
            
            if cnic_token:
                actual_cnic = st.session_state.workers_dict[selected_worker].get("cnic", "")
                if cnic_token == actual_cnic:
                    st.success(f"🔓 Verification Successful. Welcome, {selected_worker}!")
                    
                    w_data = st.session_state.workers_dict[selected_worker]
                    cl_val = int(w_data.get("CL", 0))
                    sl_val = int(w_data.get("Sick", 0))
                    al_val = int(w_data.get("Annual", 0))
                    co_val = int(w_data.get("CO", 0))
                    
                    # Layout separation for Leaves and Form
                    st.markdown("<hr>", unsafe_allowed_html=True)
                    
                    col_left_form, col_right_cards = st.columns([1.1, 0.9])
                    
                    with col_left_form:
                        st.markdown("""
                            <div style="background-color: #0f3994; padding: 8px; border-radius: 5px; color: white; font-weight: bold; text-align: center; margin-bottom: 15px;">
                                Leave Application Form
                            </div>
                        """, unsafe_allowed_html=True)
                        leave_type = st.selectbox("Select Leave Type Category:", ["Casual Leave (CL)", "Sick Leave", "Annual Leave", "Compensation (CO)"])
                        leave_days = st.number_input("Number of Leave Days Required:", min_value=1, max_value=30, value=1)
                        reason = st.text_area("State Reason for Leave:")
                        
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
                                st.success("✅ آپ کی درخواست ایڈمن پینل کو بھیج دی گئی ہے۔ جیسے ہی ایڈمن 'Okay' کریں گے، بیلنس کٹ جائے گا۔")
                                st.rerun()
                            else:
                                st.error("❌ Request Rejected: Insufficient leave balance available!")
                    
                    with col_right_cards:
                        st.markdown("<p style='font-weight: bold; margin-bottom: 5px; color:#333;'>Live Available Leave Tracks</p>", unsafe_allowed_html=True)
                        
                        # Colorful Progress-Bar-Style Metrics based on your layout image
                        st.markdown(f"""
                            <div style="margin-bottom: 12px; background-color: #f1f5f9; padding: 10px; border-radius: 6px; border-left: 5px solid #00965e;">
                                <span style="font-weight: bold; color: #333;">Casual Leave (CL):</span> 
                                <span style="float: right; font-weight: bold; color: #00965e;">{cl_val} Days Available</span>
                                <div style="background-color: #e2e8f0; border-radius: 4px; height: 12px; margin-top: 5px; overflow: hidden;">
                                    <div style="background-color: #00965e; width: {min(100, max(0, cl_val*10))}%; height: 100%;"></div>
                                </div>
                            </div>
                            
                            <div style="margin-bottom: 12px; background-color: #f1f5f9; padding: 10px; border-radius: 6px; border-left: 5px solid #ea580c;">
                                <span style="font-weight: bold; color: #333;">Sick Leave:</span> 
                                <span style="float: right; font-weight: bold; color: #ea580c;">{sl_val} Days Available</span>
                                <div style="background-color: #e2e8f0; border-radius: 4px; height: 12px; margin-top: 5px; overflow: hidden;">
                                    <div style="background-color: #ea580c; width: {min(100, max(0, sl_val*12))}%; height: 100%;"></div>
                                </div>
                            </div>
                            
                            <div style="margin-bottom: 12px; background-color: #f1f5f9; padding: 10px; border-radius: 6px; border-left: 5px solid #8b5cf6;">
                                <span style="font-weight: bold; color: #333;">Annual Leave:</span> 
                                <span style="float: right; font-weight: bold; color: #8b5cf6;">{al_val} Days Available</span>
                                <div style="background-color: #e2e8f0; border-radius: 4px; height: 12px; margin-top: 5px; overflow: hidden;">
                                    <div style="background-color: #8b5cf6; width: {min(100, max(0, al_val*7))}%; height: 100%;"></div>
                                </div>
                            </div>

                            <div style="margin-bottom: 12px; background-color: #f1f5f9; padding: 10px; border-radius: 6px; border-left: 5px solid #0f3994;">
                                <span style="font-weight: bold; color: #333;">Compensation (CO):</span> 
                                <span style="float: right; font-weight: bold; color: #0f3994;">{co_val} Days Available</span>
                                <div style="background-color: #e2e8f0; border-radius: 4px; height: 12px; margin-top: 5px; overflow: hidden;">
                                    <div style="background-color: #0f3994; width: {min(100, max(0, co_val*20))}%; height: 100%;"></div>
                                </div>
                            </div>
                        """, unsafe_allowed_html=True)
                else:
                    st.error("❌ Incorrect Identity Token (CNIC). Access Denied.")

# ==========================================
# ADMIN PORTAL
# ==========================================
else:
    st.markdown("""
        <div style="background-color: #1d70b8; padding: 10px 15px; border-radius: 6px 6px 0px 0px; color: white; font-weight: bold; font-size: 18px;">
            🛠️ Admin Management Control Panel
        </div>
    """, unsafe_allowed_html=True)
    
    with st.container(border=True):
        admin_tab, requests_tab = st.tabs(["👥 Manage Workers Profiles", "📥 Pending Leave Requests"])
        
        with admin_tab:
            st.markdown("#### ➕ Register New Factory Worker")
            col_inp1, col_inp2 = st.columns(2)
            with col_inp1:
                w_name = st.text_input("Worker Full Name:")
                w_cnic = st.text_input("ID Card Number / CNIC (No Dashes):")
            with col_inp2:
                w_mobile = st.text_input("Mobile / WhatsApp Number:")
                w_joining = st.date_input("Date of Joining Company:", value=date.today())
            
            st.markdown("##### Set Initial Leave Allocations")
            bal1, bal2, bal3, bal4 = st.columns(4)
            with bal1: c_cl = st.number_input("Casual (CL) Initial Set:", min_value=0, value=10)
            with bal2: c_sl = st.number_input("Sick Initial Set:", min_value=0, value=8)
            with bal3: c_al = st.number_input("Annual Initial Set:", min_value=0, value=14)
            with bal4: c_co = st.number_input("Compensation (CO) Initial Set:", min_value=0, value=0)
            
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
                    st.success(f"💾 Profile for '{w_name}' successfully saved and synced!")
                    st.rerun()
                else:
                    st.error("❌ Validation Error: Name and CNIC fields are required.")
                    
            if st.session_state.workers_dict:
                st.markdown("<hr>", unsafe_allowed_html=True)
                st.markdown("#### 🗑️ Remove Profile From Records")
                worker_to_delete = st.selectbox("Select Worker to Remove:", ["Select Worker"] + list(st.session_state.workers_dict.keys()))
                if worker_to_delete != "Select Worker":
                    if st.button(f"Permanently Delete {worker_to_delete}", use_container_width=True):
                        del st.session_state.workers_dict[worker_to_delete]
                        st.session_state.leave_requests = [r for r in st.session_state.leave_requests if r["worker"] != worker_to_delete]
                        save_permanent_data()
                        st.success(f"🗑️ Profile data for '{worker_to_delete}' has been completely wiped.")
                        st.rerun()

            if st.session_state.workers_dict:
                st.markdown("<hr>", unsafe_allowed_html=True)
                st.markdown("#### 📋 Factory Database Master Sheet View")
                st.json(st.session_state.workers_dict)

        with requests_tab:
            st.markdown("#### 📥 Incoming Leave Applications Queue")
            pending_reqs = [r for r in st.session_state.leave_requests if r["status"] == "Pending"]
            
            if not pending_reqs:
                st.info("🛋️ All clear! No pending leave applications found in the queue.")
            else:
                for req in pending_reqs:
                    st.markdown(f"""
                        <div style="background-color: white; padding: 15px; border-radius: 6px; border-left: 6px solid #e0a924; box-shadow: 0 2px 4px rgba(0,0,0,0.05); margin-bottom: 15px; border: 1px solid #e2e8f0; border-left: 6px solid #e0a924;">
                            <strong style="color: #0f3994; font-size: 16px;">👤 Worker Name: {req['worker']}</strong><br>
                            <span style="color: #334155;"><b>Leave Type:</b> {req['leave_type']} | <b>Duration:</b> <span style="color: #b91c1c; font-weight: bold;">{req['days']} Days</span></span><br>
                            <span style="color: #64748b; font-size: 13px;"><b>Date Received:</b> {req['date']}</span><br>
                            <div style="background-color: #f8fafc; padding: 10px; border-radius: 5px; margin-top: 8px; color: #475569; font-style: italic; border: 1px dashed #cbd5e1;">"Reason: {req['reason']}"</div>
                        </div>
                    """, unsafe_allowed_html=True)
                    
                    col_app, col_rej = st.columns(2)
                    with col_app:
                        if st.button(f"✅ Okay / Approve (ID: {req['id']})", key=f"app_{req['id']}", use_container_width=True):
                            w_name = req['worker']
                            l_key = req['leave_type']
                            days_to_cut = int(req['days'])
                            
                            if w_name in st.session_state.workers_dict:
                                current_bal = int(st.session_state.workers_dict[w_name].get(l_key, 0))
                                if current_bal >= days_to_cut:
                                    st.session_state.workers_dict[w_name][l_key] -= days_to_cut
                                    req["status"] = "Approved"
                                    save_permanent_data()
                                    st.success(f"👍 Approved! {days_to_cut} days deducted from {w_name}.")
                                    st.rerun()
                                else:
                                    st.error("❌ Error: Worker does not have sufficient balance.")
                            else:
                                st.error("❌ Error: Worker profile not found.")
                    
                    with col_rej:
                        if st.button(f"❌ Reject / Cancel (ID: {req['id']})", key=f"rej_{req['id']}", use_container_width=True):
                            req["status"] = "Rejected"
                            save_permanent_data()
                            st.warning("⚠️ Application Rejected. Leave balances unchanged.")
                            st.rerun()
                    st.markdown("<br>", unsafe_allowed_html=True)
