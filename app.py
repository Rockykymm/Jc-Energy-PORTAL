import streamlit as st
from supabase import create_client
import pandas as pd

# 1. Database Connection (Uses the Secrets you pasted above)
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

st.set_page_config(page_title="Jc Energy Secure Portal", layout="wide")

# --- CUSTOM BRANDING & LOGO ---
st.markdown("""
    <style>
    .stApp { background-color: #072A07; }
    .main-card {
        background-color: white; padding: 20px;
        border-radius: 10px; border-top: 5px solid #CC0000;
    }
    </style>
    """, unsafe_allow_html=True)

# Logo Display
l_col, r_col = st.columns([1, 4])
with l_col:
    st.markdown("""
        <div style='text-align: center; border: 2px solid white; border-radius: 8px; padding: 5px; background: white;'>
            <h1 style='color: #072A07; margin: 0;'>JC</h1>
            <h4 style='color: #CC0000; border-top: 2px solid #CC0000; margin: 0;'>ENERGY</h4>
            <span style='color: #FFD700; font-size: 24px;'>💧</span>
        </div>
        """, unsafe_allow_html=True)
with r_col:
    st.title("Jc Energy Secure Portal")

# --- LOGIN LOGIC ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.subheader("🔑 Attendant Access")
    work_id = st.text_input("Enter Work ID", type="password")
    if st.button("Open Portal"):
        # Check the 'staff' table for this ID
        res = supabase.table("staff").select("*").eq("work_id", work_id).execute()
        if res.data:
            st.session_state.logged_in = True
            st.session_state.user = res.data[0]
            st.rerun()
        else:
            st.error("Invalid ID. Please contact the Manager.")
    st.stop()

# --- APP TABS ---
user = st.session_state.user
tab_names = ["📝 Shift Record"]
if user.get('is_admin'): tab_names.append("📊 Manager Logs")
tabs = st.tabs(tab_names)

# SHIFT RECORD TAB
with tabs[0]:
    st.info(f"Logged in as: **{user['full_name']}**")
    # Fetch last closing reading from database
    res_last = supabase.table("shift_logs").select("pump_reading_end").order("created_at", desc=True).limit(1).execute()
    start_reading = float(res_last.data[0]["pump_reading_end"]) if res_last.data else 0.0
    
    st.markdown(f"### 📍 Opening Reading: `{start_reading:,} L`")
    
    with st.form("shift_form"):
        end_reading = st.number_input("Ending Reading (L)", value=start_reading)
        cash = st.number_input("Physical Cash (KES)", min_value=0.0)
        mpesa = st.number_input("M-Pesa (KES)", min_value=0.0)
        
        if st.form_submit_button("Submit & Close"):
            liters = end_reading - start_reading
            expected = liters * 189.0 # Price per liter
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
            st.success("Shift Closed!")
            st.balloons()

# MANAGER TAB (Only visible to Admins)
if user.get('is_admin'):
    with tabs[1]:
        st.subheader("Station Performance History")
        logs = supabase.table("shift_logs").select("*").order("created_at", desc=True).execute()
        if logs.data:
            df = pd.DataFrame(logs.data)
            st.dataframe(df)
