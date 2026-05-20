import streamlit as st
from datetime import datetime, date
import calendar

# پیج کی بنیادی سیٹنگز اور کلر تھیم
st.set_page_config(page_title="INSTAPLAST Leave Portal", page_icon="🏭", layout="wide")

# کسٹم سی ایس ایس (CSS) ایپ کو خوبصورت اور کلر فل بنانے کے لیے
st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(135deg, #1E3A8A 0%, #0D9488 100%);
        padding: 30px;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        margin-bottom: 25px;
    }
    div[data-testid="stMetricSimpleValue"] {
        font-size: 24px !important;
        font-weight: bold !important;
        color: #1E3A8A !important;
    }
    .profile-card {
        background-color: #F8FAFC;
        padding: 20px;
        border-radius: 12px;
        border-left: 5px solid #1E3A8A;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    .month-card {
        background-color: #FFFFFF;
        padding: 15px;
        border-radius: 12px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.02);
    }
    </style>
""", unsafe_allow_html=True)

# 1. ڈمی ڈیٹا سیٹ کرنا (بشمول شناختی کارڈ نمبر اور لیو بیلنس)
if 'workers_list' not in st.session_state:
    st.session_state.workers_list = [
        {
            "id": "IP-1022",
            "cnic": "42101-1234567-1",
            "name": "Muhammad Raza-ul-Mustafa",
            "dept": "Utilities (Electrical & Instrumentation)",
            "shift": "G28SHIFT",
            "role": "Worker (ورکر)",
            "balances": {"annual_m": 8.0, "annual_nm": 9.0, "casual": 7.5, "compensatory": 4.0},
            "attendance": {5: "Casual Leave", 6: "Casual Leave", 10: "Present"} # ڈمی حاضری کارڈ کا ڈیٹا
        },
        {
            "id": "IP-1023",
            "cnic": "42101-7654321-3",
            "name": "Ali Ahmed",
            "dept": "Production",
            "shift": "A-SHIFT",
            "role": "Worker (ورکر)",
            "balances": {"annual_m": 10.0, "annual_nm": 6.0, "casual": 5.0, "compensatory": 2.0},
            "attendance": {1: "Present", 2: "Present", 15: "Annual Leave (M)"}
        }
    ]

DEPARTMENTS = [
    "Utilities (Electrical & Instrumentation)", "Production", "Mechanical", 
    "HR / Admin", "Quality Control", "Store / Logistics", "Finishing & Packing"
]

# 2. سائیڈ بار لاگ ان پینل
st.sidebar.markdown("<h2 style='text-align: center; color: #1E3A8A;'>🔒 INSTAPLAST<br>Login Panel</h2>", unsafe_allow_html=True)
st.sidebar.write("---")
user_role = st.sidebar.selectbox("Select Role / اپنا رول منتخب کریں", ["Worker (ورکر)", "Admin (ایڈمن)"])

is_admin_authenticated = False

if user_role == "Worker (ورکر)":
    worker_names = [w['name'] for w in st.session_state.workers_list]
    if not worker_names:
        st.sidebar.warning("کوئی ورکر موجود نہیں ہے۔")
    else:
        selected_worker_name = st.sidebar.selectbox("👤 Select Worker / ورکر منتخب کریں", worker_names)
        worker_data = next(w for w in st.session_state.workers_list if w['name'] == selected_worker_name)
else:
    # ایڈمن کے لیے پاس ورڈ پروٹیکشن
    admin_password = st.sidebar.text_input("Enter Admin Password / پاس ورڈ درج کریں", type="password")
    # آپ نیچے دیے گئے 'insta123' کو اپنی مرضی کے پاس ورڈ سے بدل سکتے ہیں
    if admin_password == "insta123":
        is_admin_authenticated = True
        st.sidebar.success("🔑 ایڈمن لاگ ان کامیاب!")
    elif admin_password != "":
        st.sidebar.error("❌ غلط پاس ورڈ! دوبارہ کوشش کریں۔")

# --- مین اسکرین ہیڈر ---
st.markdown("""
    <div class="main-header">
        <h1 style="color:white; margin:0; font-family: 'Arial Black', Gadget, sans-serif; letter-spacing: 2px;">🏭 INSTAPLAST PVT LTD</h1>
        <p style="color:#CCFBF1; margin:8px 0 0 0; font-size:18px; font-weight: 500;">Employee Leave Management Portal</p>
    </div>
""", unsafe_allow_html=True)

# --- اگر ورکر لاگ ان ہے ---
if user_role == "Worker (ورکر)" and worker_names:
    col1, col2 = st.columns([1.1, 2.1])
    
    with col1:
        st.markdown("<h3 style='color: #1E3A8A; border-bottom: 2px solid #1E3A8A; padding-bottom:5px;'>👤 ورکر پروفائل</h3>", unsafe_allow_html=True)
        st.markdown(f"""
        <div class="profile-card">
            <p style="margin:5px 0;"><b>نام:</b> {worker_data['name']}</p>
            <p style="margin:5px 0;"><b>شناختی کارڈ:</b> {worker_data['cnic']}</p>
            <p style="margin:5px 0;"><b>ورکر آئی ڈی:</b> {worker_data['id']}</p>
            <p style="margin:5px 0;"><b>شعبہ:</b> {worker_data['dept']}</p>
            <p style="margin:5px 0;"><b>شفٹ:</b> {worker_data['shift']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # --- ورکر کا پورے مہینے کا کارڈ (MONTHLY ATTENDANCE CARD) ---
        st.write("")
        st.markdown("<h4 style='color: #1E3A8A;'>📅 کرنٹ منتھ کارڈ</h4>", unsafe_allow_html=True)
        
        today = date.today()
        num_days = calendar.monthrange(today.year, today.month)[1]
        month_name = today.strftime("%B %Y")
        
        st.markdown(f"<p style='margin:0; color:#64748B;'><b>مہینہ:</b> {month_name}</p>", unsafe_allow_html=True)
        
        # مہینے کا ڈیٹا ٹیبل کی شکل میں تیار کرنا
        card_data = []
        for day in range(1, num_days + 1):
            current_date = date(today.year, today.month, day)
            day_name = current_date.strftime("%A") # دن کا نام (Monday, Tuesday وغیرہ)
            
            # چیک کرنا کہ اتوار ہے یا نہیں
            if day_name == "Sunday":
                status = "🔴 Weekly Off (اتوار)"
            else:
                status = worker_data.get("attendance", {}).get(day, "🟢 Present (حاضر)")
                
            card_data.append({"تاریخ (Date)": f"{day}/{today.month}", "دن (Day)": day_name, "اسٹیٹس (Status)": status})
            
        st.dataframe(card_data, use_container_width=True, height=300)
    
    with col2:
        st.markdown("<h3 style='color: #0D9488; border-bottom: 2px solid #0D9488; padding-bottom:5px;'>📊 لیو بیلنس (Leave Account Balances)</h3>", unsafe_allow_html=True)
        st.write("")
        b = worker_data["balances"]
        
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown("<div style='background-color:#EFF6FF; padding:10px; border-radius:8px; text-align:center; border:1px solid #BFDBFE;'><b>Annual (M)</b></div>", unsafe_allow_html=True)
            st.metric("", f"{b['annual_m']} Days")
        with c2:
            st.markdown("<div style='background-color:#ECFDF5; padding:10px; border-radius:8px; text-align:center; border:1px solid #A7F3D0;'><b>Annual (NM)</b></div>", unsafe_allow_html=True)
            st.metric("", f"{b['annual_nm']} Days")
        with c3:
            st.markdown("<div style='background-color:#FFFBEB; padding:10px; border-radius:8px; text-align:center; border:1px solid #FDE68A;'><b>Casual</b></div>", unsafe_allow_html=True)
            st.metric("", f"{b['casual']} Days")
        with c4:
            st.markdown("<div style='background-color:#FDF2F8; padding:10px; border-radius:8px; text-align:center; border:1px solid #FBCFE8;'><b>Compensatory</b></div>", unsafe_allow_html=True)
            st.metric("", f"{b['compensatory']} Days")

        st.write("---")
        
        # چھٹی اپلائی کرنے کا فارم
        st.markdown("<h4 style='color: #1E3A8A;'>📝 چھٹی اپلائی کریں (Apply For Leave)</h4>", unsafe_allow_html=True)
        leave_type = st.selectbox("چھٹی کی قسم (Leave Type)", ["Annual Leave (M)", "Annual Leave (NM)", "Casual Leave", "Compensatory Leave"])
        
        col_d1, col_d2 = st.columns(2)
        start_date = col_d1.date_input("شروع ہونے کی تاریخ (Start Date)")
        end_date = col_d2.date_input("آخری تاریخ (End Date)")
        
        if st.button("🚀 چھٹی کی درخواست سبمٹ کریں", use_container_width=True):
            if end_date >= start_date:
                days_requested = (end_date - start_date).days + 1
                
                map_leave = {
                    "Annual Leave (M)": "annual_m", "Annual Leave (NM)": "annual_nm", 
                    "Casual Leave": "casual", "Compensatory Leave": "compensatory"
                }
                b_key = map_leave[leave_type]
                
                if worker_data["balances"][b_key] >= days_requested:
                    worker_data["balances"][b_key] -= days_requested
                    
                    # ورکر کے منتھ کارڈ (حاضری کارڈ) میں چھٹی والے دنوں کو اپڈیٹ کرنا
                    if "attendance" not in worker_data:
                        worker_data["attendance"] = {}
                    
                    for d in range(start_date.day, min(end_date.day + 1, num_days + 1)):
                        worker_data["attendance"][d] = f"⚠️ On {leave_type}"
                        
                    st.success(f"🎉 مبارک ہو! {days_requested} چھٹیاں کامیابی سے مائنس کر دی گئیں اور آپ کا منتھ کارڈ اپڈیٹ ہو گیا ہے۔")
                    st.balloons()
                    st.rerun()
                else:
                    st.error("معذرت! آپ کا لیو بیلنس کم ہے۔")
            else:
                st.error("آخری تاریخ درست نہیں ہے۔")

# --- اگر ایڈمن لاگ ان ہے اور پاس ورڈ درست ہے ---
elif user_role == "Admin (ایڈمن)" and is_admin_authenticated:
    st.markdown("<h2 style='color: #1E3A8A; border-bottom: 2px solid #1E3A8A; padding-bottom:5px;'>🛠️ ایڈمن کنٹرول پینل (Admin Panel)</h2>", unsafe_allow_html=True)
    
    col_admin1, col_admin2 = st.columns(2)
    
    with col_admin1:
        st.markdown("<h4 style='color: #0D9488;'>➕ نیا ورکر شامل کریں (Add New Worker)</h4>", unsafe_allow_html=True)
        with st.form("add_form", clear_on_submit=True):
            w_id = st.text_input("ورکر آئی ڈی (مثال: IP-1024)")
            w_cnic = st.text_input("شناختی کارڈ نمبر (CNIC)")
            w_name = st.text_input("ورکر کا پورا نام")
            w_dept = st.selectbox("شعبہ منتخب کریں (Department)", DEPARTMENTS)
            w_shift = st.text_input("شفٹ (Shift)")
            
            if st.form_submit_button("✅ نیا ورکر ریکارڈ میں شامل کریں"):
                if w_id and w_name and w_cnic:
                    st.session_state.workers_list.append({
                        "id": w_id, "cnic": w_cnic, "name": w_name, "dept": w_dept, "shift": w_shift, "role": "Worker (ورکر)",
                        "balances": {"annual_m": 8.0, "annual_nm": 9.0, "casual": 7.5, "compensatory": 4.0},
                        "attendance": {}
                    })
                    st.success(f"🎉 ورکر '{w_name}' ڈیٹا بیس میں کامیابی سے ایڈ ہو گیا ہے!")
                    st.rerun()
                else:
                    st.error("براہ کرم آئی ڈی، نام اور شناختی کارڈ نمبر لازمی لکھیں۔")

    with col_admin2:
        st.markdown("<h4 style='color: #E11D48;'>✏️ پرانے ورکر کا ڈیٹا تبدیل کریں (Edit Worker Data)</h4>", unsafe_allow_html=True)
        all_workers = [w['name'] for w in st.session_state.workers_list]
        edit_name = st.selectbox("کس ورکر کا ڈیٹا بدلنا ہے؟", all_workers)
        to_edit = next(w for w in st.session_state.workers_list if w['name'] == edit_name)
        
        u_name = st.text_input("نام تبدیل کریں", value=to_edit["name"])
        u_cnic = st.text_input("شناختی کارڈ نمبر تبدیل کریں", value=to_edit["cnic"])
        u_id = st.text_input("آئی ڈی تبدیل کریں", value=to_edit["id"])
        u_dept = st.selectbox("شعبہ تبدیل کریں", DEPARTMENTS, index=DEPARTMENTS.index(to_edit["dept"]) if to_edit["dept"] in DEPARTMENTS else 0)
        u_shift = st.text_input("شفٹ تبدیل کریں", value=to_edit["shift"])
        
        if st.button("🔄 ڈیٹا اپڈیٹ کریں (Update Data)", use_container_width=True):
            to_edit["name"] = u_name
            to_edit["cnic"] = u_cnic
            to_edit["id"] = u_id
            to_edit["dept"] = u_dept
            to_edit["shift"] = u_shift
            st.success("ورکر کا ڈیٹا کامیابی سے اپڈیٹ ہو گیا!")
            st.rerun()

elif user_role == "Admin (ایڈمن)" and not is_admin_authenticated:
    st.info("🔒 ایڈمن پینل تک رسائی کے لیے سائیڈ بار میں درست پاس ورڈ درج کریں۔")
