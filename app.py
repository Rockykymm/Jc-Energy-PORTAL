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

# 2. BRANDING & CSS OVERHAUL
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
        .logo-img {{ max-width: 200px; width: 45%; border-radius: 12px; }}

        /* Big Bright Welcome */
        .welcome-text {{
            color: #f1c40f !important;
            font-size: clamp(30px, 5vw, 42px) !important;
            font-weight: 800 !important;
            text-align: center;
            margin-bottom: 5px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
        }}

        /* Opening Reading Visibility */
        .opening-box {{
            background-color: rgba(255, 255, 255, 0.1);
            border-left: 5px solid #f1c40f;
            padding: 15px;
            margin-bottom: 20px;
            border-radius: 5px;
        }}

        /* Live Yellow Calculation Boxes */
        .yellow-box {{
            background-color: #f1c40f;
            color: black !important;
            padding: 20px;
            border-radius: 12px;
            text-align: center;
            font-weight: 900;
            font-size: 24px;
            margin: 10px 0;
            box-shadow: 0px 4px 15px rgba(0,0,0,0.3);
        }}
        
        .short-text {{
            color: #b33939 !important; /* Deep Red for visibility */
            display: block;
            font-size: 28px;
        }}

        /* Input Adjustments */
        label {{ color: white !important; font-weight: bold !important; }}
        .stNumberInput input {{ background-color: white !important; color: black !important; font-size: 20px !important; }}
        
        div.stButton > button {{
            background-color: #f1c40f !important;
            color: black !important;
            font-weight: bold !important;
            font-size: 22px !important;
            height: 65px !important;
            border-radius: 15px !important;
            border: 3px solid #d4ac0d !important;
        }}
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

# 4. LIVE CALCULATOR INTERFACE
user = st.session_state.user
st.markdown(f'<div class="welcome-text">Welcome, {user["full_name"]}</div>', unsafe_allow_html=True)

# Fetch Last Reading
res_last = supabase.table("shift_logs").select("pump_reading_end").order("created_at", desc=True).limit(1).execute()
start_val = float(res_last.data[0]["pump_reading_end"]) if res_last.data else 0.0

# BIG VISIBLE OPENING READING
st.markdown(f"""
    <div class="opening-box">
        <span style="color: #f1c40f; font-size: 18px;">STATION STATUS</span><br>
        <span style="color: white; font-size: 26px; font-weight: bold;">Opening Pump Reading: {start_val:,} Liters</span>
    </div>
""", unsafe_allow_html=True)

# FORM WITH LIVE UPDATES
# Note: In Streamlit, values update as soon as the user clicks out of the box or presses Enter
with st.container():
    col1, col2 = st.columns(2)
    with col1:
        end_reading = st.number_input("Current Closing Reading (L)", value=start_val, step=0.1)
    with col2:
        price_per_liter = st.number_input("Price per Liter (KES)", value=189.0, step=0.1)

    # ACTIVE CALCULATION
    liters_sold = end_reading - start_val
    total_sales_expected = liters_sold * price_per_liter

    # BIG YELLOW SALES BOX
    st.markdown(f'<div class="yellow-box">TOTAL SALES: KES {total_sales_expected:,.2f}</div>', unsafe_allow_html=True)

    st.markdown("---")
    
    # PARALLEL PAYMENT SECTION
    pay_col1, pay_col2 = st.columns(2)
    with pay_col1:
        cash = st.number_input("Cash in Hand (KES)", min_value=0.0, step=1.0)
    with pay_col2:
        mpesa = st.number_input("M-Pesa Total (KES)", min_value=0.0, step=1.0)

    actual_collected = cash + mpesa
    difference = actual_collected - total_sales_expected

    # STATUS INDICATOR
    if difference < 0:
        st.markdown(f'<div class="yellow-box"><span class="short-text">SHORTAGE: KES {abs(difference):,.2f}</span></div>', unsafe_allow_html=True)
    elif difference > 0:
        st.markdown(f'<div class="yellow-box" style="color: #27ae60 !important;">OVERAGE: KES {difference:,.2f}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="yellow-box" style="color: #27ae60 !important;">ACCOUNT BALANCED ✔</div>', unsafe_allow_html=True)

    st.write("") # Spacer
    if st.button("VERIFY & SUBMIT SHIFT", use_container_width=True):
        if liters_sold < 0:
            st.error("🚨 ALERT: Closing reading cannot be lower than opening!")
        else:
            supabase.table("shift_logs").insert({
                "attendant_name": user['full_name'],
                "pump_reading_start": start_val,
                "pump_reading_end": end_reading,
                "liters_sold": liters_sold,
                "total_collected": actual_collected,
                "difference": difference
            }).execute()
            st.balloons()
            st.success("Shift record saved to cloud. Logging out...")
            st.session_state.logged_in = False
            st.rerun()
