import streamlit as st
from datetime import datetime, date
import calendar
import pandas as pd

# پیج کی بنیادی سیٹنگز اور کلر تھیم
st.set_page_config(page_title="INSTAPLAST Leave Portal", page_icon="🏭", layout="wide")

# کسٹم سی ایس ایس (CSS) ایپ کو خوبصورت بنانے کے لیے
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
    </style>
""", unsafe_allow_html=True)

# 1. ڈمی ڈیٹا سیٹ کرنا (بشمول بنیادی تنخواہ اور حاضری)
if 'workers_list' not in st.session_state:
    st.session_state.workers_list = [
        {
            "id": "IP-1022",
            "cnic": "42101-1234567-1",
            "name": "Muhammad Raza-ul-Mustafa",
            "dept": "Utilities (Electrical & Instrumentation)",
            "shift": "G28SHIFT",
            "role": "Worker (ورکر)",
            "basic_salary": 45000.0,
            "balances": {"annual_m": 8.0, "annual_nm": 9.0, "casual": 7.5, "compensatory": 4.0},
            "attendance": {5: "Casual Leave", 6: "Casual Leave"} 
        },
        {
            "id": "IP-1023",
            "cnic": "42101-7654321-3",
            "name": "Ali Ahmed",
            "dept": "Production",
            "shift": "A-SHIFT",
            "role": "Worker (ورکر)",
            "basic_salary": 38000.0,
            "balances": {"annual_m": 10.0, "annual_nm": 6.0, "casual": 5.0, "compensatory": 2.0},
            "attendance": {15: "Without Pay (Unpaid Leave)"} # اس ورکر کی تنخواہ کٹے گی
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
    admin_password = st.sidebar.text_input("Enter Admin Password / پاس ورڈ درج کریں", type="password")
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
        
        # منتھ کارڈ
        st.write("")
        st.markdown("<h4 style='color: #1E3A8A;'>📅 کرنٹ منتھ کارڈ</h4>", unsafe_allow_html=True)
        today = date.today()
        num_days = calendar.monthrange(today.year, today.month)[1]
        
        card_data = []
        for day in range(1, num_days + 1):
            current_date = date(today.year, today.month, day)
            day_name = current_date.strftime("%A")
            
            if day_name == "Sunday":
                status = "🔴 Weekly Off (اتوار)"
            else:
                status = worker_data.get("attendance", {}).get(day, "🟢 Present (حاضر)")
                
            card_data.append({"Date": f"{day}/{today.month}", "Day": day_name, "Status": status})
            
        st.dataframe(card_data, use_container_width=True, height=250)
    
    with col2:
        st.markdown("<h3 style='color: #0D9488; border-bottom: 2px solid #0D9488; padding-bottom:5px;'>📊 لیو بیلنس (Leave Account Balances)</h3>", unsafe_allow_html=True)
        st.write("")
        b = worker_data["balances"]
        
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric("Annual (M)", f"{b['annual_m']} Days")
        with c2:
            st.metric("Annual (NM)", f"{b['annual_nm']} Days")
        with c3:
            st.metric("Casual", f"{b['casual']} Days")
        with c4:
            st.metric("Compensatory", f"{b['compensatory']} Days")

        st.write("---")
        
        # چھٹی فارم
        st.markdown("<h4 style='color: #1E3A8A;'>📝 چھٹی اپلائی کریں (Apply For Leave)</h4>", unsafe_allow_html=True)
        leave_options = ["Paid Leave (تنخواہ کے ساتھ)", "Without Pay (بغیر تنخواہ/Unpaid)"]
        selected_pay_type = st.radio("چھٹی کی نوعیت منتخب کریں:", leave_options, horizontal=True)
        
        leave_type = "Without Pay (Unpaid Leave)"
        if selected_pay_type == "Paid Leave (تنخواہ کے ساتھ)":
            leave_type = st.selectbox("چھٹی کی قسم (Leave Type)", ["Annual Leave (M)", "Annual Leave (NM)", "Casual Leave", "Compensatory Leave"])
        
        col_d1, col_d2 = st.columns(2)
        start_date = col_d1.date_input("شروع ہونے کی تاریخ")
        end_date = col_d2.date_input("آخری تاریخ")
        
        if st.button("🚀 چھٹی کی درخواست سبمٹ کریں", use_container_width=True):
            if end_date >= start_date:
                days_requested = (end_date - start_date).days + 1
                
                # حاضری اپڈیٹ کرنے کا فنکشن
                def apply_attendance_dates():
                    if "attendance" not in worker_data:
                        worker_data["attendance"] = {}
                    for d in range(start_date.day, min(end_date.day + 1, num_days + 1)):
                        worker_data["attendance"][d] = f"⚠️ {leave_type}"
                
                if selected_pay_type == "Without Pay (بغیر تنخواہ/Unpaid)":
                    apply_attendance_dates()
                    st.success(f"🎉 بغیر تنخواہ (Without Pay) کی {days_requested} چھٹیاں ریکارڈ میں درج کر دی گئی ہیں۔")
                    st.rerun()
                else:
                    map_leave = {"Annual Leave (M)": "annual_m", "Annual Leave (NM)": "annual_nm", "Casual Leave": "casual", "Compensatory Leave": "compensatory"}
                    b_key = map_leave[leave_type]
                    
                    if worker_data["balances"][b_key] >= days_requested:
                        worker_data["balances"][b_key] -= days_requested
                        apply_attendance_dates()
                        st.success(f"🎉 {days_requested} پیڈ چھٹیاں بیلنس سے کامیابی سے مائنس کر دی گئی ہیں۔")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error("معذرت! آپ کا لیو بیلنس کم ہے، براہِ کرم 'Without Pay' اپلائی کریں۔")
            else:
                st.error("آخری تاریخ درست نہیں ہے۔")

# --- اگر ایڈمن لاگ ان ہے ---
elif user_role == "Admin (ایڈمن)" and is_admin_authenticated:
    st.markdown("<h2 style='color: #1E3A8A; border-bottom: 2px solid #1E3A8A; padding-bottom:5px;'>🛠️ ایڈمن کنٹرول پینل (Admin Panel)</h2>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["👥 ورکرز مینجمنٹ", "📊 سیلری شیٹ (Salary Sheet)"])
    
    with tab1:
        col_admin1, col_admin2 = st.columns(2)
        
        with col_admin1:
            st.markdown("<h4 style='color: #0D9488;'>➕ نیا ورکر شامل کریں</h4>", unsafe_allow_html=True)
            with st.form("add_form", clear_on_submit=True):
                w_id = st.text_input("ورکر آئی ڈی")
                w_cnic = st.text_input("شناختی کارڈ نمبر")
                w_name = st.text_input("ورکر کا پورا نام")
                w_dept = st.selectbox("شعبہ (Department)", DEPARTMENTS)
                w_shift = st.text_input("شفٹ (Shift)")
                w_salary = st.number_input("بنیادی تنخواہ (Basic Salary)", min_value=0.0, step=1000.0, value=25000.0)
                
                if st.form_submit_button("✅ نیا ورکر شامل کریں"):
                    if w_id and w_name and w_cnic:
                        st.session_state.workers_list.append({
                            "id": w_id, "cnic": w_cnic, "name": w_name, "dept": w_dept, "shift": w_shift, "role": "Worker (ورکر)",
                            "basic_salary": w_salary,
                            "balances": {"annual_m": 8.0, "annual_nm": 9.0, "casual": 7.5, "compensatory": 4.0},
                            "attendance": {}
                        })
                        st.success(f"🎉 ورکر '{w_name}' بنیادی تنخواہ روپے {w_salary} کے ساتھ شامل ہو گیا!")
                        st.rerun()
                    else:
                        st.error("آئی ڈی، نام اور شناختی کارڈ لازمی درج کریں۔")

        with col_admin2:
            st.markdown("<h4 style='color: #E11D48;'>✏️ ورکر ڈیٹا تبدیل کریں</h4>", unsafe_allow_html=True)
            all_workers = [w['name'] for w in st.session_state.workers_list]
            edit_name = st.selectbox("ورکر منتخب کریں:", all_workers)
            to_edit = next(w for w in st.session_state.workers_list if w['name'] == edit_name)
            
            u_name = st.text_input("نام تبدیل کریں", value=to_edit["name"])
            u_cnic = st.text_input("شناختی کارڈ تبدیل کریں", value=to_edit["cnic"])
            u_id = st.text_input("آئی ڈی تبدیل کریں", value=to_edit["id"])
            u_dept = st.selectbox("شعبہ تبدیل کریں", DEPARTMENTS, index=DEPARTMENTS.index(to_edit["dept"]) if to_edit["dept"] in DEPARTMENTS else 0)
            u_shift = st.text_input("شفٹ تبدیل کریں", value=to_edit["shift"])
            u_salary = st.number_input("بنیادی تنخواہ تبدیل کریں", min_value=0.0, step=1000.0, value=to_edit.get("basic_salary", 25000.0))
            
            if st.button("🔄 ڈیٹا اپڈیٹ کریں", use_container_width=True):
                to_edit["name"] = u_name
                to_edit["cnic"] = u_cnic
                to_edit["id"] = u_id
                to_edit["dept"] = u_dept
                to_edit["shift"] = u_shift
                to_edit["basic_salary"] = u_salary
                st.success("ورکر کا ڈیٹا اور تنخواہ کامیابی سے اپڈیٹ ہو گئی!")
                st.rerun()
                
    with tab2:
        st.markdown("<h4 style='color: #1E3A8A;'>📊 فیکٹری منتھلی سیلری شیٹ</h4>", unsafe_allow_html=True)
        
        today = date.today()
        num_days = calendar.monthrange(today.year, today.month)[1]
        
        st.write(f"موجودہ مہینہ: **{today.strftime('%B %Y')}** (کل دن: {num_days})")
        
        salary_sheet_data = []
        
        for w in st.session_state.workers_list:
            basic = w.get("basic_salary", 25000.0)
            daily_rate = basic / num_days
            
            # Unpaid Leaves کا حساب لگانا
            unpaid_days = 0
            for att_day, att_status in w.get("attendance", {}).items():
                if "Without Pay" in att_status:
                    unpaid_days += 1
            
            # کٹوتی (Deduction) کا فارمولا
            deduction = unpaid_days * daily_rate
            net_salary = basic - deduction
            
            salary_sheet_data.append({
                "ورکر آئی ڈی": w["id"],
                "ورکر کا نام": w["name"],
                "شعبہ (Dept)": w["dept"],
                "بنیادی تنخواہ": f"Rs. {basic:,.2f}",
                "بغیر تنخواہ چھٹیاں (Unpaid)": f"{unpaid_days} Days",
                "کل کٹوتی (Deduction)": f"Rs. {deduction:,.2f}",
                "نیٹ سیلری (Net Payable)": f"Rs. {net_salary:,.2f}"
            })
            
        df_salary = pd.DataFrame(salary_sheet_data)
        st.dataframe(df_salary, use_container_width=True)
        
        # ایکسل/CSV فائل ڈاؤن لوڈ بٹن
        csv = df_salary.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 ڈاؤن لوڈ سیلری شیٹ (Excel/CSV File)",
            data=csv,
            file_name=f"Instaplast_Salary_Sheet_{today.strftime('%b_%Y')}.csv",
            mime='text/csv',
            use_container_width=True
        )

elif user_role == "Admin (ایڈمن)" and not is_admin_authenticated:
    st.info("🔒 سیلری شیٹ اور ایڈمن پینل دیکھنے کے لیے سائیڈ بار میں درست پاس ورڈ درج کریں۔")
