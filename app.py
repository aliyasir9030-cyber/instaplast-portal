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
    .notification-box {
        background-color: #EFF6FF;
        border-right: 5px solid #3B82F6;
        padding: 10px 15px;
        margin: 5px 0;
        border-radius: 6px;
    }
    </style>
""", unsafe_allow_html=True)

# 1. ڈیٹا سیٹ کرنا
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
            "balances": {"casual": 10.0, "sick": 8.0, "annual": 14.0, "compensatory": 4.0},
            "attendance": {5: "Sick Leave (بیماری کی چھٹی)"} 
        },
        {
            "id": "IP-1023",
            "cnic": "42101-7654321-3",
            "name": "Ali Ahmed",
            "dept": "Production",
            "shift": "A-SHIFT",
            "role": "Worker (ورکر)",
            "basic_salary": 38000.0,
            "balances": {"casual": 12.0, "sick": 6.0, "annual": 10.0, "compensatory": 2.0},
            "attendance": {15: "Without Pay (Unpaid Leave)"}
        }
    ]

# گلوبل نوٹیفیکیشن لسٹ
if 'notifications' not in st.session_state:
    st.session_state.notifications = [
        "📢 محمد رضا المصطفیٰ نے 5 تاریخ کو Sick Leave اپلائی کی تھی۔",
        "📢 علی احمد نے 15 تاریخ کو Without Pay چھٹی اپلائی کی تھی۔"
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

if user_role == "Admin (ایڈمن)":
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

# --- 📢 نوٹیفیکیشن ڈیش بورڈ ---
st.markdown("<h3 style='color: #3B82F6;'>🔔 لیو نوٹیفیکیشن ڈیش بورڈ (Leave Notifications)</h3>", unsafe_allow_html=True)
if st.session_state.notifications:
    for note in reversed(st.session_state.notifications[-5:]): # صرف آخری 5 نوٹیفیکیشن دکھائے گا
        st.markdown(f"<div class='notification-box'>{note}</div>", unsafe_allow_html=True)
else:
    st.info("فی الحال چھٹی کی کوئی نئی درخواست موجود نہیں ہے۔")
st.write("---")


# --- اگر ورکر لاگ ان ہے ---
if user_role == "Worker (ورکر)":
    worker_names = [w['name'] for w in st.session_state.workers_list]
    
    if not worker_names:
        st.warning("کوئی ورکر موجود نہیں ہے۔")
    else:
        st.markdown("<h4 style='color: #1E3A8A;'>👤 اپنا اکاؤنٹ لاگ ان کریں:</h4>", unsafe_allow_html=True)
        col_log1, col_log2 = st.columns(2)
        selected_worker_name = col_log1.selectbox("اپنا نام منتخب کریں (Select Your Name):", worker_names)
        input_cnic = col_log2.text_input("اپنا شناختی کارڈ نمبر درج کریں (Enter CNIC as Password):", type="password")
        
        worker_data = next(w for w in st.session_state.workers_list if w['name'] == selected_worker_name)
        
        if input_cnic == worker_data["cnic"]:
            st.success(f"🔓 لاگ ان کامیاب! خوش آمدید {worker_data['name']}")
            st.write("---")
            
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
                    st.metric("Casual (ضروری کام)", f"{b.get('casual', 0.0)} Days")
                with c2:
                    st.metric("Sick (بیماری کی چھٹی)", f"{b.get('sick', 0.0)} Days")
                with c3:
                    st.metric("Annual (سالانہ چھٹیاں)", f"{b.get('annual', 0.0)} Days")
                with c4:
                    st.metric("Compensatory (متبادل)", f"{b.get('compensatory', 0.0)} Days")

                st.write("---")
                
                # چھٹی فارم
                st.markdown("<h4 style='color: #1E3A8A;'>📝 چھٹی اپلائی کریں (Apply For Leave)</h4>", unsafe_allow_html=True)
                leave_options = ["Paid Leave (تنخواہ کے ساتھ)", "Without Pay (بغیر تنخواہ/Unpaid)"]
                selected_pay_type = st.radio("چھٹی کی نوعیت منتخب کریں:", leave_options, horizontal=True)
                
                leave_type = "Without Pay (Unpaid Leave)"
                if selected_pay_type == "Paid Leave (تنخواہ کے ساتھ)":
                    leave_type = st.selectbox("چھٹی کی قسم (Leave Type)", [
                        "Casual Leave (ضروری کام کی چھٹی)", 
                        "Sick Leave (بیماری کی چھٹی)", 
                        "Annual Leave (سالانہ چھٹیاں)", 
                        "Compensatory Leave (متبادل چھٹی)"
                    ])
                
                col_d1, col_d2 = st.columns(2)
                start_date = col_d1.date_input("شروع ہونے کی تاریخ")
                end_date = col_d2.date_input("آخری تاریخ")
                
                if st.button("🚀 چھٹی کی درخواست سبمٹ کریں", use_container_width=True):
                    if end_date >= start_date:
                        days_requested = (end_date - start_date).days + 1
                        
                        def apply_attendance_dates():
                            if "attendance" not in worker_data:
                                worker_data["attendance"] = {}
                            for d in range(start_date.day, min(end_date.day + 1, num_days + 1)):
                                worker_data["attendance"][d] = f"⚠️ {leave_type}"
                        
                        if selected_pay_type == "Without Pay (بغیر تنخواہ/Unpaid)":
                            apply_attendance_dates()
                            st.session_state.notifications.append(f"⚠️ ورکر {worker_data['name']} نے {start_date.day} سے {end_date.day} تاریخ تک کے لیے {days_requested} دن کی {leave_type} اپلائی کی ہے۔")
                            st.success(f"🎉 بغیر تنخواہ کی {days_requested} چھٹیاں ریکارڈ میں درج کر دی گئی ہیں۔")
                            st.rerun()
                        else:
                            map_leave = {
                                "Casual Leave (ضروری کام کی چھٹی)": "casual", 
                                "Sick Leave (بیماری کی چھٹی)": "sick", 
                                "Annual Leave (سالانہ چھٹیاں)": "annual", 
                                "Compensatory Leave (متبادل چھٹی)": "compensatory"
                            }
                            b_key = map_leave[leave_type]
                            
                            if worker_data["balances"].get(b_key, 0.0) >= days_requested:
                                worker_data["balances"][b_key] -= days_requested
                                apply_attendance_dates()
                                st.session_state.notifications.append(f"⚠️ ورکر {worker_data['name']} نے {start_date.day} سے {end_date.day} تاریخ تک کے لیے {days_requested} دن کی {leave_type} اپلائی کی ہے۔")
                                st.success(f"🎉 {days_requested} چھٹیاں بیلنس سے مائنس کر کے منتھ کارڈ اپڈیٹ کر دیا گیا ہے۔")
                                st.balloons()
                                st.rerun()
                            else:
                                st.error(f"معذرت! آپ کا {leave_type} کا بیلنس کم ہے، براہِ کرم 'Without Pay' اپلائی کریں۔")
                    else:
                        st.error("آخری تاریخ درست نہیں ہے۔")
        elif input_cnic != "":
            st.error("❌ غلط شناختی کارڈ نمبر! آپ کسی دوسرے کا ریکارڈ نہیں دیکھ سکتے۔")
        else:
            st.info("🔒 اپنا ڈیٹا اور لیو بیلنس دیکھنے کے لیے اپنا شناختی کارڈ نمبر (CNIC) درج کریں۔")

# --- اگر ایڈمن لاگ ان ہے ---
elif user_role == "Admin (ایڈمن)" and is_admin_authenticated:
    st.markdown("<h2 style='color: #1E3A8A; border-bottom: 2px solid #1E3A8A; padding-bottom:5px;'>🛠️ ایڈمن کنٹرول پینل (Admin Panel)</h2>", unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["👥 ورکرز مینجمنٹ & اپروول", "📋 تمام ورکرز کا ریکارڈ (Leave Balances)", "📊 سیلری شیٹ (Salary Sheet)"])
    
    with tab1:
        col_admin1, col_admin2 = st.columns(2)
        
        with col_admin1:
            st.markdown("<h4 style='color: #0D9488;'>➕ نیا ورکر شامل کریں اور چھٹیاں الاؤ کریں</h4>", unsafe_allow_html=True)
            with st.form("add_form", clear_on_submit=True):
                w_id = st.text_input("ورکر آئی ڈی")
                w_cnic = st.text_input("شناختی کارڈ نمبر (یہی ورکر کا پاس ورڈ ہوگا)")
                w_name = st.text_input("ورکر کا پورا نام")
                w_dept = st.selectbox("شعبہ (Department)", DEPARTMENTS)
                w_shift = st.text_input("شفٹ (Shift)")
                w_salary = st.number_input("بنیادی تنخواہ (Basic Salary)", min_value=0.0, step=1000.0, value=25000.0)
                
                st.markdown("<p style='color:#1E3A8A; font-weight:bold; margin-top:15px;'>📋 پورے سال کی الاؤ چھٹیاں:</p>", unsafe_allow_html=True)
                col_l1, col_l2 = st.columns(2)
                allow_casual = col_l1.number_input("Casual Leave (ضروری کام)", min_value=0.0, value=10.0)
                allow_sick = col_l2.number_input("Sick Leave (بیماری)", min_value=0.0, value=8.0)
                allow_annual = col_l1.number_input("Annual Leave (سالانہ)", min_value=0.0, value=14.0)
                allow_comp = col_l2.number_input("Compensatory Leave (متبادل)", min_value=0.0, value=0.0)
                
                if st.form_submit_button("✅ نیا ورکر ریکارڈ میں شامل کریں"):
                    if w_id and w_name and w_cnic:
                        st.session_state.workers_list.append({
                            "id": w_id, "cnic": w_cnic, "name": w_name, "dept": w_dept, "shift": w_shift, "role": "Worker (ورکر)",
                            "basic_salary": w_salary,
                            "balances": {"casual": allow_casual, "sick": allow_sick, "annual": allow_annual, "compensatory": allow_comp},
                            "attendance": {}
                        })
                        st.success(f"🎉 ورکر '{w_name}' مخصوص چھٹیوں کے کوٹے کے ساتھ شامل ہو گیا!")
                        st.rerun()
                    else:
                        st.error("آئی ڈی، نام اور شناختی کارڈ لازمی درج کریں۔")

            # 🔥 نیا اضافہ: ایڈمن پینل سے براہ راست چھٹی اپلائی/منظور کرنے کا فارم
            st.write("---")
            st.markdown("<h4 style='color: #3B82F6;'>✍️ ایڈمن پینل سے چھٹی منظور کریں (Direct Approval)</h4>", unsafe_allow_html=True)
            all_workers_names = [w['name'] for w in st.session_state.workers_list]
            
            adm_select_worker = st.selectbox("کس ورکر کی چھٹی منظور کرنی ہے؟", all_workers_names, key="adm_sel_w")
            adm_worker_data = next(w for w in st.session_state.workers_list if w['name'] == adm_select_worker)
            
            adm_leave_pay = st.radio("نوعیت:", ["Paid Leave (تنخواہ کے ساتھ)", "Without Pay (بغیر تنخواہ)"], key="adm_pay", horizontal=True)
            
            if adm_leave_pay == "Paid Leave (تنخواہ کے ساتھ)":
                adm_leave_type = st.selectbox("چھٹی کی قسم:", ["Casual Leave", "Sick Leave", "Annual Leave", "Compensatory Leave"], key="adm_l_type")
            else:
                adm_leave_type = "Without Pay"
                
            col_ad1, col_ad2 = st.columns(2)
            adm_start = col_ad1.date_input("شروع تاریخ", key="adm_s_date")
            adm_end = col_ad2.date_input("آخری تاریخ", key="adm_e_date")
            
            if st.button("✅ چھٹی فوراً منظور اور لاگو کریں", use_container_width=True):
                if adm_end >= adm_start:
                    days_num = (adm_end - adm_start).days + 1
                    t_month_days = calendar.monthrange(adm_start.year, adm_start.month)[1]
                    
                    if "attendance" not in adm_worker_data:
                        adm_worker_data["attendance"] = {}
                    
                    for d in range(adm_start.day, min(adm_end.day + 1, t_month_days + 1)):
                        adm_worker_data["attendance"][d] = f"⚠️ {adm_leave_type} (Approved by Admin)"
                    
                    if adm_leave_pay == "Paid Leave (تنخواہ کے ساتھ)":
                        map_k = {"Casual Leave": "casual", "Sick Leave": "sick", "Annual Leave": "annual", "Compensatory Leave": "compensatory"}
                        k = map_k[adm_leave_type]
                        adm_worker_data["balances"][k] = max(0.0, adm_worker_data["balances"].get(k, 0.0) - days_num)
                    
                    st.session_state.notifications.append(f"💼 ایڈمن نے ورکر {adm_select_worker} کی {days_num} دن کی {adm_leave_type} خود منظور کر دی ہے۔")
                    st.success(f"🎉 {adm_select_worker} کی چھٹی کامیابی سے سسٹم میں درج اور بیلنس اپڈیٹ کر دیا گیا ہے!")
                    st.rerun()
                else:
                    st.error("آخری تاریخ درست منتخب کریں۔")

        with col_admin2:
            st.markdown("<h4 style='color: #E11D48;'>✏️ ورکر ڈیٹا / چھٹیاں تبدیل کریں</h4>", unsafe_allow_html=True)
            all_workers = [w['name'] for w in st.session_state.workers_list]
            edit_name = st.selectbox("ورکر منتخب کریں:", all_workers, key="edit_sel")
            to_edit = next(w for w in st.session_state.workers_list if w['name'] == edit_name)
            
            u_name = st.text_input("نام تبدیل کریں", value=to_edit["name"])
            u_cnic = st.text_input("شناختی کارڈ تبدیل کریں", value=to_edit["cnic"])
            u_id = st.text_input("آئی ڈی تبدیل کریں", value=to_edit["id"])
            u_dept = st.selectbox("شعبہ تبدیل کریں", DEPARTMENTS, index=DEPARTMENTS.index(to_edit["dept"]) if to_edit["dept"] in DEPARTMENTS else 0)
            u_shift = st.text_input("شفٹ تبدیل کریں", value=to_edit["shift"])
            u_salary = st.number_input("بنیادی تنخواہ تبدیل کریں", min_value=0.0, step=1000.0, value=to_edit.get("basic_salary", 25000.0))
            
            st.markdown("<p style='color:#E11D48; font-weight:bold; margin-top:15px;'>🔄 چھٹیوں کا بیلنس اپڈیٹ کریں:</p>", unsafe_allow_html=True)
            col_u1, col_u2 = st.columns(2)
            u_casual = col_u1.number_input("Casual Leave Balance", min_value=0.0, value=float(to_edit["balances"].get("casual", 0.0)))
            u_sick = col_u2.number_input("Sick Leave Balance", min_value=0.0, value=float(to_edit["balances"].get("sick", 0.0)))
            u_annual = col_u1.number_input("Annual Leave Balance", min_value=0.0, value=float(to_edit["balances"].get("annual", 0.0)))
            u_comp = col_u2.number_input("Compensatory Leave Balance", min_value=0.0, value=float(to_edit["balances"].get("compensatory", 0.0)))
            
            if st.button("🔄 ڈیٹا اور چھٹیاں اپڈیٹ کریں", use_container_width=True):
                to_edit["name"] = u_name
                to_edit["cnic"] = u_cnic
                to_edit["id"] = u_id
                to_edit["dept"] = u_dept
                to_edit["shift"] = u_shift
                to_edit["basic_salary"] = u_salary
                to_edit["balances"] = {"casual": u_casual, "sick": u_sick, "annual": u_annual, "compensatory": u_comp}
                st.success("ورکر کا ڈیٹا اور لیو بیلنس کامیابی سے اپڈیٹ ہو گیا!")
                st.rerun()
                
    with tab2:
        st.markdown("<h4 style='color: #1E3A8A;'>📋 تمام ورکرز کا لائیو لیو ریکارڈ اور اسٹیٹس</h4>", unsafe_allow_html=True)
        
        records_data = []
        for w in st.session_state.workers_list:
            # ورکر نے اس مہینے جو چھٹیاں لیں ان کا ریکارڈ ایک ٹیکسٹ کی شکل میں دکھانے کے لیے
            taken_leaves = []
            for day, status in w.get("attendance", {}).items():
                if "Leave" in status or "Without Pay" in status:
                    taken_leaves.append(f"{day} تاریخ ({status.split(' ')[0]})")
            
            leaves_summary = ", ".join(taken_leaves) if taken_leaves else "کوئی چھٹی نہیں کی (حاضر)"
            
            records_data.append({
                "آئی ڈی": w["id"],
                "ورکر کا نام": w["name"],
                "شعبہ": w["dept"],
                "Casual (ضروری کام)": w["balances"].get("casual", 0.0),
                "Sick (بیماری)": w["bala
