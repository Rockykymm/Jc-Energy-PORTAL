import streamlit as st
from supabase import create_client
import pandas as pd
from PIL import Image
import io
import base64

# 1. DATABASE CONNECTION
# Ensure these match your Secrets in Streamlit Cloud
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

# 2. PAGE CONFIGURATION
st.set_page_config(
    page_title="JC Energy Secure Portal",
    page_icon="⛽",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 3. HIGH-DETAIL BRANDING & RESPONSIVE CSS
def apply_branding():
    try:
        # Load the local file to prevent web-link breakage
        img = Image.open("Gemini_Generated_Image_ykd8mjykd8mjykd8.jpg")
        
        # Convert to high-quality Base64 to maintain detail on all screens
        buffered = io.BytesIO()
        img.save(buffered, format="JPEG", quality=100)
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        st.markdown(
            f"""
            <style>
            /* Main Background */
            .stApp {{
                background-color: #072a07;
                color: white;
            }}
            
            /* Sharp, Responsive Logo */
            .logo-wrapper {{
                display: flex;
                justify-content: center;
                padding: 20px 0;
            }}
            .logo-img {{
                max-width: 250px;
                width: 60%;
                height: auto;
                border-radius: 15px;
                box-shadow: 0px 8px 20px rgba(0,0,0,0.4);
                image-rendering: -webkit-optimize-contrast;
            }}

            /* Global Text Styling */
            h1, h2, h3, h4, p, label, .stMarkdown {{ 
                color: white !important; 
            }}

            /* Mobile-Friendly Input Boxes */
            .stNumberInput input, .stTextInput input {{
                background-color: white !important;
                color: black !important;
                height: 50px !important;
                font-size: 18px !important;
                border-radius: 8px !important;
            }}

            /* Big Green Submit Button for Android */
            div.stButton > button {{
                background-color: #2e7d32 !important;
                color: white !important;
                height: 55px !important;
                width: 100% !important;
                font-weight: bold !important;
                font-size: 18px !important;
                border-radius: 12px !important;
                border: 2px solid #388e3c !important;
                margin-top: 10px;
            }}

            /* Clean up the UI */
            header {{visibility: hidden;}}
            footer {{visibility: hidden;}}
            [data-testid="stHeader"] {{background: rgba(0,0,0,0);}}
            </style>
            
            <div class="logo-wrapper">
                <img src="data:image/jpeg;base64,{img_str}" class="logo-img">
            </div>
            """,
            unsafe_allow_html=True
        )
    except:
        st.markdown("<h1 style='text-align: center; color: white;'>JC ENERGY</h1>", unsafe_allow_html=True)

apply_branding()

# 4. LOGIN SYSTEM
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, col, _ = st.columns([0.1, 0.8, 0.1])
    with col:
        st.markdown("<h3 style='text-align: center;'>🔐 Staff Login</h3>", unsafe_allow_html=True)
        work_id = st.text_input("Enter Work ID", type="password", placeholder="e.g. 001")
        if st.button("Open Portal"):
            res = supabase.table("staff").select("*").eq("work_id", work_id).execute()
            if res.data:
                st.session_state.logged_in = True
                st.session_state.user = res.data[0]
                st.rerun()
            else:
                st.error("Invalid ID. Check with manager.")
    st.stop()

# 5. MAIN APP INTERFACE
user = st.session_state.user
tabs = st.tabs(["📝 Record Shift", "📊 History"])

with tabs[0]:
    st.markdown(f"**Current Attendant:** {user['full_name']}")
    
    # Auto-fetch the opening reading from the last entry
    res_last = supabase.table("shift_logs").select("pump_reading_end").order("created_at", desc=True).limit(1).execute()
    start_val = float(res_last.data[0]["pump_reading_end"]) if res_last.data else 0.0
    
    st.info(f"Opening Pump Reading: **{start_val:,} L**")
    
    with st.form("shift_form", clear_on_submit=True):
        st.markdown("### Enter Shift Totals")
        end_reading = st.number_input("Closing Pump Reading (Liters)", value=start_val, step=0.1)
        cash = st.number_input("Total Cash Collected (KES)", min_value=0.0, step=1.0)
        mpesa = st.number_input("Total M-Pesa Collected (KES)", min_value=0.0, step=1.0)
        
        if st.form_submit_button("Submit Shift & Log Out"):
            liters = end_reading - start_val
            if liters < 0:
                st.error("Error: Closing reading cannot be less than opening.")
            else:
                total_money = cash + mpesa
                supabase.table("shift_logs").insert({
                    "attendant_name": user['full_name'],
                    "pump_reading_start": start_val,
                    "pump_reading_end": end_reading,
                    "liters_sold": liters,
                    "total_collected": total_money
                }).execute()
                
                st.success("Data Saved! Logging out...")
                st.session_state.logged_in = False
                st.rerun()

with tabs[1]:
    st.markdown("### Your Recent Shifts")
    history = supabase.table("shift_logs").select("*").eq("attendant_name", user['full_name']).order("created_at", desc=True).limit(5).execute()
    if history.data:
        df = pd.DataFrame(history.data)
        st.dataframe(df[['created_at', 'liters_sold', 'total_collected']])
    else:
        st.write("No history found.")
