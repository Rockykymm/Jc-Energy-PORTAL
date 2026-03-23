import streamlit as st
import requests


BASE_URL = st.secrets["SUPABASE_URL"].rstrip("/")
KEY = st.secrets["SUPABASE_KEY"]

HEADERS = {
    "apikey": KEY,
    "Authorization": f"Bearer {KEY}",
    "Content-Type": "application/json",
}


st.set_page_config(page_title="Station Manager", page_icon="⛽", layout="centered")
st.title("⛽ Shift Handover System")


def get_last_closing() -> float:
    """Fetch last pump_reading_end from Supabase via REST."""
    try:
        url = f"{BASE_URL}/rest/v1/shift_logs"
        params = {
            "select": "pump_reading_end",
            "order": "created_at.desc",
            "limit": 1,
        }
        resp = requests.get(url, headers=HEADERS, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if not data:
            return 0.0
        return float(data[0].get("pump_reading_end", 0.0))
    except Exception:
        return 0.0


def insert_shift(entry: dict) -> bool:
    """Insert a new shift row via REST."""
    try:
        url = f"{BASE_URL}/rest/v1/shift_logs"
        params = {"return": "minimal"}
        resp = requests.post(url, headers=HEADERS, params=params, json=entry, timeout=10)
        resp.raise_for_status()
        return True
    except Exception as e:
        st.error(f"Error saving to Supabase: {e}")
        return False


last_reading = get_last_closing()

with st.container(border=True):
    st.subheader("📝 Record New Shift")
    st.info(f"Last Closing Reading: **{last_reading:,} L**")

    with st.form("entry_form", clear_on_submit=False):
        name = st.text_input("Current Attendant Name")
        current_reading = st.number_input(
            "Current Meter Reading (Liters)",
            value=float(last_reading),
            step=0.01,
            format="%.2f",
        )
        price = st.number_input("Price per Liter (KES)", value=189.0, step=0.1)

        st.divider()
        cash = st.number_input("Physical Cash Handed Over (KES)", min_value=0.0, step=1.0)
        till = st.number_input("M-Pesa / Till Total (KES)", min_value=0.0, step=1.0)

        if st.form_submit_button("Submit & Verify Shift"):
            if not name.strip():
                st.error("Please enter the attendant name.")
                st.stop()

            liters_sold = float(current_reading) - float(last_reading)
            expected_total = liters_sold * float(price)
            actual_total = float(cash) + float(till)
            difference = actual_total - expected_total

            entry = {
                "attendant_name": name.strip(),
                "pump_reading_start": float(last_reading),
                "pump_reading_end": float(current_reading),
                "cash_at_hand": float(cash),
                "till_amount": float(till),
                "fuel_price": float(price),
            }

            if insert_shift(entry):
                st.success("✅ Shift successfully logged to the cloud!")

            c1, c2, c3 = st.columns(3)
            c1.metric("Liters Sold", f"{liters_sold:.2f}L")
            c2.metric("Expected KES", f"{expected_total:,.0f}")
            c3.metric("Actual KES", f"{actual_total:,.0f}")

            if difference < 0:
                st.error(f"⚠️ Shortage: KES {abs(difference):,.2f}")
            elif difference > 0:
                st.warning(f"📈 Extra: KES {difference:,.2f}")
            else:
                st.balloons()
                st.success("🎯 Shift Balanced Perfectly!")

