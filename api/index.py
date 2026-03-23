from flask import Flask, jsonify, request
from flask_cors import CORS
from supabase import create_client
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

# 1. DATABASE CONNECTION
# On Vercel, set these in Settings > Environment Variables
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase = create_client(url, key) if url and key else None

@app.route('/api/status', methods=['GET'])
def get_status():
    return jsonify({"status": "online", "message": "Backend Connected"})

@app.route('/api/last-reading', methods=['GET'])
def get_last_reading():
    """Fetches the previous shift's end readings"""
    try:
        res = supabase.table("shift_logs").select("pump_reading_end", "meter_reading_end").order("created_at", desc=True).limit(1).execute()
        if res.data:
            return jsonify(res.data[0])
        return jsonify({"pump_reading_end": 0.0, "meter_reading_end": 0.0})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/finalize-shift', methods=['POST'])
def finalize_shift():
    """Calculates and saves the shift data to Supabase"""
    data = request.json
    try:
        # Core Logic from your Streamlit file
        liters_sold = float(data['end_mtr']) - float(data['start_mtr'])
        total_sales_expected = liters_sold * float(data['price_per_liter'])
        actual_collected = float(data['cash']) + float(data['mpesa'])
        diff = actual_collected - total_sales_expected

        # Database Insert
        response = supabase.table("shift_logs").insert({
            "attendant_name": data['user_name'],
            "pump_reading_start": data['start_val'],
            "pump_reading_end": data['end_reading'],
            "meter_reading_start": data['start_mtr'],
            "meter_reading_end": data['end_mtr'],
            "liters_sold": liters_sold,
            "price_per_ltr": data['price_per_liter'],
            "total_sales": total_sales_expected,
            "cash": data['cash'],
            "till": data['mpesa'],
            "difference": diff
        }).execute()

        return jsonify({"success": True, "message": "SHIFT OVER!"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)