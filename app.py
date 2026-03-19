import streamlit as st
from supabase import create_client
import pandas as pd
from PIL import Image
import io
import base64
from datetime import datetime

# 1. DATABASE CONNECTION
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

# Set page to wide and ensure sidebar is visible by default
st.set_page_config(page_title="JC Energy Portal", layout="wide", initial_sidebar_state="expanded")

# 2. BRANDING & CSS
def apply_branding():
    try:
        img = Image.open("Gemini_Generated_Image_ykd8mjykd8mjykd8.jpg")
        buffered = io.BytesIO()
        img.save(buffered, format="JPEG", quality=100)
        img_str = base64.b64encode(buffered.getvalue()).decode()
        logo_html = f'<div class="logo-wrapper"><img src="data:image/jpeg;base64,{img_str}" class="logo-img"></div>'
    except:
        logo_html = "<h1 style='text-align: center; color: #f1c40f;'>JC ENERGY</h1>"

    st.markdown(
        f"""
        <style>
        .stApp {{ background-color: #072a07; }}
        .logo-wrapper {{ display: flex; justify-content: center; padding: 10px 0; }}
        .logo-img {{ max-width: 180px; width: 40%; border-radius: 12px; }}
        .welcome-text {{ color: #f1c40f !important; font-size: 38px !important; font-weight: 800 !important; text-align: center; margin-bottom: 5px; }}
        .yellow-box {{ background-color: #f1c40f; color: black !important; padding: 20px; border-radius: 12px; text-align: center; font-weight: 900; font-size: 24px; margin: 10px 0; }}
        .opening-box {{ background-color: rgba(255, 255, 255, 0.1); border-left: 5px solid #f1c40f; padding: 15px; margin-bottom: 20px; border-radius: 5px; }}
        label {{ color: white !important; font-weight: bold !important; }}
        .stNumberInput input {{ background-color: white !important; color: black !important; font-size: 18px !important; }}
        
        /* SIDEBAR TOGGLE & VISIBILITY FIX */
        [data-testid="stSidebar"] {{ background-color: #041a04; border-right: 1px solid #f1c40f; }}
        
        /* Fixed Yellow Sidebar Arrow for Top Left */
        button[kind="headerNoSpacing"] {{
            background-color: #f1c40f !important;
            color: black !important;
            border-radius: 50% !important;
            left: 10px !important;
            top: 10px !important;
            position: fixed !important;
            z-index: 999999;
        }}
        
        /* Management Dashboard White-Card Visibility */
        .admin-card {{
            background-color: white;
            padding: 20px;
            border-radius: 15px;
            color: black !important;
            margin-bottom: 20px;
        }}
        .admin-card * {{ color: black !important; }}

        header {{visibility: hidden;}}
        </style>
        {logo_html}
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

# 4. SIDEBAR NAVIGATION
user = st.session_state.user
st.sidebar.title("JC Navigation")
menu = ["📝 Record Shift"]
if user['full_name'] == "Peter Kimani" or user.get('role') == 'manager':
    menu.append("👨‍💼 Management")

choice = st.sidebar.radio("Go to:", menu)

if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.rerun()

# --- PAGE 1: RECORD SHIFT (Logic: Opening - Closing) ---
if choice == "📝 Record Shift":
    st.markdown(f'<div class="welcome-text">Welcome, {user["full_name"]}</div>', unsafe_allow_html=True)
    
    res_last = supabase.table("shift_logs").select("pump_reading_end").order("created_at", desc=True).limit(1).execute()
    start_val = float(res_last.data[0]["pump_reading_end"]) if res_last.data else 0.0

    st.markdown(f'<div class="opening-box"><span style="color: #f1c40f;">STATION STATUS</span><br><span style="color: white; font-size: 22px; font-weight: bold;">Opening Reading: {start_val:,} L</span></div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        end_reading = st.number_input("Current Closing Reading (L)", value=start_val, step=0.1)
    with col2:
        price_per_liter = st.number_input("Price per Liter (KES)", value=189.0, step=0.1)

    # MATH: Opening - Closing = Liters Sold
    liters_sold = start_val - end_reading
    total_sales_expected = max(0.0, liters_sold * price_per_liter)
    
    st.markdown(f'<div class="yellow-box">TOTAL SALES: KES {total_sales_expected:,.2f}</div>', unsafe_allow_html=True)
