import streamlit as st
from supabase import create_client

# 1. Database Connection
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

st.set_page_config(page_title="Jc Energy Secure Portal", layout="wide")

# --- BRANDING: THE LOGO DESIGN ---
st.markdown("""
    <style>
    .stApp { background-color: #072A07; }
    .logo-box {
        text-align: center; border: 2px solid white; border-radius: 8px; 
        padding: 10px; background: white; margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- LOGIN GATEWAY ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown("<div class='logo-box'><h1 style='color:#072A07; margin:0;'>JC</h1><h4 style='color:#CC0000; border-top:2px solid #CC0000; margin:0;'>ENERGY</h4><span style='font-size:20px;'>💧</span></div>", unsafe_allow_html=True)
    st.subheader("🔑 Security Login")
    work_id = st.text_input("Enter Work ID", type="password")
    if st.button("Access Portal"):
        res = supabase.table("staff").select("*").eq("work_id", work_id).execute()
        if res.data:
            st.session_state.logged_in = True
            st.session_state.user = res.data[0]
            st.rerun()
        else:
            st.error("Access Denied: Invalid Work ID")
    st.stop()

# --- PORTAL CONTENT (LOGGED IN) ---
user = st.session_state.user
st.sidebar.success(f"Welcome, {user['full_name']}")
if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.rerun()

# --- AUTOMATIC METER LOGIC ---
res_last = supabase.table("shift_logs").select("pump_reading_end").order("created_at", desc=True).limit(1).execute()
start_reading = float(res_last.data[0]["pump_reading_end"]) if res_last.data else 0.0

tab_list = ["📝 Shift Record"]
if user['is_admin']: tab_list += ["📊 Manager Logs"]
tabs = st.tabs(tab_list)

with tabs[0]:
    st.info(f"📍 Opening Reading (Chain): **{start_reading:,} L**")
    with st.form("shift_form"):
        end_reading = st.number_input("Ending Reading (Liters)", value=start_reading)
        cash = st.number_input("Physical Cash Handed Over (KES)", min_value=0.0)
        mpesa = st.number_input("M-Pesa / Till Total (KES)", min_value=0.0)
        
        if st.form_submit_button("Submit & Close Shift"):
            liters = end_reading - start_reading
            expected = liters * 189.0
            total = cash + mpesa
            
            entry = {
                "attendant_name": user['full_name'],
                "pump_reading_start": start_reading,
                "pump_reading_end": end_reading,
                "liters_sold": liters,
                "expected_total": expected,
                "actual_cash": cash,
                "actual_mpesa": mpesa,
                "total_collected": total,
                "difference": total - expected
            }
            supabase.table("shift_logs").insert(entry).execute()
            st.success("Shift successfully recorded!")
            st.balloons()

