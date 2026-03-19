import streamlit as st
from supabase import create_client
import pandas as pd
from PIL import Image
import io
import base64

# 1. DATABASE CONNECTION
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

st.set_page_config(page_title="JC Energy Portal", layout="wide")

# 2. BRANDING & CSS OVERHAUL (Visibility Focus)
def apply_branding():
    st.markdown(
        f"""
        <style>
        .stApp {{ background-color: #072a07; }}
        
        /* High Visibility Text Cards */
        .white-card {{
            background-color: white;
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0px 4px 10px rgba(0,0,0,0.3);
            margin-bottom: 20px;
        }}
        
        .card-text {{
            color: #072a07 !important;
            font-weight: bold !important;
        }}

        .welcome-text {{
            color: #f1c40f !important;
            font-size: 38px !important;
            font-weight: 800 !important;
            text-align: center;
        }}

        /* Table Styling for Visibility */
        [data-testid="stMetricValue"] {{
            background-color: white;
            padding: 10px;
            border-radius: 10px;
            color: #072a07 !important;
        }}
        
        header {{visibility: hidden;}}
        </style>
        """,
        unsafe_allow_html=True
    )

apply_branding()

# 3. LOGIN SESSION
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, col, _ = st.columns([0.1, 0.8, 0.1])
    with col:
        st.markdown("<h3 style='text-align: center; color: white;'>🔐 Staff Login</h3>", unsafe_allow_html=True)
        work_id = st.text_input("Work ID", type="password")
        if st.button("Open Portal", use_container_width=True):
            res = supabase.table("staff").select("*").eq("work_id", work_id).execute()
            if res.data:
                st.session_state.logged_in = True
                st.session_state.user = res.data[0]
                st.rerun()
    st.stop()

# 4. NAVIGATION
user = st.session_state.user
st.sidebar.title("JC Navigation")
menu = ["📝 Record Shift"]
if user['full_name'] == "Peter Kimani":
    menu.append("👨‍💼 Management")

choice = st.sidebar.radio("Navigate to:", menu)

if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.rerun()

# --- PAGE 1: RECORD SHIFT (Stock-Down Logic) ---
if choice == "📝 Record Shift":
    st.markdown(f'<div class="welcome-text">Shift Entry: {user["full_name"]}</div>', unsafe_allow_html=True)
    
    # Fetch Opening Stock
    res_last = supabase.table("shift_logs").select("pump_reading_end").order("created_at", desc=True).limit(1).execute()
    start_stock = float(res_last.data[0]["pump_reading_end"]) if res_last.data else 0.0

    st.markdown(f"""
        <div style="background-color: white; padding: 15px; border-radius: 10px; border-left: 8px solid #f1c40f; margin-bottom: 20px;">
            <p style="color: gray; margin: 0;">CURRENT FUEL STOCK</p>
            <h2 style="color: black; margin: 0;">{start_stock:,} Liters</h2>
        </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        closing_reading = st.number_input("End of Shift Reading (Liters)", value=start_stock, step=0.1)
    with col2:
        price = st.number_input("Rate per Liter (KES)", value=189.0)

    # Calculation: Opening - Closing = Liters Sold
    liters_depleted = start_stock - closing_reading
    expected_cash = liters_depleted * price

    st.markdown(f"""
        <div style="background-color: #f1c40f; padding: 20px; border-radius: 10px; text-align: center;">
            <h4 style="color: black; margin: 0;">EXPECTED REVENUE</h4>
            <h1 style="color: black; margin: 0;">KES {expected_cash:,.2f}</h1>
        </div>
    """, unsafe_allow_html=True)

    st.write("---")
    c_col1, c_col2 = st.columns(2)
    with c_col1:
        cash = st.number_input("Physical Cash Handed Over", min_value=0.0)
    with c_col2:
        mpesa = st.number_input("Total M-Pesa Record", min_value=0.0)

    total_actual = cash + mpesa
    balance = total_actual - expected_cash

    if balance < 0:
        st.error(f"⚠️ SHORTAGE: KES {abs(balance):,.2f}")
    elif balance > 0:
        st.success(f"✅ OVERAGE: KES {balance:,.2f}")
    else:
        st.info("✅ ACCOUNT PERFECTLY BALANCED")

    if st.button("SUBMIT & CLOSE SHIFT", use_container_width=True):
        if closing_reading > start_stock:
            st.warning("Error: Closing reading cannot be higher than current stock!")
        else:
            supabase.table("shift_logs").insert({
                "attendant_name": user['full_name'], 
                "pump_reading_start": start_stock,
                "pump_reading_end": closing_reading, 
                "liters_sold": liters_depleted,
                "total_collected": total_actual, 
                "difference": balance
            }).execute()
            st.success("Log saved to Supabase.")
            st.rerun()

# --- PAGE 2: MANAGEMENT (New Audit & Remove Features) ---
elif choice == "👨‍💼 Management":
    st.markdown('<div class="welcome-text">Management Dashboard</div>', unsafe_allow_html=True)
    
    t1, t2 = st.tabs(["📊 Audit Logs", "👥 Team Management"])
    
    with t1:
        # WHITE BACKGROUND CARD FOR LOGS
        st.markdown('<div class="white-card">', unsafe_allow_html=True)
        logs_res = supabase.table("shift_logs").select("*").order("created_at", desc=True).execute()
        
        if logs_res.data:
            df = pd.DataFrame(logs_res.data)
            
            # Individual Performance Breakdown
            st.subheader("Performance by Person")
            person_stats = df.groupby('attendant_name').agg({
                'liters_sold': 'sum',
                'total_collected': 'sum',
                'difference': 'sum'
            }).reset_index()
            st.table(person_stats)

            st.write("---")
            st.subheader("All Shift History")
            st.dataframe(df, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with t2:
        st.markdown('<div class="white-card">', unsafe_allow_html=True)
        st.subheader("Current Active Staff")
        staff_res = supabase.table("staff").select("*").execute()
        
        if staff_res.data:
            for s in staff_res.data:
                sc1, sc2 = st.columns([0.8, 0.2])
                sc1.write(f"**{s['full_name']}** (ID: {s['work_id']})")
                # Remove Button (The logic to delete from DB)
                if sc2.button("Remove", key=s['id']):
                    supabase.table("staff").delete().eq("id", s['id']).execute()
                    st.success(f"Removed {s['full_name']}")
                    st.rerun()

        st.write("---")
        st.subheader("Add New Attendant")
        with st.form("add_staff"):
            n_name = st.text_input("Full Name")
            n_id = st.text_input("New Work ID")
            if st.form_submit_button("Enroll Employee"):
                supabase.table("staff").insert({"full_name": n_name, "work_id": n_id}).execute()
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
