import streamlit as st
import time
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

# 2. PAGE CONFIG
st.set_page_config(
    page_title="JC Energy Portal", 
    page_icon="static/logo.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 3. BRANDING & CSS
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
        .welcome-text {{ color: #f1c40f !important; font-size: 38px !important; font-weight: 800 !important; text-align: center; margin-bottom: 20px; }}
        
        [data-testid="stSidebar"] {{ 
            background-color: #041a04 !important; 
            border-right: 5px solid #f1c40f !important;
            min-width: 250px !important;
        }}
        [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label {{
            color: #FFFFFF !important;
            font-weight: bold !important;
            font-size: 18px !important;
        }}
        
        thead tr th {{
            background-color: #f1c40f !important;
            color: #072a07 !important;
            font-size: 15px !important;
            white-space: nowrap !important;
        }}
        
        tbody tr td {{
            background-color: #041a04 !important;
            color: #FFFFFF !important;
            white-space: nowrap !important;
            font-weight: 500;
            border-bottom: 1px solid #1e3d1e !important;
        }}
        
        tbody tr:nth-child(even) {{
            background-color: #072a07 !important;
        }}
        
        .stTable {{
            overflow-x: auto;
            display: block;
            border: 1px solid #f1c40f !important;
            border-radius: 8px;
        }}
        
        .readable-card {{
            background-color: white;
            padding: 30px;
            border-radius: 15px;
            color: black !important;
            margin-bottom: 25px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        }}
        .readable-card h3, .readable-card p, .readable-card label, .readable-card span {{
            color: black !important;
        }}
        
        [data-testid="stMetricValue"] {{
            color: #072a07 !important;
            font-weight: 900 !important;
        }}
        
        .stTextInput label p {{
            color: #f1c40f !important; 
            font-size: 16px !important;
        }}
        </style>
        {logo_html}
        """,
        unsafe_allow_html=True
    )

apply_branding()

# 4. AUTHENTICATION LOGIC
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, col, _ = st.columns([0.2, 0.6, 0.2])
    with col:
        st.markdown("<h3 style='text-align: center; color: white;'>🔐 Staff Portal Login</h3>", unsafe_allow_html=True)
        work_id = st.text_input("Enter Work ID", type="password")
        if st.button("Access System", use_container_width=True):
            res = supabase.table("staff").select("*").eq("work_id", work_id).execute()
            if res.data:
                st.session_state.logged_in = True
                st.session_state.user = res.data[0]
                st.rerun()
            else:
                st.error("Invalid Work ID. Please contact Peter Kimani.")
    st.stop()

# 5. SIDEBAR NAVIGATION
user = st.session_state.user
with st.sidebar:
    st.markdown("<h2 style='color: #f1c40f; text-align: center;'>SYSTEM MENU</h2>", unsafe_allow_html=True)
    st.markdown(f"👤 **User:** {user['full_name']}")
    st.write("---")
    
    menu = ["📝 Record Shift"]
    if user['full_name'] == "Peter Kimani" or user.get('role') == 'manager':
        menu.append("👨‍💼 Management")
    
    choice = st.radio("SELECT PAGE:", menu, index=0)
    
    st.write("---")
    if st.button("🚪 Logout System", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()

# 6. PAGE 1: RECORD SHIFT
if choice == "📝 Record Shift":
    st.markdown(f'<div class="welcome-text">Welcome, {user["full_name"]}</div>', unsafe_allow_html=True)
    
    res_last = supabase.table("shift_logs").select("*").order("created_at", desc=True).limit(20).execute()
    
    prev_tank_end = float(res_last.data[0]["pump_reading_end"]) if res_last.data else 0.0
    prev_mtr_end = float(res_last.data[0]["meter_reading_end"]) if res_last.data else 0.0

    today_str = datetime.now().strftime('%Y-%m-%d')
    tank_entries_today = [d for d in res_last.data if pd.to_datetime(d['created_at']).strftime('%Y-%m-%d') == today_str] if res_last.data else []
    tank_already_done = len(tank_entries_today) > 0

    with st.expander("📊 DAILY TANK DIPSTICK (6:00 AM ONLY)", expanded=not tank_already_done):
        if tank_already_done:
            st.success("✅ Today's 6 AM Dipstick reading is already recorded.")
            tank_start = float(tank_entries_today[-1]["pump_reading_start"])
            tank_end = float(tank_entries_today[-1]["pump_reading_end"])
        else:
            st.warning("🌅 Please enter the 6 AM cold-fuel dipstick readings.")
            col_t1, col_t2 = st.columns(2)
            tank_start = col_t1.number_input("Opening Tank (L)", value=prev_tank_end)
            tank_end = col_t2.number_input("Closing Tank (L) [Dipstick]", value=prev_tank_end)

    st.write("---")

    st.subheader("⛽ Shift Meter Readings")
    col_m1, col_m2, col_p = st.columns(3)
    with col_m1:
        mtr_start = st.number_input("Meter Start (L)", value=prev_mtr_end, disabled=True)
    with col_m2:
        mtr_end = st.number_input("Meter End (L)", value=prev_mtr_end, step=0.1)
    with col_p:
        price = st.number_input("Price (KES/L)", value=189.0, step=0.1)

    liters_sold = mtr_end - mtr_start
    total_sales_expected = liters_sold * price
    
    st.markdown(f'<div style="background: #f1c40f; color: black; padding: 20px; border-radius: 10px; text-align: center; font-weight: 800; font-size: 24px; margin: 15px 0; border: 2px solid white;">EXPECTED REVENUE: KES {max(0.0, total_sales_expected):,.2f}</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    cash = c1.number_input("Total Cash Collected (KES)", min_value=0.0)
    mpesa = c2.number_input("Total M-Pesa / Till (KES)", min_value=0.0)

    if st.button("FINALIZE SHIFT", use_container_width=True):
        actual_total = cash + mpesa
        diff = actual_total - total_sales_expected

        if mtr_end < mtr_start:
            st.error("🚨 Error: Closing meter cannot be lower than opening!")
        elif not tank_already_done:
            st.error("🚨 Please record the dipstick reading before finalizing the shift.")
        else:
            with st.spinner("Recording Shift..."): 
                try:
                    supabase.table("shift_logs").insert({
                        "attendant_name": user['full_name'], 
                        "pump_reading_start": tank_start,
                        "pump_reading_end": tank_end, 
                        "meter_reading_start": mtr_start,
                        "meter_reading_end": mtr_end,
                        "liters_sold": liters_sold,
                        "price_per_ltr": price, 
                        "total_sales": total_sales_expected,
                        "cash": cash, 
                        "till": mpesa, 
                        "difference": diff
                    }).execute()
                    
                    st.success("✨ SHIFT SUCCESSFULLY RECORDED!")
                    time.sleep(2)
                    st.session_state.logged_in = False
                    st.rerun()
                except Exception as e:
                    st.error(f"Database Error: {e}")

# 7. PAGE 2: MANAGEMENT
elif choice == "👨‍💼 Management":
    st.markdown('<div class="welcome-text">Business Management Dashboard</div>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["📊 Sales & Logs", "👤 Team Management"])
    
    st.markdown(
    f"""
    <style>
    .stApp {{ background-color: #072a07; }}
    .logo-wrapper {{ display: flex; justify-content: center; padding: 10px 0; }}
    .logo-img {{ max-width: 180px; width: 40%; border-radius: 12px; }}
    .welcome-text {{ color: #f1c40f !important; font-size: 38px !important; font-weight: 800 !important; text-align: center; margin-bottom: 20px; }}
    
    [data-testid="stSidebar"] {{ 
        background-color: #041a04 !important; 
        border-right: 5px solid #f1c40f !important;
        min-width: 250px !important;
    }}
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label {{
        color: #FFFFFF !important;
        font-weight: bold !important;
        font-size: 18px !important;
    }}
    
    /* MANAGEMENT PAGE: WHITE BACKGROUND */
    [data-testid="stTabs"] {{
        background-color: white !important;
        padding: 30px !important;
        border-radius: 15px !important;
    }}
    
    /* TABLE STYLING: WHITE BG + BLACK TEXT */
    thead tr th {{
        background-color: #f1c40f !important;
        color: #072a07 !important;
        font-weight: bold !important;
    }}
    
    tbody tr td {{
        background-color: #FFFFFF !important;
        color: #000000 !important;
        padding: 12px 8px !important;
    }}
    
    tbody tr:nth-child(even) {{
        background-color: #F5F5F5 !important;
    }}
    
    /* CARDS */
    .readable-card {{
        background-color: white;
        padding: 30px;
        border-radius: 15px;
        color: black !important;
    }}
    .readable-card h2, .readable-card h3, .readable-card p {{
        color: black !important;
    }}
    
    /* METRICS */
    [data-testid="stMetricValue"] {{
        color: #072a07 !important;
        font-weight: 900 !important;
    }}
    </style>
    {logo_html}
    """,
    unsafe_allow_html=True
)
    with tab2:
        st.markdown('<div class="readable-card">', unsafe_allow_html=True)
        st.markdown("### Active Staff Members")
        staff_res = supabase.table("staff").select("*").execute()
        
        if staff_res.data:
            for s in staff_res.data:
                c1, c2 = st.columns([0.8, 0.2])
                c1.write(f"👤 **{s['full_name']}** (Work ID: {s['work_id']})")
                if c2.button("Remove", key=f"rem_{s['id']}", use_container_width=True):
                    supabase.table("staff").delete().eq("id", s['id']).execute()
                    st.toast(f"Removed {s['full_name']}")
                    st.rerun()
        
        st.write("---")
        st.markdown("#### ➕ Register New Staff")
        with st.form("add_staff_form", clear_on_submit=True):
            n_name = st.text_input("Employee Full Name")
            n_id = st.text_input("Assign Unique Work ID")
            if st.form_submit_button("Save Employee"):
                if n_name and n_id:
                    supabase.table("staff").insert({"full_name": n_name, "work_id": n_id}).execute()
                    st.success(f"Successfully added {n_name}")
                    st.rerun()
                else:
                    st.warning("Both fields are required.")
        st.markdown('</div>', unsafe_allow_html=True)
