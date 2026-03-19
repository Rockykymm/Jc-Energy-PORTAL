import streamlit as st
from supabase import create_client
import pandas as pd

# 1. Database Connection
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

st.set_page_config(page_title="Jc Energy Secure Portal", layout="wide")

# --- CUSTOM BACKGROUND LOGO & STYLING ---
def add_bg_logo():
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: linear-gradient(rgba(7, 42, 7, 0.9), rgba(7, 42, 7, 0.9)), 
                              url("https://raw.githubusercontent.com/Rockykymm/Jc-Energy-PORTAL/main/Gemini_Generated_Image_ykd8mjykd8mjykd8.jpg");
            background-size: contain;
            background-repeat: no-repeat;
            background-position: center;
            background-attachment: fixed;
        }}
        /* Styling for input cards to make them pop against the background */
        .stTextInput, .stNumberInput, [data-testid="stForm"] {{
            background-color: rgba(255, 255, 255, 0.05);
            padding: 20px;
            border-radius: 10px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }}
        h2, h3, h4, p, label {{
            color: white !important;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

add_bg_logo()

# Login Logic
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    # Center the login box
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h2 style='text-align: center;'>🔑 Attendant Access</h2>", unsafe_allow_html=True)
        work_id = st.text_input("Enter Work ID", type="password")
        if st.button("Open Portal", use_container_width=True):
            res = supabase.table("staff").select("*").eq("work_id", work_id).execute()
            if res.data:
                st.session_state.logged_in = True
                st.session_state.user = res.data[0]
                st.rerun()
            else:
                st.error("Invalid ID. Please contact Peter.")
    st.stop()

user = st.session_state.user
tab_names = ["📝 Shift Record"]
if user.get('is_admin'): tab_names.append("📊 Manager Tools")
tabs = st.tabs(tab_names)

# --- TAB 1: SHIFT RECORD (Entry Readings) ---
with tabs[0]:
    st.markdown(f"### Welcome, {user['full_name']}")
    
    # Auto-fetch the last closing reading
    res_last = supabase.table("shift_logs").select("pump_reading_end").order("created_at", desc=True).limit(1).execute()
    start_reading = float(res_last.data[0]["pump_reading_end"]) if res_last.data else 0.0
    
    st.info(f"Opening Pump Reading: **{start_reading:,} Liters**")
    
    with st.form("shift_entry"):
        st.markdown("#### Record Shift Totals")
        end_reading = st.number_input("Current Closing Pump Reading (Liters)", value=start_reading, step=0.01)
        cash = st.number_input("Total Cash Collected (KES)", min_value=0.0)
        mpesa = st.number_input("Total M-Pesa Collected (KES)", min_value=0.0)
        
        if st.form_submit_button("Submit Shift & Log Out"):
            liters = end_reading - start_reading
            if liters < 0:
                st.error("Error: Closing reading cannot be less than opening!")
            else:
                # Calculate totals (assuming a base price, e.g., 189)
                expected = liters * 189.0 
                total_collected = cash + mpesa
                
                entry = {
                    "attendant_name": user['full_name'],
                    "pump_reading_start": start_reading,
                    "pump_reading_end": end_reading,
                    "liters_sold": liters,
                    "expected_total": expected,
                    "actual_cash": cash,
                    "actual_mpesa": mpesa,
                    "total_collected": total_collected,
                    "difference": total_collected - expected
                }
                supabase.table("shift_logs").insert(entry).execute()
                st.success("Shift successfully recorded!")
                st.session_state.logged_in = False
                st.rerun()

# --- TAB 2: MANAGER TOOLS ---
if user.get('is_admin'):
    with tabs[1]:
        m_tab1, m_tab2 = st.tabs(["📈 View Sales Logs", "👥 Manage Staff"])
        
        with m_tab1:
            st.subheader("Station Performance History")
            logs = supabase.table("shift_logs").select("*").order("created_at", desc=True).execute()
            if logs.data:
                df = pd.DataFrame(logs.data)
                st.dataframe(df, use_container_width=True)
            else:
                st.write("No logs recorded yet.")

        with m_tab2:
            st.subheader("Add New Staff Member")
            with st.form("add_staff"):
                new_name = st.text_input("Staff Full Name")
                new_id = st.text_input("Assign Work ID")
                is_mgr = st.checkbox("Give Manager Access?")
                if st.form_submit_button("Register Staff"):
                    if new_name and new_id:
                        try:
                            supabase.table("staff").insert({
                                "full_name": new_name, 
                                "work_id": new_id, 
                                "is_admin": is_mgr
                            }).execute()
                            st.success(f"Added {new_name} to the system!")
                        except:
                            st.error("ID already exists!")
