import streamlit as st

# This MUST be the first streamlit command in the file
st.set_page_config(
    page_title="JC Energy Portal", 
    page_icon="static/logo.png",
    layout="wide"
)

# This is the "magic" link that tells your phone to show the 'Install' button
st.markdown(
    """
    <link rel="manifest" href="/app/static/manifest.json">
    <link rel="icon" href="/app/static/logo.png" type="image/png">
    <link rel="apple-touch-icon" href="/app/static/logo.png">
    <meta name="mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    """,
    unsafe_allow_html=True
)

# ...
import time
import streamlit as st
from supabase import create_client
import pandas as pd
from PIL import Image
import io
import base64
from datetime import datetime

# 1. DATABASE CONNECTION
# Ensure these secrets are set in your Streamlit Cloud dashboard
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

# FORCE WIDE LAYOUT & OPEN SIDEBAR
st.set_page_config(
    page_title="JC Energy Portal", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# 2. BRANDING & FULL CSS (SIDEBAR + 8-COLUMN TABLE + CARDS)
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
        /* Main Background */
        .stApp {{ background-color: #072a07; }}
        
        .logo-wrapper {{ display: flex; justify-content: center; padding: 10px 0; }}
        .logo-img {{ max-width: 180px; width: 40%; border-radius: 12px; }}
        .welcome-text {{ color: #f1c40f !important; font-size: 38px !important; font-weight: 800 !important; text-align: center; margin-bottom: 20px; }}
        
        /* SIDEBAR: BRIGHT WHITE TEXT & YELLOW BORDER */
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
        div[data-testid="stSidebar"] .stRadio label div[data-testid="stMarkdownContainer"] p {{
            color: #FFFFFF !important;
            font-size: 20px !important;
        }}

       /* TABLE STYLING: DARK ROWS FOR WHITE TEXT VISIBILITY */
        thead tr th {{
            background-color: #f1c40f !important; /* Yellow Header */
            color: #072a07 !important; /* Dark Green Text on Header */
            font-size: 15px !important;
            white-space: nowrap !important;
        }}
        
        /* This makes the rows dark so your white text stands out */
        tbody tr td {{
            background-color: #041a04 !important; /* Dark Green background */
            color: #FFFFFF !important; /* Forced White Text */
            white-space: nowrap !important;
            font-weight: 500;
            border-bottom: 1px solid #1e3d1e !important;
        }}

        /* Subtle stripe for row separation */
        tbody tr:nth-child(even) {{
            background-color: #072a07 !important;
        }}
        
        .stTable {{
            overflow-x: auto;
            display: block;
            border: 1px solid #f1c40f !important;
            border-radius: 8px;
        }}

        /* MANAGEMENT DASHBOARD CARDS (Ensures text inside stays black) */
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
        
        /* METRIC VALUES */
        [data-testid="stMetricValue"] {{
            color: #072a07 !important;
            font-weight: 900 !important;
        }}

        /* --- UPGRADED TEAM MANAGEMENT VISIBILITY --- */
        /* Forces text on the green background to be white/yellow */
        #active-staff-members, #register-new-staff, 
        [data-testid="stVerticalBlock"] p, 
        [data-testid="stVerticalBlock"] label {{
            color: #FFFFFF !important;
        }}
        
        /* Specific contrast for Input Labels */
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

# 3. AUTHENTICATION LOGIC
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

# 4. SIDEBAR NAVIGATION
user = st.session_state.user
with st.sidebar:
    st.markdown("<h2 style='color: #f1c40f; text-align: center;'>SYSTEM MENU</h2>", unsafe_allow_html=True)
    st.markdown(f"👤 **User:** {user['full_name']}")
    st.write("---")
    
    menu = ["📝 Record Shift"]
    # Check if user is the Owner (Peter Kimani) or a Manager
    if user['full_name'] == "Peter Kimani" or user.get('role') == 'manager':
        menu.append("👨‍💼 Management")
    
    choice = st.radio("SELECT PAGE:", menu, index=0)
    
    st.write("---")
    if st.button("🚪 Logout System", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()

# --- PAGE 1: RECORD SHIFT ---
if choice == "📝 Record Shift":
    st.markdown(f'<div class="welcome-text">Welcome, {user["full_name"]}</div>', unsafe_allow_html=True)
    
    # 1. GET OPENING READINGS (LITRES & METER)
    res_last = supabase.table("shift_logs").select("pump_reading_end", "meter_reading_end").order("created_at", desc=True).limit(1).execute()
    
    start_val = float(res_last.data[0]["pump_reading_end"]) if res_last.data else 0.0
    start_mtr = float(res_last.data[0]["meter_reading_end"]) if res_last.data else 0.0

    # Display both in the status card
    st.markdown(f'<div style="background: rgba(255,255,255,0.1); border-left: 5px solid #f1c40f; padding: 20px; border-radius: 8px; margin-bottom: 20px;">'
                f'<span style="color: #f1c40f; font-weight: bold;">STATION STATUS</span><br>'
                f'<span style="color: white; font-size: 20px;">Opening Litres: {start_val:,.1f} L</span><br>'
                f'<span style="color: white; font-size: 20px;">Opening Meter: {start_mtr:,.1f} Mtr</span></div>', unsafe_allow_html=True)
    # 2. INPUT DATA
    col1, col2, col3 = st.columns(3)
    with col1:
        end_reading = st.number_input("Closing Litres (L)", value=start_val, step=0.1)
    with col2:
        end_mtr = st.number_input("Closing Meter (Mtr)", value=start_mtr, step=0.1)
    with col3:
        price_per_liter = st.number_input("Price (KES/L)", value=189.0, step=0.1)
    # 3. CALCULATIONS (Use Meter for Sales)
    liters_sold = end_mtr - start_mtr  # Sales volume comes from Meter
    total_sales_expected = liters_sold * price_per_liter
    
    # ... (Keep your revenue display and cash/mpesa inputs the same) ...

    # Inside the "FINALIZE SHIFT" button logic, update the insert dictionary:
    if st.button("FINALIZE SHIFT", use_container_width=True):
        # Calculate again to be sure
        liters_sold = end_mtr - start_mtr 
        total_sales_expected = liters_sold * price_per_liter
        actual_collected = cash + mpesa
        diff = actual_collected - total_sales_expected

        # Update the database columns (Make sure these exist in Supabase!)
        supabase.table("shift_logs").insert({
            "attendant_name": user['full_name'], 
            "pump_reading_start": start_val,
            "pump_reading_end": end_reading, 
            "meter_reading_start": start_mtr, # New Column
            "meter_reading_end": end_mtr,     # New Column
            "liters_sold": liters_sold,
            "price_per_ltr": price_per_liter, 
            "total_sales": total_sales_expected,
            "cash": cash, 
            "till": mpesa, 
            "difference": diff
        }).execute()
                
        # 2. THE EXIT SEQUENCE
        # Show your specific message in a big green success box
        st.success("✨ THANK YOU, SHIFT OVER!")
                
        # Wait 3 seconds so they can read it
        time.sleep(3)
                
        # Reset login status and force refresh to the Login Page
        st.session_state.logged_in = False
        st.rerun()
# --- PAGE 2: MANAGEMENT (FULL RESTORED VERSION) ---
elif choice == "👨‍💼 Management":
    st.markdown('<div class="welcome-text">Business Management Dashboard</div>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["📊 Sales & Logs", "👥 Team Management"])
    
    with tab1:
        st.markdown('<div class="readable-card">', unsafe_allow_html=True)
        st.markdown("### Performance Overview")
        logs_res = supabase.table("shift_logs").select("*").order("created_at", desc=True).execute()
        
        if logs_res.data:
            df = pd.DataFrame(logs_res.data)
            
            # --- CRASH PROTECTION (KEYERROR FIX) ---
            req_cols = ['total_sales', 'liters_sold', 'difference', 'price_per_ltr', 'cash', 'till']
            for c in req_cols:
                if c not in df.columns: df[c] = 0.0

            # Summary Metrics
            m1, m2, m3 = st.columns(3)
            m1.metric("Total Volume", f"{df['liters_sold'].sum():,.1f} L")
            m2.metric("Total Revenue", f"KES {df['total_sales'].sum():,.2f}")
            m3.metric("Net Balance", f"KES {df['difference'].sum():,.2f}")
            
            st.write("---")
            st.markdown("### All Shift Records (8 Columns)")
            
            # Format Data
            df['created_at'] = pd.to_datetime(df['created_at']).dt.strftime('%Y-%m-%d %H:%M')
            
            def get_status(val):
                if val < -2: return f"🔴 Shortage (KES {abs(val):,.0f})"
                if val > 2: return f"🟢 Excess (KES {val:,.0f})"
                return "⚪ Balanced"
            
            df['Shift Status'] = df['difference'].apply(get_status)
            
            # SELECT THE 8 SPECIFIC COLUMNS
            display_df = df[[
                'created_at', 'attendant_name', 'liters_sold', 
                'price_per_ltr', 'total_sales', 'cash', 'till', 'Shift Status'
            ]]
            
            # Rename for display
            display_df.columns = [
                'Date/Time', 'Attendant', 'Liters Sold', 
                'Price/Ltr', 'Total Sales', 'Cash', 'Till (M-Pesa)', 'Shift Status'
            ]
            
            # Display Table
            st.table(display_df)
        else:
            st.info("No sales records found in the database yet.")
        st.markdown('</div>', unsafe_allow_html=True)

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
