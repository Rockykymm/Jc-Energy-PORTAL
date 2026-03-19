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

# 2. HIGH-DETAIL BRANDING & DYNAMIC CSS
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
        
        {logo_html}
        .logo-wrapper {{ display: flex; justify-content: center; padding: 10px 0; }}
        .logo-img {{ max-width: 220px; width: 50%; border-radius: 12px; }}

        /* Big Bright Welcome */
        .welcome-text {{
            color: #f1c40f !important;
            font-size: 42px !important;
            font-weight: 800 !important;
            text-align: center;
            margin-bottom: 20px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
        }}

        /* Yellow Calculation Boxes */
        .yellow-box {{
            background-color: #f1c40f;
            color: black !important;
            padding: 15px;
            border-radius: 10px;
            text-align: center;
            font-weight: bold;
            font-size: 20px;
            margin: 10px 0;
        }}
        
        .short-warning {{
            color: #d63031 !important; /* Red text */
            font-size: 24px;
        }}

        /* Input Styling */
        label {{ color: white !important; font-size: 16px !important; }}
        .stNumberInput input {{ background-color: white !important; color: black !important; font-size: 18px !important; }}
        
        /* Submit Button */
        div.stButton > button {{
            background-color: #f1c40f !important;
            color: black !important;
            font-weight: bold !important;
            font-size: 20px !important;
            height: 60px !important;
            border-radius: 15px !important;
            border: none !important;
            margin-top: 20px;
        }}
        header {{visibility: hidden;}}
        </style>
        {logo_html}
        """,
        unsafe_allow_html=True
    )

apply_branding()

# 3. LOGIN SYSTEM
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, col, _ = st.columns([0.1, 0.8, 0.1])
    with col:
        st.markdown("<h3 style='text-align: center; color: white;'>🔐 Staff Access</h3>", unsafe_allow_html=True)
        work_id = st.text_input("Work ID", type="password")
        if st.button("Open Portal", use_container_width=True):
            res = supabase.table("staff").select("*").eq("work_id", work_id).execute()
            if res.data:
                st.session_state.logged_in = True
                st.session_state.user = res.data[0]
                st.rerun()
    st.stop()

# 4. MAIN INTERFACE
user = st.session_state.user
st.markdown(f'<div class="welcome-text">Welcome, {user["full_name"]}</div>', unsafe_allow_html=True)

# Fetch Last Reading
res_last = supabase.table("shift_logs").select("pump_reading_end").order("created_at", desc=True).limit(1).execute()
start_val = float(res_last.data[0]["pump_reading_end"]) if res_last.data else 0.0

with st.form("shift_form"):
    # Row 1: Readings & Price
    col1, col2, col3 = st.columns(3)
    with col1:
        st.write(f"**Opening:** {start_val:,} L")
        end_reading = st.number_input("Closing Reading (L)", value=start_val, step=0.1)
    with col2:
        price_per_liter = st.number_input("Price per Liter (KES)", value=189.0, step=0.5)
    with col3:
        liters_sold = end_reading - start_val
        total_sales_expected = liters_sold * price_per_liter
        st.markdown(f'<div class="yellow-box">Total Sales<br>KES {total_sales_expected:,.2f}</div>', unsafe_allow_html=True)

    # Row 2: Parallel Payments
    p_col1, p_col2 = st.columns(2)
    with p_col1:
        cash = st.number_input("Total Cash (KES)", min_value=0.0)
    with p_col2:
        mpesa = st.number_input("Total M-Pesa (KES)", min_value=0.0)

    # Calculation Logic
    actual_collected = cash + mpesa
    difference = actual_collected - total_sales_expected

    # Display Difference
    if difference < 0:
        st.markdown(f'<div class="yellow-box short-warning">SHORTAGE: KES {abs(difference):,.2f}</div>', unsafe_allow_html=True)
    elif difference > 0:
        st.markdown(f'<div class="yellow-box" style="color: green !important;">OVERAGE: KES {difference:,.2f}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="yellow-box">ACCOUNT BALANCED</div>', unsafe_allow_html=True)

    submit = st.form_submit_button("VERIFY & SUBMIT SHIFT", use_container_width=True)
    
    if submit:
        if liters_sold < 0:
            st.error("Error: Closing reading is lower than opening!")
        else:
            supabase.table("shift_logs").insert({
                "attendant_name": user['full_name'],
                "pump_reading_start": start_val,
                "pump_reading_end": end_reading,
                "liters_sold": liters_sold,
                "total_collected": actual_collected,
                "difference": difference
            }).execute()
            st.success("Shift successfully logged!")
            st.session_state.logged_in = False
            st.rerun()
        df = pd.DataFrame(history.data)
        st.dataframe(df[['created_at', 'liters_sold', 'total_collected']])
    else:
        st.write("No history found.")
