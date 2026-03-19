import streamlit as st
from supabase import create_client
import pandas as pd
import requests
import base64

# 1. Database Connection
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

st.set_page_config(page_title="Jc Energy Secure Portal", layout="wide")

# --- BRANDING & LOGO STYLING ---
def apply_branding():
    # This is the direct 'Raw' link to your GitHub image
    github_raw_url = "https://raw.githubusercontent.com/Rockykymm/Jc-Energy-PORTAL/main/Gemini_Generated_Image_ykd8mjykd8mjykd8.jpg"
    
    try:
        # We 'bake' the image into the code so it never fails to load
        response = requests.get(github_raw_url)
        img_base64 = base64.b64encode(response.content).decode()
        logo_html = f"data:image/jpeg;base64,{img_base64}"
    except:
        # Fallback if the internet connection to GitHub blips
        logo_html = github_raw_url

    st.markdown(
        f"""
        <style>
        .logo-container {{
            display: flex;
            justify-content: center;
            padding: 20px;
        }}
        .logo-img {{
            width: 200px;
            border-radius: 15px;
            border: 2px solid rgba(255, 255, 255, 0.2);
        }}
        .stApp {{
            background-color: #072a07;
            background-image: linear-gradient(rgba(7, 42, 7, 0.9), rgba(7, 42, 7, 0.9));
        }}
        h1, h2, h3, h4, p, label, .stMarkdown {{ color: white !important; }}
        [data-testid="stForm"] {{
            background-color: rgba(255, 255, 255, 0.05);
            border-radius: 15px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }}
        </style>
        
        <div class="logo-container">
            <img class="logo-img" src="{logo_html}">
        </div>
        """,
        unsafe_allow_html=True
    )

apply_branding()

# --- LOGIN LOGIC ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("<h3 style='text-align: center;'>🔐 Secure Access</h3>", unsafe_allow_html=True)
        work_id = st.text_input("Enter Work ID", type="password")
        if st.button("Open Portal", use_container_width=True):
            res = supabase.table("staff").select("*").eq("work_id", work_id).execute()
            if res.data:
                st.session_state.logged_in = True
                st.session_state.user = res.data[0]
                st.rerun()
            else:
                st.error("Invalid ID.")
    st.stop()

# --- MAIN PORTAL ---
user = st.session_state.user
tab_names = ["📝 Shift Record"]
if user.get('is_admin'): tab_names.append("📊 Manager Tools")
tabs = st.tabs(tab_names)

with tabs[0]:
    st.markdown(f"### Welcome, {user['full_name']}")
    res_last = supabase.table("shift_logs").select("pump_reading_end").order("created_at", desc=True).limit(1).execute()
    start_reading = float(res_last.data[0]["pump_reading_end"]) if res_last.data else 0.0
    st.info(f"Opening Pump Reading: **{start_reading:,} L**")
    
    with st.form("shift_entry"):
        end_reading = st.number_input("Closing Pump Reading (L)", value=start_reading, step=0.01)
        cash = st.number_input("Total Cash (KES)", min_value=0.0)
        mpesa = st.number_input("Total M-Pesa (KES)", min_value=0.0)
        if st.form_submit_button("Submit & Log Out"):
            liters = end_reading - start_reading
            if liters < 0: st.error("Invalid Reading!")
            else:
                total = cash + mpesa
                supabase.table("shift_logs").insert({
                    "attendant_name": user['full_name'], "pump_reading_start": start_reading,
                    "pump_reading_end": end_reading, "liters_sold": liters,
                    "total_collected": total
                }).execute()
                st.balloons()
                st.session_state.logged_in = False
                st.rerun()
