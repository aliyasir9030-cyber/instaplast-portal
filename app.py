import streamlit as st
from datetime import datetime, date, timedelta
import base64
import json
import os

# Page Setup
st.set_page_config(page_title="INSTAPLAST Leave Portal", page_icon="🏭", layout="wide")

ADMIN_PASSWORD = "admin123"  

# --- 📌 ڈیٹا کو مستقل محفوظ (LOCK) کرنے کی لاجک ---
# یہ کوڈ خود بخود آپ کے کمپیوٹر کے ڈیسک ٹاپ کا پاتھ ڈھونڈ کر فائل وہاں بنائے گا
DESKTOP_PATH = os.path.join(os.path.expanduser("~"), "Desktop")
DB_FILE = os.path.join(DESKTOP_PATH, "instaplast_database.json")

def load_local_database():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                st.session_state.workers_dict = data.get("workers", {})
                st.session_state.leave_requests = data.get("requests", [])
                
                # ہارڈ ڈسک سے پرانا لاگ ان سیشن بحال کرنے کے لیے
                if "logged_in_user" not in st.session_state:
                    st.session_state.logged_in_user = data.get("active_worker_session", None)
                if "admin_authenticated" not in st.session_state:
                    st.session_state.admin_authenticated = data.get("active_admin_session", False)
                return
        except Exception as e:
            pass
    
    # اگر پہلی بار چل رہا ہو اور فائل نہ ہو
    if "workers_dict" not in st.session_state:
        st.session_state.workers_dict = {}
    if "leave_requests" not in st.session_state:
        st.session_state.leave_requests = []
    if "logged_in_user" not in st.session_state:
        st.session_state.logged_in_user = None
    if "admin_authenticated" not in st.session_state:
        st.session_state.admin_authenticated = False

def save_local_database():
    db_export = {
        "workers": st.session_state.workers_dict,
        "requests": st.session_state.leave_requests,
        "active_worker_session": st.session_state.get("logged_in_user", None),
        "active_admin_session": st.session_state.get("admin_authenticated", False)
    }
    try:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(db_export, f, indent=4, ensure_ascii=False)
    except Exception as e:
        st.error(f"Error saving data to Desktop: {e}")

# خود کار طریقے سے ڈیٹا لوڈ کرنا
load_local_database()

if "lang" not in st.session_state:
    st.session_state.lang = "English"

# Custom CSS for Professional UI and Fixing Logo Cutting Issue
st.html("""
<style>
    [data-testid="stHeader"] {
        display: none !important;
    }
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
    }
    .section-title {
        color: #1e3a8a;
        font-family: 'Segoe UI', Arial, sans-serif;
        font-weight: 700;
        border-bottom: 3px solid #e0a924;
        padding-bottom: 5px;
        margin-bottom: 15px;
    }
    .data-box {
        border-radius: 8px;
        padding: 20px;
        margin-top: 15px;
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
    }
    .urdu-text {
        font-family: 'Nafees', 'Jonamehr', 'Noto Nastaliq Urdu', sans-serif;
        direction: rtl;
        text-align: right;
    }
</style>
""")

# Image handling functions
def get_image_base64(uploaded_file):
    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()
        return base64.b64encode(bytes_data).decode()
    return None

def display_worker_photo(base64_str):
    if base64_str:
        st.markdown(f'<img src="data:image/png;base64,{base64_str}" style="width:130px; height:130px; border-radius:50%; object-fit:cover; border:3px solid #e0a924; display:block; margin-left:auto; margin-right:auto; margin-bottom:15px;">', unsafe_allow_html=True)
    else:
        st.markdown('<div style="width:130px; height:130px; border-radius:50%; background-color:#e2e8f0; border:3px dashed #cbd5e1; display:flex; align-items:center; justify-content:center; margin-left:auto; margin-right:auto; margin-bottom:15px; color:#64748b; font-weight:bold;">No Photo</div>', unsafe_allow_html=True)

# --- TOP BAR: BRANDING & LANGUAGE SWITCHER ---
lang_col1, lang_col2 = st.columns([4, 1])
with lang_col1:
    st.html("""
        <div style="background-color: #1e3a8a; padding: 30px 20px; border-radius: 12px; text-align: center; border-left: 8px solid #e0a924; margin-top: 10px;">
            <h1 style="color: #ffffff; margin: 0; font-size: 32px; font-family: 'Segoe UI', Arial, sans-serif; font-weight: bold; line-height: 1.4; letter-spacing: 1px;">🏭 INSTAPLAST PVT LTD</h1>
            <p style="color: #f1f5f9; margin: 10px 0 0 0; font-size: 15px; font-weight: 500; opacity: 0.95;">Time Management & Leave Allocation System</p>
        </div>
    """)
with lang_col2:
    st.write("")
    st.write("")
    st.write("")
    if st.session_state.lang == "English":
        if st.button("اردو میں تبدیل کریں 🇵🇰", use_container_width=True):
            st.session_state.lang = "Urdu"
            st.rerun()
    else:
        if st.button("Switch to English 🇬🇧", use_container_width=True):
            st.session_state.lang = "English"
            st.rerun()

is_urdu = (st.session_state.lang == "Urdu")

# Sidebar Navigation Control
st.sidebar.title("🔒 Gate Panel" if not is_urdu else "🔒 گیٹ پینل")
role_options = ["Worker", "Admin Portal"] if not is_urdu else ["ورکر پورٹل (Worker)", "ایڈمن پورٹل (Admin)"]
access_role = st.sidebar.selectbox("Select Access Role:" if not is_urdu else "رسائی کا طریقہ منتخب کریں:", role_options)
st.sidebar.divider()
st.sidebar.caption("⚡ Powered by INSTAPLAST Engine v15.0")

is_admin_mode = "Admin" in access_role

# Helper function for details subtabs
def render_profile_subdata(w_name, data, unique_key):
    st.write("---")
    st.markdown("### 📋 Detailed Profile Modules" if not is_urdu else "### 📋 پروفائل کی تفصیلات")
    
    cb1, cb2, cb3, cb4, cb5 = st.columns(5)
    with cb1: btn_personal = st.button("👤 Personal Data" if not is_urdu else "👤 ذاتی معلومات", key=f"btn_p_{unique_key}", use_container_width=True)
    with cb2: btn_job = st.button("💼 Job Data" if not is_urdu else "💼 نوکری کا ریکارڈ", key=f"btn_j_{unique_key}", use_container_width=True)
    with cb3: btn_time = st.button("⏱️ Time Management" if not is_urdu else "⏱️ حاضری و اوقات", key=f"btn_t_{unique_key}", use_container_width=True)
    with cb4: btn_benefit = st.button("🎁 Benefit & Goals" if not is_urdu else "🎁 مراعات و اہداف", key=f"btn_b_{unique_key}", use_container_width=True)
    with cb5: btn_payroll = st.button("💰 Payroll & Comp." if not is_urdu else "💰 تنخواہ کا ریکارڈ", key=f"btn_pay_{unique_key}", use_container_width=True)

    state_key = f"active_tab_{unique_key}"
    if state_key not in st.session_state:
        st.session_state[state_key] = "Personal Data"

    if btn_personal: st.session_state[state_key] = "Personal Data"
    if btn_job: st.session_state[state_key] = "Job Data"
    if btn_time: st.session_state[state_key] = "Time Management"
    if btn_benefit: st.session_state[state_key] = "Benefit"
    if btn_payroll: st.session_state[state_key] = "Payroll"

    active = st.session_state[state_key]
    
    if active == "Personal Data":
        st.markdown(f"""
        <div class="data-box {'urdu-text' if is_urdu else ''}" style="border-left: 5px solid #3b82f6; border-right: {'5px solid #3b82f6' if is_urdu else 'none'};">
            <h4 style="color:#1d4ed8;">{"👤 ذاتی معلومات کا ریکارڈ" if is_urdu else "👤 Personal Data Record"}</h4>
            <p><b>{"پورا نام" if is_urdu else "Full Name"}:</b> {w_name}</p>
            <p><b>{"والد کا نام" if is_urdu else "Father's Name"}:</b> {data.get('father_name', 'N/A')}</p>
            <p><b>{"شناختی کارڈ نمبر (پاسورڈ)" if is_urdu else "CNIC Number (System Password)"}:</b> {data.get('cnic', 'N/A')}</p>
            <p><b>{"موبائل / واٹس ایپ" if is_urdu else "Mobile / WhatsApp"}:</b> {data.get('mobile', 'N/A')}</p>
        </div>
        """, unsafe_allow_html=True)
        
    elif active == "Job Data":
        st.markdown(f"""
        <div class="data-box {'urdu-text' if is_urdu else ''}" style="border-left: 5px solid #10b981; border-right: {'5px solid #10b981' if is_urdu else 'none'};">
            <h4 style="color:#047857;">{"💼 فیکٹری نوکری کا ریکارڈ" if is_urdu else "💼 Job Data Record"}</h4>
            <p><b>{"ورکر آئی ڈی" if is_urdu else "Worker Registry ID"}:</b> {data.get('id', 'N/A')}</p>
            <p><b>{"شعبہ (Department)" if is_urdu else "Department Name"}:</b> {data.get('department', 'STORE')}</p>
            <p><b>{"شامل ہونے کی تاریخ" if is_urdu else "Official Date of Joining"}:</b> {data.get('joining_date', 'N/A')}</p>
            <p><b>{"معاہدے کی آخری تاریخ" if is_urdu else "Date of End (Contract End)"}:</b> {data.get('end_date', 'N/A')}</p>
        </div>
        """, unsafe_allow_html=True)
        
    elif active == "Time Management":
        st.markdown(f"""
        <div class="data-box {'urdu-text' if is_urdu else ''}" style="border-left: 5px solid #f59e0b; border-right: {'5px solid #f59e0b' if is_urdu else 'none'};">
            <h4 style="color:#b45309;">{"⏱️ اوقات کار اور حاضری" if is_urdu else "⏱️ Time Management & Attendance"}</h4>
            <p><b>{"مقرر کردہ شفٹ" if is_urdu else "Assigned Shift"}:</b> General Factory Shift</p>
            <p><b>{"شفٹ کے اوقات" if is_urdu else "Standard Shift Timings"}:</b> 08:00 AM - 05:00 PM</p>
            <p><b>{"کل منظور شدہ رخصت کا بیلنس" if is_urdu else "Total Approved Leave Balance"}:</b> {int(data.get('CL', 0)) + int(data.get('Sick', 0)) + int(data.get('Annual', 0)) + int(data.get('CO', 0))} {"دن" if is_urdu else "Days"}</p>
        </div>
        """, unsafe_allow_html=True)
        
    elif active == "Benefit":
        st.markdown(f"""
        <div class="data-box {'urdu-text' if is_urdu else ''}" style="border-left: 5px solid #8b5cf6; border-right: {'5px solid #8b5cf6' if is_urdu else 'none'};">
            <h4 style="color:#6d28d9;">{"🎁 مراعات اور کارکردگی" if is_urdu else "🎁 Benefits, Performance & Goals"}</h4>
            <p><b>{"کارکردگی کی صورتحال" if is_urdu else "Performance Status"}:</b> Good Standing</p>
            <p><b>{"میڈیکل کور انشورنس" if is_urdu else "Medical Cover Benefits"}:</b> Included (Standard Factory Grade Package)</p>
        </div>
        """, unsafe_allow_html=True)
        
    elif active == "Payroll":
        st.markdown(f"""
        <div class="data-box {'urdu-text' if is_urdu else ''}" style="border-left: 5px solid #ec4899; border-right: {'5px solid #ec4899' if is_urdu else 'none'};">
            <h4 style="color:#be185d;">{"💰 تنخواہ اور معاوضہ" if is_urdu else "💰 Payroll & Compensation"}</h4>
            <p><b>{"ماہانہ بنیادی تنخواہ" if is_urdu else "Basic Monthly Salary"}:</b> Rs. {data.get('salary', '0')}/-</p>
            <p><b>{"اضافی ڈیوٹی رخصت (CO)" if is_urdu else "Compensation Leave (CO) Allotment"}:</b> {data.get('CO', 0)} {"دن" if is_urdu else "Days"}</p>
        </div>
        """, unsafe_allow_html=True)

# ==========================================
# WORKER PORTAL INTERFACE
# ==========================================
if not is_admin_mode:
    title_text = "👤 ورکر شناختی تصدیق اور رخصت کی درخواست" if is_urdu else "👤 Employee Identity Verification & Leave Application"
    st.html(f"<h2 class='section-title'>{title_text}</h2>")
    
    if not st.session_state.workers_dict:
        st.warning("⚠️ No worker profiles found in the system database. Please switch to Admin Portal." if not is_urdu else "⚠️ سسٹم میں کوئی ورکر موجود نہیں ہے۔ براہ کرم ایڈمن پورٹل سے ورکر رجسٹر کریں۔")
    else:
        if st.session_state.logged_in_user is None:
            worker_list = list(st.session_state.workers_dict.keys())
            col_sel1, col_sel2 = st.columns(2)
            
            with col_sel1: 
                selected_worker = st.selectbox("Select Profile Name:" if not is_urdu else "اپنا نام منتخب کریں:", worker_list)
            with col_sel2: 
                password_input = st.text_input("Enter Password (Your CNIC Number):" if not is_urdu else "پاسورڈ درج کریں (اپنا شناختی کارڈ نمبر):", type="password")
                
            if st.button("🔒 Secure Login" if not is_urdu else "🔒 لاگ ان کریں", use_container_width=True):
                w_data = st.session_state.workers_dict[selected_worker]
                if str(password_input).strip() == str(w_data.get("cnic", "")).strip():
                    st.session_state.logged_in_user = selected_worker
                    save_local_database()  
                    st.success("✅ Logged in successfully!")
                    st.rerun()
                else:
                    st.error("❌ Incorrect Password. Please enter your correct CNIC number." if not is_urdu else "❌ پاسورڈ غلط ہے۔ براہ کرم صحیح شناختی کارڈ نمبر درج کریں۔")
        else:
            current_worker = st.session_state.logged_in_user
            
            if current_worker not in st.session_state.workers_dict:
                st.session_state.logged_in_user = None
                save_local_database()
                st.rerun()
                
            w_data = st.session_state.workers_dict[current_worker]
            
            l_out1, l_out2 = st.columns([3, 1])
            with l_out1:
                msg = f"🔓 Logged In Status: Active Session for '{current_worker}'" if not is_urdu else f"🔓 لاگ ان کی صورتحال: '{current_worker}' کا اکاؤنٹ کھلا ہے"
                st.success(msg)
            with l_out2:
                btn_lbl = "🚪 Log Out of System" if not is_urdu else "🚪 اکاؤنٹ لاگ آؤٹ کریں"
                if st.button(btn_lbl, use_container_width=True):
                    st.session_state.logged_in_user = None
                    save_local_database()  
                    st.rerun()
                    
            st.divider()
            
            dash_title = "📊 Your Live Progress Dashboard" if not is_urdu else "📊 آپ کی رخصت کا لائیو ڈیش بورڈ"
            st.html(f"<h3 class='section-title'>{dash_title}</h3>")
            cl_val, sl_val = int(w_data.get("CL", 0)), int(w_data.get("Sick", 0))
            al_val, co_val = int(w_data.get("Annual", 0)), int(w_data.get("CO", 0))
            
            col_c1, col_c2, col_c3, col_c4 = st.columns(4)
            with col_c1: st.metric(label="🟢 Casual Leave (CL)" if not is_urdu else "🟢 عام رخصت (CL)", value=f"{cl_val} {"دن" if is_urdu else "Days"}")
            with col_c2: st.metric(label="🟠 Sick Leave (SL)" if not is_urdu else "🟠 بیماری کی رخصت (SL)", value=f"{sl_val} {"دن" if is_urdu else "Days"}")
            with col_c3: st.metric(label="🔵 Annual Leave (AL)" if not is_urdu else "🔵 سالانہ رخصت (AL)", value=f"{al_val} {"دن" if is_urdu else "Days"}")
            with col_c4: st.metric(label="🔴 Compensation (CO)" if not is_urdu else "🔴 اضافی ڈیوٹی رخصت (CO)", value=f"{co_val} {"دن" if is_urdu else "Days"}")
            
            col_left_form, col_right_profile = st.columns([1.1, 0.9])
            
            with col_left_form:
                st.html(f"### 📝 {"رخصت کا فارم" if is_urdu else "Leave Application Form"}")
                leave_opts = ["Casual Leave (CL)", "Sick Leave (SL)", "Annual Leave (AL)", "Compensation (CO)"] if not is_urdu else ["عام رخصت (Casual Leave)", "بیماری کی رخصت (Sick Leave)", "سالانہ رخصت (Annual Leave)", "اضافی ڈیوٹی معاوضہ رخصت (CO)"]
                leave_type = st.selectbox("Select Leave Type:" if not is_urdu else "رخصت کی قسم منتخب کریں:", leave_opts)
                col_d1, col_d2 = st.columns(2)
                with col_d1: date_from = st.date_input("Leave From:" if not is_urdu else "کب سے:", value=date.today())
                with col_d2: date_to = st.date_input("Leave To:" if not is_urdu else "کب تک:", value=date.today())
                
                leave_days = st.number_input("Number of Days Required:" if not is_urdu else "کل کتنے دن کی چھٹی چاہیے:", min_value=1, max_value=30, value=1)
                reason = st.text_area("State Reason for Leave:" if not is_urdu else "چھٹی کی وجہ لکھیں:")
                
                if st.button("Apply Now (Submit Request)" if not is_urdu else "درخواست جمع کریں", use_container_width=True):
                    leave_key = "CL" if "Casual" in leave_type or "عام" in leave_type else "Sick" if "Sick" in leave_type or "بیماری" in leave_type else "Annual" if "Annual" in leave_type or "سالانہ" in leave_type else "CO"
                    if int(w_data.get(leave_key, 0)) >= leave_days:
                        new_req = {
                            "id": len(st.session_state.leave_requests) + 1,
                            "worker": current_worker, "leave_type": leave_key, "days": leave_days,
                            "date_from": str(date_from), "date_to": str(date_to), "reason": reason,
                            "applied_on": str(date.today()), "status": "Pending"
                        }
                        st.session_state.leave_requests.append(new_req)
                        save_local_database()  
                        st.success("✅ Application submitted successfully!" if not is_urdu else "✅ درخواست کامیابی کے ساتھ جمع ہو گئی ہے!")
                        st.rerun()
                    else:
                        st.error("❌ Request Rejected: Insufficient leave balance!" if not is_urdu else "❌ درخواست مسترد: آپ کے پاس چھٹیوں کا بیلنس کم ہے!")
                        
            with col_right_profile:
                st.html(f"### 🌟 {"ورکر کارپوریٹ پروفائل" if is_urdu else "Worker Corporate Profile"}")
                display_worker_photo(w_data.get("photo"))
                st.write(f"👤 **{"نام" if is_urdu else "Name"}:** {current_worker}")
                st.write(f"🏭 **{"شعبہ" if is_urdu else "Department"}:** {w_data.get('department', 'STORE')}")
                st.write(f"🆔 **{"آئی ڈی" if is_urdu else "ID"}:** {w_data.get('id', 'N/A')}")
                
                render_profile_subdata(current_worker, w_data, "worker_view")

# ==========================================
# ADMIN PORTAL INTERFACE
# ==========================================
else:
    st.html("<h2 class='section-title'>🛠️ Admin Management Control Panel</h2>")
    
    if not st.session_state.admin_authenticated:
        admin_auth = st.text_input("Enter Admin Security Password:", type="password")
        if st.button("🔒 Verify Admin Access", use_container_width=True):
            if admin_auth == ADMIN_PASSWORD:
                st.session_state.admin_authenticated = True
                save_local_database()
                st.rerun()
            else:
                st.error("❌ Incorrect Password.")
    else:
        adm_row1, adm_row2 = st.columns([3, 1])
        with adm_row1:
            st.success("🔓 Authorized Access Status: Live Session Open")
        with adm_row2:
            if st.button("🚪 Lock Admin Panel (Log Out)", use_container_width=True):
                st.session_state.admin_authenticated = False
                save_local_database()
                st.rerun()
                
        st.divider()

        with st.container(border=True):
            admin_tab, edit_tab, requests_tab, records_tab = st.tabs([
                "👥 Register & Delete Workers", "✏️ Edit Worker Profiles", "📥 Leave Requests Queue", "📊 Complete Factory Sheets"
            ])
            
            # TAB 1: REGISTER WORKERS
            with admin_tab:
                st.html("<h4>➕ Register New Factory Worker Profile</h4>")
                col_p1, col_p2, col_p3 = st.columns(3)
                with col_p1:
                    w_id = st.text_input("Worker ID / Roll No:")
                    w_name = st.text_input("Worker Full Name:")
                    w_father = st.text_input("Father's Name:")
                with col_p2:
                    w_cnic = st.text_input("ID Card Number / CNIC:")
                    w_mobile = st.text_input("Mobile / WhatsApp Number:")
                    w_salary = st.text_input("Monthly Salary (Rs.):", value="0")
                with col_p3:
                    w_dept = st.text_input("Department Name (e.g., Production, Store):", value="STORE")
                    w_joining = st.date_input("Date of Joining Company:", value=date.today(), min_value=date(1980,1,1))
                    w_end = st.date_input("Date of End (Contract End):", value=date.today() + timedelta(days=365), min_value=date(1980,1,1))
                    w_photo = st.file_uploader("Upload Worker Photo:", type=["jpg", "jpeg", "png"])
                
                st.html("<h5>📊 Initial Leave Quota Allocation</h5>")
                col_l1, col_l2, col_l3, col_l4 = st.columns(4)
                with col_l1: cl_q = st.number_input("Casual Leave (CL):", value=0, key="reg_cl")
                with col_l2: sl_q = st.number_input("Sick Leave (SL):", value=0, key="reg_sl")
                with col_l3: al_q = st.number_input("Annual Leave (AL):", value=0, key="reg_al")
                with col_l4: co_q = st.number_input("Compensation (CO):", value=0, key="reg_co")
                
                if st.button("Save Profile & Commit Registry", use_container_width=True):
                    if w_name and w_cnic and w_id:
                        photo_b64 = get_image_base64(w_photo)
                        st.session_state.workers_dict[w_name] = {
                            "id": w_id, "cnic": w_cnic, "father_name": w_father, "mobile": w_mobile,
                            "salary": w_salary, "joining_date": str(w_joining), "end_date": str(w_end),
                            "department": w_dept, "password": w_cnic, "photo": photo_b64, 
                            "CL": cl_q, "Sick": sl_q, "Annual": al_q, "CO": co_q
                        }
                        save_local_database()  
                        st.success(f"💾 Profile for '{w_name}' saved permanently to Desktop!")
                        st.rerun()

            # TAB 2: EDIT PROFILES
            with edit_tab:
                st.html("<h4>✏️ Audit & Edit Worker Balances / Profiles</h4>")
                if st.session_state.workers_dict:
                    edit_worker_name = st.selectbox("Select Worker to Edit:", ["Select Worker"] + list(st.session_state.workers_dict.keys()))
                    if edit_worker_name != "Select Worker":
                        current_w_data = st.session_state.workers_dict[edit_worker_name]
                        
                        try: saved_end_dt = datetime.strptime(current_w_data.get("end_date", str(date.today())), '%Y-%m-%d').date()
                        except: saved_end_dt = date.today()
                            
                        col_e1, col_e2, col_e3 = st.columns(3)
                        with col_e1:
                            edit_id = st.text_input("Worker ID:", value=current_w_data.get("id", ""))
                            edit_father = st.text_input("Father Name:", value=current_w_data.get("father_name", ""))
                            edit_dept = st.text_input("Department:", value=current_w_data.get("department", "STORE"))
                        with col_e2:
                            edit_cnic = st.text_input("CNIC Number:", value=current_w_data.get("cnic", ""))
                            edit_mobile = st.text_input("Mobile Number:", value=current_w_data.get("mobile", ""))
                            edit_salary = st.text_input("Monthly Salary:", value=current_w_data.get("salary", "0"))
                        with col_e3:
                            edit_joining = st.date_input("Joining Date:", value=datetime.strptime(current_w_data.get("joining_date", str(date.today())), '%Y-%m-%d').date(), min_value=date(1980,1,1), key="ed_j")
                            edit_end = st.date_input("Date of End (Contract End):", value=saved_end_dt, min_value=date(1980,1,1), key="ed_e")
                            edit_photo = st.file_uploader("Update New Photo (Optional):", type=["jpg", "png"])
                        
                        col_eb1, col_eb2, col_eb3, col_eb4 = st.columns(4)
                        with col_eb1: edit_cl = st.number_input("Casual Leave (CL):", value=int(current_w_data.get("CL", 0)), key="e_cl")
                        with col_eb2: edit_sl = st.number_input("Sick Leave (SL):", value=int(current_w_data.get("Sick", 0)), key="e_sl")
                        with col_eb3: edit_al = st.number_input("Annual Leave (AL):", value=int(current_w_data.get("Annual", 0)), key="e_al")
                        with col_eb4: edit_co = st.number_input("Compensation (CO):", value=int(current_w_data.get("CO", 0)), key="e_co")
                        
                        # ورکر پروفائل ڈیلیٹ کرنے کا آپشن
                        st.divider()
                        delete_worker = st.checkbox("⚠️ Check this box to DELETE this worker permanently from the system")
                        
                        if st.button("Update Profile & Save Changes", use_container_width=True):
                            if delete_worker:
                                del st.session_state.workers_dict[edit_worker_name]
                                save_local_database()
                                st.success(f"❌ Profile for '{edit_worker_name}' deleted permanently!")
                            else:
                                photo_str = get_image_base64(edit_photo) if edit_photo else current_w_data.get("photo")
                                st.session_state.workers_dict[edit_worker_name] = {
                                    "id": edit_id, "cnic": edit_cnic, "father_name": edit_father, "mobile": edit_mobile,
                                    "salary": edit_salary, "joining_date": str(edit_joining), "end_date": str(edit_end),
                                    "department": edit_dept, "password": edit_cnic, "photo": photo_str, 
                                    "CL": edit_cl, "Sick": edit_sl, "Annual": edit_al, "CO": edit_co
                                }
                                save_local_database()  
                                st.success("✅ Changes saved and data file auto-updated successfully on Desktop.")
                            st.rerun()

            # TAB 3: LEAVE REQUESTS QUEUE
            with requests_tab:
                st.html("<h4>📥 Incoming Leave Applications Queue</h4>")
                pending_reqs = [r for r in st.session_state.leave_requests if r["status"] == "Pending"]
                if not pending_reqs: st.info("🛋️ No pending leave applications.")
                else:
                    for req in pending_reqs:
                        with st.container(border=True):
                            st.write(f"👤 **Worker Name:** {req['worker']} | 📋 **Leave Category:** {req['leave_type']} ({req['days']} Days)")
                            st.write(f"📅 **Duration:** {req['date_from']} to {req['date_to']} | 📝 **Reason:** {req['reason']}")
                            col_app, col_rej = st.columns(2)
                            with col_app:
                                if st.button("✅ Approve Request", key=f"app_{req['id']}", use_container_width=True):
                                    st.session_state.workers_dict[req['worker']][req['leave_type']] -= int(req['days'])
                                    req["status"] = "Approved"
                                    save_local_database()  
                                    st.rerun()
                            with col_rej:
                                if st.button("❌ Reject Request", key=f"rej_{req['id']}", use_container_width=True):
                                    req["status"] = "Rejected"
                                    save_local_database()  
                                    st.rerun()

            # TAB 4: COMPLETE SHEETS RECORD
            with records_tab:
                st.html("<h4>📊 Factory Workers Sheets & Search Panel</h4>")
                search_query = st.text_input("🔍 Search Worker by Name, ID or Department:", "", key="adm_search").lower()
                
                if not st.session_state.workers_dict:
                    st.info("No workers registered in the platform yet.")
                else:
                    for name, details in st.session_state.workers_dict.items():
                        match_name = search_query in name.lower()
                        match_id = search_query in str(details.get('id', '')).lower()
                        match_dept = search_query in str(details.get('department', '')).lower()
                        
                        if match_name or match_id or match_dept:
                            with st.expander(f"📋 Profile: {name} (ID: {details.get('id', 'N/A')} | Dept: {details.get('department', 'N/A')})"):
                                col_v1, col_v2, col_v3 = st.columns([0.6, 1.4, 1.4])
                                with col_v1: display_worker_photo(details.get("photo"))
                                with col_v2:
                                    st.write(f"🧔 **Father's Name:** {details.get('father_name', 'N/A')}")
                                    st.write(f"🆔 **CNIC / Password:** {details.get('cnic', 'N/A')}")
                                    st.write(f"📱 **Mobile:** {details.get('mobile', 'N/A')}")
                                with col_v3:
                                    st.write(f"🏢 **Department:** {details.get('department', 'STORE')}")
                                    st.write(f"📅 **Date of Joining:** {details.get('joining_date', 'N/A')}")
                                    st.write(f"⏳ **Date of End:** {details.get('end_date', 'N/A')}")
                                    st.write(f"💰 **Monthly Salary:** Rs. {details.get('salary', '0')}/-")
                                
                                st.write(f"**Casual (CL):** {details.get('CL', 0)} Days | **Sick (SL):** {details.get('Sick', 0)} Days | **Annual (AL):** {details.get('Annual', 0)} Days | **CO:** {details.get('CO', 0)} Days")
                                
                                render_profile_subdata(name, details, f"admin_view_{details.get('id')}")
