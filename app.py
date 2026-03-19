import streamlit as st
from supabase import create_client
import pandas as pd
from PIL import Image
import io
import base64
from datetime import datetime

# ==========================================
# 1. DATABASE CONNECTION & CONFIG
# ==========================================
# Credentials from Streamlit Secrets
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

# Set page to Wide Mode and keep Sidebar open
st.set_page_config(
    page_title="JC Energy Portal", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# ==========================================
# 2. BRANDING & HIGH-VISIBILITY CSS
# ==========================================
def apply_branding():
    try:
        # Load the JC Energy Logo
        img = Image.open("Gemini_Generated_Image_ykd8mjykd8mjykd8.jpg")
        buffered = io.BytesIO()
        img.save(buffered, format="JPEG", quality=100)
        img_str = base64.b64encode(buffered.getvalue()).decode()
        logo_html = f'<div class="logo-wrapper"><img src="data:image/jpeg;base64,{img_str}" class="logo-img"></div>'
    except:
        # Fallback if image is missing
        logo_html = "<h1 style='text-align: center; color: #f1c40f;'>JC ENERGY</h1>"

    st.markdown(
        f"""
        <style>
        /* MAIN BACKGROUND */
        .stApp, [data-testid="stHeader"] {{ 
            background-color: #072a07 !important; 
        }}
        
        /* FIXING INVISIBLE TEXT LABELS */
        /* This ensures "Current Closing Reading", "Cash Collected", etc. are bright white */
        p, span, label, .stMarkdown, [data-testid="stWidgetLabel"] p {{
            color: #FFFFFF !important;
            font-weight: 600 !important;
            font-size: 16px !important;
        }}
        
        /* HEADERS: JC YELLOW */
        h1, h2, h3, h4, .welcome-text {{
            color: #f1c40f !important;
            font-weight: 800 !important;
            text-align: center;
        }}

        .logo-wrapper {{ 
            display: flex; 
            justify-content: center; 
            padding: 10px 0; 
        }}
        
        .logo-img {{ 
            max-width: 180px; 
            width: 40%; 
            border-radius: 12px; 
        }}
        
        /* SIDEBAR STYLING */
        [data-testid="stSidebar"] {{ 
            background-color: #041a04 !important; 
            border-right: 5px solid #f1c40f !important;
        }}
        
        /* SIDEBAR TEXT */
        [data-testid="stSidebar"] p, 
        [data-testid="stSidebar"] span, 
        [data-testid="stSidebar"] label {{
            color: #FFFFFF !important;
        }}

        /* TABLE STYLING: 8-COLUMN LAYOUT */
        thead tr th {{
            background-color: #2d3436 !important;
            color: #f1c40f !important;
            font-size: 15px !important;
            white-space: nowrap !important;
            padding: 10px !important;
        }}
        
        tbody tr td {{
            background-color: white !important;
            color: black !important;
            white-space: nowrap !important;
            font-weight: bold !important;
            padding: 10px !important;
        }}

        /* MANAGEMENT DASHBOARD CARDS */
        .readable-card {{
            background-color: rgba(255, 255, 255, 0.95) !important;
            padding: 35px !important;
            border-radius: 15px !important;
            margin-bottom: 25px !important;
            border: 3px solid #f1c40f !important;
        }}
        
        /* Force black text inside cards for high contrast */
        .readable-card p, 
        .readable-card h3, 
        .readable-card label, 
        .readable-card span {{
            color: #000000 !important;
        }}
        
        /* BUTTONS */
        div.stButton > button:first-child {{
            background-color: #f1c40f !important;
            color: #000000 !important;
            font-weight: bold !important;
            border-radius: 10px !important;
            border: 2px solid white !important;
            height: 3em !important;
        }}
        
        /* METRIC STYLING */
        [data-testid="stMetricLabel"] p {{ 
            color: #f1c40f !important; 
            font-size: 18px !important;
        }}
        
        [data-testid="stMetricValue"] {{ 
            color: #000000 !important; 
            font-weight: 900 !important; 
        }}
        </style>
        {logo_html}
        """,
        unsafe_allow_html=True
    )

apply_branding()

# ==========================================
# 3. USER AUTHENTICATION & LOGIN
# ==========================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    # Login form centered on screen
    left_space, login_col, right_space = st.columns([0.2, 0.6, 0.2])
    with login_col:
        st.markdown("<h3 style='text-align: center;'>🔐 Staff Portal Login</h3>", unsafe_allow_html=True)
        work_id = st.text_input("Enter your Work ID to unlock", type="password")
        
        if st.button("Unlock System", use_container_width=True):
            # Verify ID against Supabase 'staff' table
            res = supabase.table("staff").select("*").eq("work_id", work_id).execute()
            if res.data:
                st.session_state.logged_in = True
                st.session_state.user = res.data[0]
                st.rerun()
            else:
                st.error("Access Denied: Invalid Work ID. Please see Peter Kimani.")
    st.stop()

# ==========================================
# 4. SIDEBAR NAVIGATION
# ==========================================
user_profile = st.session_state.user

with st.sidebar:
    st.markdown("<h2 style='text-align: center;'>SYSTEM MENU</h2>", unsafe_allow_html=True)
    st.markdown(f"👤 **Logged in as:** {user_profile['full_name']}")
    st.write("---")
    
    # Navigation Options
    nav_options = ["📝 Record Shift"]
    
    # Check for Owner/Manager permissions
    if user_profile['full_name'] == "Peter Kimani" or user_profile.get('role') == 'manager':
        nav_options.append("👨‍💼 Management")
    
    current_page = st.radio("SELECT PAGE:", nav_options, index=0)
    
    st.write("---")
    # Logout Logic
    if st.button("🚪 Logout System", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()

# ==========================================
# 5. PAGE: RECORD SHIFT
# ==========================================
if current_page == "📝 Record Shift":
    st.markdown(f'<div class="welcome-text">Welcome, {user_profile["full_name"]}</div>', unsafe_allow_html=True)
    
    # FETCH LAST CLOSING READING FROM DATABASE
    last_record = supabase.table("shift_logs").select("pump_reading_end").order("created_at", desc=True).limit(1).execute()
    
    if last_record.data:
        opening_val = float(last_record.data[0]["pump_reading_end"])
    else:
        opening_val = 0.0

    # Display Station Status Card
    st.markdown(
        f'<div style="background: rgba(255,255,255,0.1); border-left: 1px solid #f1c40f; padding: 20px; border-radius: 8px; margin-bottom: 20px;">'
        f'<span style="color: #f1c40f; font-weight: bold; letter-spacing: 2px;">STATION STATUS</span><br>'
        f'<span style="color: white; font-size: 28px; font-weight: 900;">Opening Reading: {opening_val:,.1f} L</span></div>', 
        unsafe_allow_html=True
    )

    # Input Fields for Readings
    col_left, col_right = st.columns(2)
    with col_left:
        closing_reading = st.number_input("Enter Current Closing Reading (L)", value=opening_val, step=0.1)
    with col_right:
        price_ltr = st.number_input("Fuel Price per Liter (KES)", value=189.0, step=0.1)

    # Real-time Calculations
    vol_sold = opening_val - closing_reading
    expected_revenue = vol_sold * price_ltr
    
    # Highlight Expected Revenue
    st.markdown(
        f'<div style="background: #f1c40f; color: black; padding: 30px; border-radius: 15px; text-align: center; font-weight: 900; font-size: 30px; margin: 20px 0; border: 3px solid #ffffff;">'
        f'TOTAL SALES: KES {max(0.0, expected_revenue):,.2f}</div>', 
        unsafe_allow_html=True
    )

    # Payment Inputs
    cash_col, mpesa_col = st.columns(2)
    with cash_col:
        cash_input = st.number_input("Total Cash on Hand (KES)", min_value=0.0)
    with mpesa_col:
        mpesa_input = st.number_input("Total M-Pesa / Till (KES)", min_value=0.0)

    # Calculate Discrepancy
    total_found = cash_input + mpesa_input
    shift_diff = total_found - expected_revenue

    # Submit Button
    if st.button("VERIFY & SUBMIT SHIFT DATA", use_container_width=True):
        if closing_reading > opening_val:
            st.error("🚨 ERROR: The meter reading cannot go backwards. Please re-check the pump.")
        else:
            with st.spinner("Syncing with Supabase Cloud..."):
                supabase.table("shift_logs").insert({
                    "attendant_name": user_profile['full_name'], 
                    "pump_reading_start": opening_val,
                    "pump_reading_end": closing_reading, 
                    "liters_sold": vol_sold,
                    "price_per_ltr": price_ltr, 
                    "total_sales": expected_revenue,
                    "cash": cash_input, 
                    "till": mpesa_input, 
                    "difference": shift_diff
                }).execute()
                st.success("✅ Shift Successfully Recorded!")
                st.rerun()

# ==========================================
# 6. PAGE: MANAGEMENT
# ==========================================
elif current_page == "👨‍💼 Management":
    st.markdown('<div class="welcome-text">Owner Management Portal</div>', unsafe_allow_html=True)
    
    # Tabs for Data and Staff
    logs_tab, team_tab = st.tabs(["📊 Business Performance", "👥 Staff Management"])
    
    with logs_tab:
        st.markdown('<div class="readable-card">', unsafe_allow_html=True)
        st.markdown("### Business Summary")
        
        # Fetch all logs
        logs_query = supabase.table("shift_logs").select("*").order("created_at", desc=True).execute()
        
        if logs_query.data:
            df_logs = pd.DataFrame(logs_query.data)
            
            # --- CRASH PROTECTION: Missing Column Safety ---
            safety_check = ['total_sales', 'liters_sold', 'difference', 'price_per_ltr', 'cash', 'till']
            for col_name in safety_check:
                if col_name not in df_logs.columns: 
                    df_logs[col_name] = 0.0

            # Metric Display
            met1, met2, met3 = st.columns(3)
            met1.metric("Total Liters Sold", f"{df_logs['liters_sold'].sum():,.1f} L")
            met2.metric("Total Revenue", f"KES {df_logs['total_sales'].sum():,.2f}")
            met3.metric("Net Variance", f"KES {df_logs['difference'].sum():,.2f}")
            
            st.write("---")
            st.markdown("### All Shift Records (Detailed)")
            
            # Format Date
            df_logs['created_at'] = pd.to_datetime(df_logs['created_at']).dt.strftime('%Y-%m-%d %H:%M')
            
            # Status Function
            def calc_status(val):
                if val < -5: return f"🔴 Short (KES {abs(val):,.0f})"
                if val > 5: return f"🟢 Excess (KES {val:,.0f})"
                return "⚪ Balanced"
            
            df_logs['Shift Status'] = df_logs['difference'].apply(calc_status)
            
            # Final 8-Column DataFrame Selection
            final_view = df_logs[[
                'created_at', 'attendant_name', 'liters_sold', 
                'price_per_ltr', 'total_sales', 'cash', 'till', 'Shift Status'
            ]]
            
            # Rename for display
            final_view.columns = [
                'Date/Time', 'Attendant', 'Liters', 'Rate', 'Sales', 'Cash', 'Till', 'Status'
            ]
            
            st.table(final_view)
        else:
            st.info("The database is currently empty.")
        st.markdown('</div>', unsafe_allow_html=True)

    with team_tab:
        st.markdown('<div class="readable-card">', unsafe_allow_html=True)
        st.markdown("### Active Staff Directory")
        
        staff_query = supabase.table("staff").select("*").execute()
        
        if staff_query.data:
            for person in staff_query.data:
                s_col1, s_col2 = st.columns([0.8, 0.2])
                s_col1.write(f"👤 **{person['full_name']}** (Work ID: {person['work_id']})")
                if s_col2.button("Remove Staff", key=f"delete_{person['id']}", use_container_width=True):
                    supabase.table("staff").delete().eq("id", person['id']).execute()
                    st.rerun()
        
        st.write("---")
        st.markdown("#### ➕ Register New Employee")
        with st.form("staff_registration", clear_on_submit=True):
            staff_name = st.text_input("Full Legal Name")
            staff_id = st.text_input("Assign Unique Work ID")
            
            if st.form_submit_button("Save to Database"):
                if staff_name and staff_id:
                    supabase.table("staff").insert({
                        "full_name": staff_name, 
                        "work_id": staff_id
                    }).execute()
                    st.success(f"Successfully added {staff_name}")
                    st.rerun()
                else:
                    st.warning("Please fill in both fields.")
        st.markdown('</div>', unsafe_allow_html=True)

# THE END OF THE CODE
