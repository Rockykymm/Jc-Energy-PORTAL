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

st.set_page_config(page_title="JC Energy Portal", layout="wide", initial_sidebar_state="expanded")

# 2. BRANDING & CSS (MAXIMUM READABILITY)
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
        .welcome-text {{ color: #f1c40f !important; font-size: 38px !important; font-weight: 800 !important; text-align: center; }}
        
        /* SIDEBAR: DARK GREEN WITH YELLOW BORDER */
        [data-testid="stSidebar"] {{ 
            background-color: #041a04 !important; 
            border-right: 5px solid #f1c40f !important;
        }}
        
        /* SIDEBAR TEXT: FORCED BRIGHT WHITE */
        [data-testid="stSidebar"] p, 
        [data-testid="stSidebar"] span, 
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] .stMarkdown {{
            color: #FFFFFF !important;
            font-weight: bold !important;
            font-size: 18px !important;
        }}

        /* RADIO BUTTON TEXT: LARGE & WHITE */
        div[data-testid="stSidebar"] .stRadio label div[data-testid="stMarkdownContainer"] p {{
            color: #FFFFFF !important;
            font-size: 20px !important;
        }}

        /* MANAGEMENT DASHBOARD CARDS: HIGH CONTRAST */
        .readable-card {{
            background-color: white;
            padding: 30px;
            border-radius: 15px;
            color: black !important;
            margin-bottom: 20px;
        }}
        .readable-card h2, .readable-card h3, .readable-card p, .readable-card span {{
            color: black !important;
            font-weight: bold;
        }}
        
        /* METRIC STYLING */
        [data-testid="stMetricValue"] {{
            color: #072a07 !important;
            font-weight: 900 !important;
        }}
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
with st.sidebar:
    st.markdown("<h2 style='color: #f1c40f; text-align: center;'>NAVIGATION</h2>", unsafe_allow_html=True)
    st.markdown(f"👤 **{user['full_name']}**")
    st.write("---")
    
    menu = ["📝 Record Shift"]
    # Check if user is the admin (Peter Kimani) or has a manager role
    if user['full_name'] == "Peter Kimani" or user.get('role') == 'manager':
        menu.append("👨‍💼 Management")
    
    choice = st.radio("GO TO:", menu, index=0)
    
    st.write("---")
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()

# --- PAGE 1: RECORD SHIFT ---
if choice == "📝 Record Shift":
    st.markdown(f'<div class="welcome-text">Welcome, {user["full_name"]}</div>', unsafe_allow_html=True)
    
    # Get last closing reading from database
    res_last = supabase.table("shift_logs").select("pump_reading_end").order("created_at", desc=True).limit(1).execute()
    start_val = float(res_last.data[0]["pump_reading_end"]) if res_last.data else 0.0

    st.markdown(f'<div style="background: rgba(255,255,255,0.1); border-left: 5px solid #f1c40f; padding: 15px; border-radius: 5px;">'
                f'<span style="color: #f1c40f;">STATION STATUS</span><br>'
                f'<span style="color: white; font-size: 24px; font-weight: bold;">Opening Reading: {start_val:,} L</span></div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        end_reading = st.number_input("Current Closing Reading (L)", value=start_val, step=0.1)
    with col2:
        price_per_liter = st.number_input("Price per Liter (KES)", value=189.0, step=0.1)

    liters_sold = start_val - end_reading
    total_sales_expected = liters_sold * price_per_liter
    
    st.markdown(f'<div style="background: #f1c40f; color: black; padding: 20px; border-radius: 12px; text-align: center; font-weight: 900; font-size: 24px; margin: 10px 0;">'
                f'TOTAL SALES: KES {max(0.0, total_sales_expected):,.2f}</div>', unsafe_allow_html=True)

    pay_col1, pay_col2 = st.columns(2)
    with pay_col1:
        cash = st.number_input("Cash Collected (KES)", min_value=0.0)
    with pay_col2:
        mpesa = st.number_input("M-Pesa Collected (KES)", min_value=0.0)

    actual = cash + mpesa
    diff = actual - total_sales_expected

    if st.button("VERIFY & SUBMIT SHIFT", use_container_width=True):
        if end_reading > start_val:
            st.error("🚨 Error: Closing reading cannot be higher than opening!")
        else:
            supabase.table("shift_logs").insert({
                "attendant_name": user['full_name'], "pump_reading_start": start_val,
                "pump_reading_end": end_reading, "liters_sold": liters_sold,
                "total_collected": actual, "difference": diff
            }).execute()
            st.success("Shift Logged Successfully!")
            st.rerun()

# --- PAGE 2: MANAGEMENT (FULL RESTORED VERSION) ---
elif choice == "👨‍💼 Management":
    st.markdown('<div class="welcome-text">Management Dashboard</div>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["📊 Business Logs", "👥 Staff Management"])
    
    with tab1:
        st.markdown('<div class="readable-card">', unsafe_allow_html=True)
        st.markdown("### Business Performance")
        logs_res = supabase.table("shift_logs").select("*").order("created_at", desc=True).execute()
        
        if logs_res.data:
            df = pd.DataFrame(logs_res.data)
            m1, m2, m3 = st.columns(3)
            m1.metric("Liters Sold", f"{df['liters_sold'].sum():,.1f}")
            m2.metric("Total Revenue", f"KES {df['total_collected'].sum():,.2f}")
            m3.metric("Net Difference", f"KES {df['difference'].sum():,.2f}")
            
            st.write("---")
            st.markdown("#### All Shift Records")
            # Format date for readability
            df['created_at'] = pd.to_datetime(df['created_at']).dt.strftime('%Y-%m-%d %H:%M')
            st.dataframe(df[['created_at', 'attendant_name', 'liters_sold', 'total_collected', 'difference']], use_container_width=True)
        else:
            st.info("No logs found yet.")
        st.markdown('</div>', unsafe_allow_html=True)

    with tab2:
        st.markdown('<div class="readable-card">', unsafe_allow_html=True)
        st.markdown("### Staff Directory")
        staff_res = supabase.table("staff").select("*").execute()
        
        if staff_res.data:
            for s in staff_res.data:
                c1, c2 = st.columns([0.8, 0.2])
                c1.write(f"👤 **{s['full_name']}** (Work ID: {s['work_id']})")
                if c2.button("Remove", key=f"rem_{s['id']}"):
                    supabase.table("staff").delete().eq("id", s['id']).execute()
                    st.success(f"Removed {s['full_name']}")
                    st.rerun()
        
        st.write("---")
        with st.expander("➕ Add New Employee"):
            new_name = st.text_input("Full Name")
            new_id = st.text_input("Assign Work ID")
            if st.button("Save New Staff Member"):
                if new_name and new_id:
                    supabase.table("staff").insert({"full_name": new_name, "work_id": new_id}).execute()
                    st.success(f"Added {new_name}")
                    st.rerun()
                else:
                    st.warning("Please enter both name and ID.")
        st.markdown('</div>', unsafe_allow_html=True)
