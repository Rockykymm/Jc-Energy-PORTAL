import streamlit as st
from supabase import create_client
import pandas as pd

# Database Connection
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

st.set_page_config(page_title="Jc Energy Secure Portal", layout="wide")

# Custom Branding
st.markdown("""
    <style>
    .stApp { background-color: #072A07; }
    .main-card {
        background-color: white; padding: 20px;
        border-radius: 10px; border-top: 5px solid #CC0000;
    }
    </style>
    """, unsafe_allow_html=True)

# Login Logic
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.subheader("🔑 Attendant Access")
    work_id = st.text_input("Enter Work ID", type="password")
    if st.button("Open Portal"):
        res = supabase.table("staff").select("*").eq("work_id", work_id).execute()
        if res.data:
            st.session_state.logged_in = True
            st.session_state.user = res.data[0]
            st.rerun()
        else:
            st.error("Invalid ID.")
    st.stop()

# App Tabs
user = st.session_state.user
tabs = st.tabs(["📝 Shift Record", "📊 Manager Logs"] if user.get('is_admin') else ["📝 Shift Record"])

with tabs[0]:
    st.info(f"Logged in: **{user['full_name']}**")
    # Form for shift logs
    with st.form("shift_form"):
        end_reading = st.number_input("Ending Reading (L)")
        cash = st.number_input("Cash (KES)")
        mpesa = st.number_input("M-Pesa (KES)")
        if st.form_submit_button("Submit & Close"):
            entry = {
                "attendant_name": user['full_name'],
                "pump_reading_end": end_reading,
                "actual_cash": cash,
                "actual_mpesa": mpesa
            }
            supabase.table("shift_logs").insert(entry).execute()
            st.success("Record Saved!")
            st.balloons()
