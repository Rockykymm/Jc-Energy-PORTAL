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
# --- PAGE 1: RECORD SHIFT ---
if choice == "📝 Record Shift":
    st.markdown(f'<div class="welcome-text">Welcome, {user["full_name"]}</div>', unsafe_allow_html=True)
    
    # 1. FETCH ALL DATA FIRST (To prevent NameErrors)
    # We fetch the last 20 records to check for today's dipstick status
    res_last = supabase.table("shift_logs").select("*").order("created_at", desc=True).limit(20).execute()
    
    # Define start values from history or default to 0.0 if the table is empty
    prev_tank_end = float(res_last.data[0]["pump_reading_end"]) if res_last.data else 0.0
    prev_mtr_end = float(res_last.data[0]["meter_reading_end"]) if res_last.data else 0.0

    # 2. CHECK 6 AM DIPSTICK STATUS
    # Accurate cold-fuel measurements only happen once a day at 6 AM
    today_str = datetime.now().strftime('%Y-%m-%d')
    # Filter through the fetched records for any entry from today
    tank_entries_today = [d for d in res_last.data if pd.to_datetime(d['created_at']).strftime('%Y-%m-%d') == today_str]
    tank_already_done = len(tank_entries_today) > 0

    # 3. TANK SECTION (Dipstick logic)
    # Becomes unresponsive/locked after the first entry of the day
    with st.expander("📊 DAILY TANK DIPSTICK (6:00 AM ONLY)", expanded=not tank_already_done):
        if tank_already_done:
            st.success("✅ Today's 6 AM Dipstick reading is already recorded.")
            # Lock the values to the first dipstick entry of the day
            tank_start = float(tank_entries_today[-1]["pump_reading_start"])
            tank_end = float(tank_entries_today[-1]["pump_reading_end"])
        else:
            st.warning("🌅 Please enter the 6 AM cold-fuel dipstick readings.")
            col_t1, col_t2 = st.columns(2)
            tank_start = col_t1.number_input("Opening Tank (L)", value=prev_tank_end)
            tank_end = col_t2.number_input("Closing Tank (L) [Dipstick]", value=prev_tank_end)

    st.write("---")

    # 4. METER SECTION (The primary driver for sales revenue)
    st.subheader("⛽ Shift Meter Readings")
    col_m1, col_m2, col_p = st.columns(3)
    with col_m1:
        # Meter Start is locked to the previous shift's end to prevent fudging numbers
        mtr_start = st.number_input("Meter Start (L)", value=prev_mtr_end, disabled=True)
    with col_m2:
        mtr_end = st.number_input("Meter End (L)", value=prev_mtr_end, step=0.1)
    with col_p:
        price = st.number_input("Price (KES/L)", value=189.0, step=0.1)

    # 5. CALCULATIONS
    liters_sold = mtr_end - mtr_start
    total_sales_expected = liters_sold * price
    
    # Branded Revenue box
    st.markdown(f'<div style="background: #f1c40f; color: black; padding: 20px; border-radius: 10px; text-align: center; font-weight: 800; font-size: 24px; margin: 15px 0; border: 2px solid white;">'
                f'EXPECTED REVENUE: KES {max(0.0, total_sales_expected):,.2f}</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    cash = c1.number_input("Total Cash Collected (KES)", min_value=0.0)
    mpesa = c2.number_input("Total M-Pesa / Till (KES)", min_value=0.0)

    # 6. SUBMISSION SEQUENCE
    if st.button("FINALIZE SHIFT", use_container_width=True):
        actual_total = cash + mpesa
        diff = actual_total - total_sales_expected

        if mtr_end < mtr_start:
            st.error("🚨 Error: Closing meter cannot be lower than opening!")
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
                        "cash": cash, "till": mpesa, "difference": diff
                    }).execute()
                    
                    st.success("✨ SHIFT OVER! Thank you.")
                    time.sleep(2)
                    st.session_state.logged_in = False
                    st.rerun()
                except Exception as e:
                    st.error(f"Database Error: {e}")

    # 2. CHECK 6 AM DIPSTICK STATUS
    today_str = datetime.now().strftime('%Y-%m-%d')
    # Filter history for any tank updates done today
    tank_entries_today = [d for d in res_last.data if pd.to_datetime(d['created_at']).strftime('%Y-%m-%d') == today_str]
    tank_already_done = len(tank_entries_today) > 0

    # 3. TANK SECTION (Locked if already done today)
    with st.expander("📊 DAILY TANK DIPSTICK (6:00 AM ONLY)", expanded=not tank_already_done):
        if tank_already_done:
            st.success("✅ Today's 6 AM Dipstick reading is already recorded.")
            # Ensure tank values are carried over even if locked
            tank_start = float(tank_entries_today[-1]["pump_reading_start"])
            tank_end = float(tank_entries_today[-1]["pump_reading_end"])
        else:
            st.warning("🌅 Please enter the 6 AM cold-fuel dipstick readings.")
            col_t1, col_t2 = st.columns(2)
            tank_start = col_t1.number_input("Opening Tank (L)", value=start_val)
            tank_end = col_t2.number_input("Closing Tank (L) [Dipstick]", value=start_val)

    st.write("---")

    # 4. METER SECTION (Primary Sales Driver)
    st.subheader("⛽ Shift Meter Readings")
    col_m1, col_m2, col_p = st.columns(3)
    with col_m1:
        # Meter Start is locked to the previous shift's end for accuracy
        mtr_start = st.number_input("Meter Start (L)", value=start_mtr, disabled=True)
    with col_m2:
        mtr_end = st.number_input("Meter End (L)", value=start_mtr, step=0.1)
    with col_p:
        price = st.number_input("Price (KES/L)", value=189.0, step=0.1)

    # 5. CALCULATIONS
    liters_sold = mtr_end - mtr_start
    total_sales_expected = liters_sold * price
    
    st.markdown(f'<div style="background: #f1c40f; color: black; padding: 20px; border-radius: 10px; text-align: center; font-weight: 800; font-size: 24px; margin: 15px 0; border: 2px solid white;">'
                f'EXPECTED REVENUE: KES {max(0.0, total_sales_expected):,.2f}</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    cash = c1.number_input("Total Cash Collected (KES)", min_value=0.0)
    mpesa = c2.number_input("Total M-Pesa / Till (KES)", min_value=0.0)

    # 6. SUBMISSION
    if st.button("FINALIZE SHIFT", use_container_width=True):
        actual_total = cash + mpesa
        diff = actual_total - total_sales_expected

        if mtr_end < mtr_start:
            st.error("🚨 Error: Closing meter cannot be lower than opening!")
        else:
            with st.spinner("Recording Shift..."):
                supabase.table("shift_logs").insert({
                    "attendant_name": user['full_name'], 
                    "pump_reading_start": tank_start,
                    "pump_reading_end": tank_end, 
                    "meter_reading_start": mtr_start,
                    "meter_reading_end": mtr_end,
                    "liters_sold": liters_sold,
                    "price_per_ltr": price, 
                    "total_sales": total_sales_expected,
                    "cash": cash, "till": mpesa, "difference": diff
                }).execute()
                
                st.success("✨ SHIFT OVER! Thank you.")
                time.sleep(2)
                st.session_state.logged_in = False
                st.rerun()

    # 2. TANK SECTION (Dipstick - Locked after first entry of the day)
    with st.expander("📊 DAILY TANK DIPSTICK (6:00 AM ONLY)", expanded=not tank_already_done):
        if tank_already_done:
            st.success("✅ Today's 6 AM Dipstick reading is already recorded.")
            tank_start = prev_tank_end
            tank_end = prev_tank_end
        else:
            st.warning("🌅 Please enter the 6 AM cold-fuel dipstick readings.")
            col_t1, col_t2 = st.columns(2)
            tank_start = col_t1.number_input("Opening Tank (L)", value=prev_tank_end)
            tank_end = col_t2.number_input("Closing Tank (L) [Dipstick]", value=prev_tank_end)

    st.write("---")

    # 3. METER SECTION (The primary sales driver)
    st.subheader("⛽ Shift Meter Readings")
    col_m1, col_m2, col_p = st.columns(3)
    with col_m1:
        # Meter Start is always the previous shift's End (Locked for accuracy)
        mtr_start = st.number_input("Meter Start (L)", value=prev_mtr_end, disabled=True)
    with col_m2:
        mtr_end = st.number_input("Meter End (L)", min_value=mtr_start, step=0.1)
    with col_p:
        price = st.number_input("Price (KES/L)", value=189.0, step=0.1)

    # 4. CALCULATIONS
    liters_sold = mtr_end - mtr_start
    total_sales_expected = liters_sold * price
    
    st.markdown(f'<div style="background: #f1c40f; color: black; padding: 20px; border-radius: 10px; text-align: center; font-weight: 800; font-size: 24px; margin: 15px 0; border: 2px solid white;">'
                f'EXPECTED REVENUE: KES {total_sales_expected:,.2f}</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    cash = c1.number_input("Total Cash Collected (KES)", min_value=0.0)
    mpesa = c2.number_input("Total M-Pesa / Till (KES)", min_value=0.0)

    # 5. FINAL SUBMISSION
    if st.button("FINALIZE SHIFT", use_container_width=True):
        actual_total = cash + mpesa
        diff = actual_total - total_sales_expected

        if mtr_end < mtr_start:
            st.error("🚨 Error: Closing meter cannot be lower than opening!")
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
                        "cash": cash, "till": mpesa, "difference": diff
                    }).execute()
                    
                    st.success("✨ SHIFT SUCCESSFULLY RECORDED!")
                    time.sleep(2)
                    st.session_state.logged_in = False
                    st.rerun()
                except Exception as e:
                    st.error(f"Database Error: {e}")
    # 2. INPUT DATA
    col1, col2, col3 = st.columns(3)
    with col1:
        end_reading = st.number_input("Closing Litres (L)", value=start_val, step=0.1)
    with col2:
        end_mtr = st.number_input("Closing Meter (Mtr)", value=start_mtr, step=0.1)
    with col3:
        price_per_liter = st.number_input("Price (KES/L)", value=189.0, step=0.1)

    # 3. CALCULATIONS (Sales based on Meter)
    liters_sold = end_mtr - start_mtr
    total_sales_expected = liters_sold * price_per_liter
    
    st.markdown(f'<div style="background: #f1c40f; color: black; padding: 25px; border-radius: 12px; text-align: center; font-weight: 900; font-size: 28px; margin: 15px 0; border: 2px solid white;">'
                f'EXPECTED REVENUE: KES {max(0.0, total_sales_expected):,.2f}</div>', unsafe_allow_html=True)

    pay_col1, pay_col2 = st.columns(2)
    with pay_col1:
        cash = st.number_input("Total Cash Collected (KES)", min_value=0.0)
    with pay_col2:
        mpesa = st.number_input("Total Till / M-Pesa (KES)", min_value=0.0)

    # 4. SUBMISSION
    if st.button("FINALIZE SHIFT", use_container_width=True):
        actual_collected = cash + mpesa
        diff = actual_collected - total_sales_expected

        if end_mtr < start_mtr:
            st.error("🚨 Error: Closing meter cannot be lower than opening!")
        else:
            with st.spinner("Saving to Cloud..."):
                supabase.table("shift_logs").insert({
                    "attendant_name": user['full_name'], 
                    "pump_reading_start": start_val,
                    "pump_reading_end": end_reading, 
                    "meter_reading_start": start_mtr,
                    "meter_reading_end": end_mtr,
                    "liters_sold": liters_sold,
                    "price_per_ltr": price_per_liter, 
                    "total_sales": total_sales_expected,
                    "cash": cash, 
                    "till": mpesa, 
                    "difference": diff
                }).execute()
                
                st.success("✨ THANK YOU, SHIFT OVER!")
                time.sleep(3)
                st.session_state.logged_in = False
                st.rerun()
# --- PAGE 2: MANAGEMENT (FULL RESTORED VERSION) ---
# --- DAILY PERFORMANCE SUMMARY (MANAGEMENT ONLY) ---
    if user['full_name'] == "Peter Kimani" or user.get('role') == 'manager':
        # Filter for today's data to calculate summaries
        today_date = datetime.now().date()
        df['created_date'] = pd.to_datetime(df['created_at']).dt.date
        today_df = df[df['created_date'] == today_date]

        st.markdown("### 📈 Today's Station Performance")
        m1, m2, m3 = st.columns(3)
        
        total_rev = today_df['total_sales'].sum()
        total_ltrs = today_df['liters_sold'].sum()
        net_bal = today_df['difference'].sum()

        m1.metric("Total Revenue", f"KES {total_rev:,.2f}")
        m2.metric("Total Liters (Meter)", f"{total_ltrs:,.1f} L")
        
        # Shows Green for Excess, Red for Shortage
        bal_color = "normal" if net_bal >= 0 else "inverse"
        m3.metric("Net Balance", f"KES {net_bal:,.2f}", delta=net_bal, delta_color=bal_color)
        
        st.write("---")
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
            
            # SELECT THE 10 SPECIFIC COLUMNS (Including the new Meter data)
            display_df = df[[
                'created_at', 'attendant_name', 
                'pump_reading_start', 'pump_reading_end',
                'meter_reading_start', 'meter_reading_end',
                'liters_sold', 'total_sales', 'cash', 'till', 'Shift Status'
            ]]
            
            # Give the columns clean, readable names for the table
            display_df.columns = [
                'Date/Time', 'Attendant', 
                'Tank Start', 'Tank End',
                'Mtr Start', 'Mtr End',
                'Liters Sold', 'Expected Revenue', 'Cash', 'M-Pesa', 'Status'
            ]
            
            # Display the updated table
            st.table(display_df)
            
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
