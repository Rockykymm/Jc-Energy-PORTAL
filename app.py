import streamlit as st
from supabase import create_client
import pandas as pd
from PIL import Image

# 1. Database Connection
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

# Force wide mode but keep content centered for mobile
st.set_page_config(page_title="Jc Energy Portal", layout="wide")

# --- BRANDING & MOBILE OPTIMIZATION ---
def apply_branding():
    try:
        # Loading the image locally is the best way to ensure it shows on Android
        logo = Image.open("Gemini_Generated_Image_ykd8mjykd8mjykd8.jpg")
        
        # This creates a flexible layout: 1 column on mobile, 3 on PC
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.image(logo, use_container_width=True)
    except:
        st.markdown("<h1 style='text-align: center; color: white;'>JC ENERGY</h1>", unsafe_allow_html=True)

    st.markdown(
        """
        <style>
        /* Dark Green Background */
        .stApp {
            background-color: #072a07;
        }
        
        /* Make text white and easy to read on small screens */
        h1, h2, h3, h4, p, label, .stMarkdown { 
            color: white !important; 
            font-family: 'sans-serif';
        }

        /* Adjust input boxes for fat fingers (Android/Touch) */
        .stNumberInput input, .stTextInput input {
            background-color: white !important;
            color: black !important;
            height: 45px !important;
            font-size: 18px !important;
        }

        /* Styling the Submit Button to be big and green */
        div.stButton > button {
            background-color: #2e7d32 !important;
            color: white !important;
            height: 50px !important;
            font-weight: bold !important;
            border-radius: 10px !important;
            border: none !important;
        }
        
        /* Hide the Streamlit header for a cleaner 'App' look */
        header {visibility: hidden;}
        </style>
        """,
        unsafe_allow_html=True
    )

apply_branding()

# --- LOGIN LOGIC ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    # Centered login box for both PC and Mobile
    _, col, _ = st.columns([0.1, 0.8, 0.1])
    with col:
        st.markdown("<h3 style='text-align: center;'>🔐 Staff Login</h3>", unsafe_allow_html=True)
        work_id = st.text_input("Enter Work ID", type="password", placeholder="e.g. 001")
        if st.button("Open Portal", use_container_width=True):
            res = supabase.table("staff").select("*").eq("work_id", work_id).execute()
            if res.data:
                st.session_state.logged_in = True
                st.session_state.user = res.data[0]
                st.rerun()
            else:
                st.error("Invalid ID. Please try again.")
    st.stop()

# --- MAIN PORTAL ---
user = st.session_state.user
tabs = st.tabs(["📝 Record Shift", "📊 History"])

with tabs[0]:
    st.markdown(f"**Attendant:** {user['full_name']}")
    
    # Fetch the last reading
    res_last = supabase.table("shift_logs").select("pump_reading_end").order("created_at", desc=True).limit(1).execute()
    start_val = float(res_last.data[0]["pump_reading_end"]) if res_last.data else 0.0
    
    st.info(f"Opening Reading: {start_val:,} L")
    
    with st.form("shift_form"):
        end_reading = st.number_input("Closing Pump Reading (Liters)", value=start_val)
        cash = st.number_input("Total Cash (KES)", min_value=0.0)
        mpesa = st.number_input("Total M-Pesa (KES)", min_value=0.0)
        
        if st.form_submit_button("Submit Shift & Log Out", use_container_width=True):
            liters = end_reading - start_val
            if liters < 0:
                st.error("Closing reading cannot be less than opening.")
            else:
                supabase.table("shift_logs").insert({
                    "attendant_name": user['full_name'],
                    "pump_reading_start": start_val,
                    "pump_reading_end": end_reading,
                    "liters_sold": liters,
                    "total_collected": cash + mpesa
                }).execute()
                st.success("Shift Logged Successfully!")
                st.session_state.logged_in = False
                st.rerun()
