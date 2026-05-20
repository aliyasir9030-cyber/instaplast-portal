import streamlit as st
from datetime import datetime

# 1. ڈمی ڈیٹا سیٹ کرنا (بشمول لیو بیلنس)
if 'workers_list' not in st.session_state:
    st.session_state.workers_list = [
        {
            "id": "IP-1022",
            "name": "Muhammad Raza-ul-Mustafa",
            "dept": "Utilities (Electrical & Instrumentation)",
            "shift": "G28SHIFT",
            "role": "Worker (ورکر)",
            "balances": {"annual_m": 8.0, "annual_nm": 9.0, "casual": 7.5, "compensatory": 4.0}
        }
    ]

# 2. سائیڈ بار لاگ ان پینل
st.sidebar.title("🔒 Login Panel")
user_role = st.sidebar.selectbox("Select Role / اپنا رول منتخب کریں", ["Worker (ورکر)", "Admin (ایڈمن)"])

available_workers = [w['name'] for w in st.session_state.workers_list if w['role'] == user_role]

if not available_workers:
    st.sidebar.warning("اس رول کا کوئی ورکر موجود نہیں ہے۔")
else:
    selected_worker_name = st.sidebar.selectbox("Select Worker / ورکر منتخب کریں", available_workers)
    worker_data = next(w for w in st.session_state.workers_list if w['name'] == selected_worker_name)

# --- مین اسکرین (Main Screen) ---
st.title("🏭 INSTAPLAST PVT LTD")
st.caption("Employee Leave Management Portal")

# اگر ورکر لاگ ان ہے
if user_role == "Worker (ورکر)" and available_workers:
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("👤 ورکر پروفائل")
        st.write(f"**نام:** {worker_data['name']}")
        st.write(f"**آئی ڈی:** {worker_data['id']}")
        st.write(f"**شعبہ:** {worker_data['dept']}")
        st.write(f"**شفٹ:** {worker_data['shift']}")
    
    with col2:
        st.subheader("📊 لیو بیلنس (Leave Account Balances)")
        b = worker_data["balances"]
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Annual (M)", f"{b['annual_m']} Days")
        c2.metric("Annual (NM)", f"{b['annual_nm']} Days")
        c3.metric("Casual", f"{b['casual']} Days")
        c4.metric("Compensatory", f"{b['compensatory']} Days")

    st.write("---")
    
    # چھٹی اپلائی کرنے کا فارم
    st.subheader("📝 چھٹی اپلائی کریں (Apply For Leave)")
    leave_type = st.selectbox("چھٹی کی قسم (Leave Type)", ["Annual Leave (M)", "Annual Leave (NM)", "Casual Leave", "Compensatory Leave"])
    start_date = st.date_input("شروع ہونے کی تاریخ (Start Date)")
    end_date = st.date_input("آخری تاریخ (End Date)")
    
    if st.button("چھٹی کی درخواست بھیجیں"):
        if end_date >= start_date:
            days_requested = (end_date - start_date).days + 1
            
            # چھٹی کی قسم کے مطابق کی (Key) منتخب کریں
            map_leave = {"Annual Leave (M)": "annual_m", "Annual Leave (NM)": "annual_nm", "Casual Leave": "casual", "Compensatory Leave": "compensatory"}
            b_key = map_leave[leave_type]
            
            if worker_data["balances"][b_key] >= days_requested:
                worker_data["balances"][b_key] -= days_requested
                st.success(f"🎉 {days_requested} چھٹیاں کامیابی سے مائنس کر دی گئیں!")
                st.rerun()
            else:
                st.error("معذرت! آپ کا لیو بیلنس کم ہے۔")
        else:
            st.error("آخری تاریخ درست نہیں ہے۔")

# اگر ایڈمن لاگ ان ہے
elif user_role == "Admin (ایڈمن)":
    st.subheader("🛠️ ایڈمن کنٹرول پینل")
    
    # نیا ورکر ایڈ کرنے کا سیکشن
    with st.expander("➕ نیا ورکر شامل کریں"):
        with st.form("add_form", clear_on_submit=True):
            w_id = st.text_input("آئی ڈی")
            w_name = st.text_input("نام")
            w_dept = st.text_input("شعبہ")
            w_shift = st.text_input("شفٹ")
            if st.form_submit_button("شامل کریں"):
                st.session_state.workers_list.append({
                    "id": w_id, "name": w_name, "dept": w_dept, "shift": w_shift, "role": "Worker (ورکر)",
                    "balances": {"annual_m": 8.0, "annual_nm": 9.0, "casual": 7.5, "compensatory": 4.0}
                })
                st.success("نیا ورکر ایڈ ہو گیا!")
                st.rerun()

    # پرانے ورکر کا ڈیٹا تبدیل (Edit) کرنے کا سیکشن
    with st.expander("✏️ پرانے ورکر کا ڈیٹا تبدیل کریں (Edit Worker)"):
        all_workers = [w['name'] for w in st.session_state.workers_list]
        edit_name = st.selectbox("ورکر منتخب کریں جس کا ڈیٹا بدلنا ہے", all_workers)
        to_edit = next(w for w in st.session_state.workers_list if w['name'] == edit_name)
        
        u_name = st.text_input("نام تبدیل کریں", value=to_edit["name"])
        u_id = st.text_input("آئی ڈی تبدیل کریں", value=to_edit["id"])
        u_dept = st.text_input("شعبہ تبدیل کریں", value=to_edit["dept"])
        u_shift = st.text_input("شفٹ تبدیل کریں", value=to_edit["shift"])
        
        if st.button("ڈیٹا اپڈیٹ کریں"):
            to_edit["name"] = u_name
            to_edit["id"] = u_id
            to_edit["dept"] = u_dept
            to_edit["shift"] = u_shift
            st.success("ڈیٹا کامیابی سے تبدیل ہو گیا!")
            st.rerun()
    