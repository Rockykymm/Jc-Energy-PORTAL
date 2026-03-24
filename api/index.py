import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from supabase import create_client
from datetime import datetime

app = Flask(__name__)
# Ensures the frontend can talk to the backend without security blocks
CORS(app)

# --- HELPER: CONNECTS TO DB ONLY WHEN NEEDED ---
def get_supabase():
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    if not url or not key:
        return None
    return create_client(url, key)

# --- 1. STATUS ROUTE (Fixes the "Initializing" screen) ---
@app.route('/api/status', methods=['GET'])
def get_status():
    return jsonify({"status": "online", "message": "Backend Connected"}), 200

# --- 2. YOUR ORIGINAL LOGIC: FETCH READINGS ---
@app.route('/api/last-reading', methods=['GET'])
def get_last_reading():
    try:
        sb = get_supabase()
        if not sb:
            return jsonify({"error": "DB Keys Missing"}), 500
        
        # This is your exact table and query logic
        res = sb.table("shift_logs").select("pump_reading_end, meter_reading_end").order("created_at", desc=True).limit(1).execute()
        
        if res.data:
            return jsonify(res.data[0])
        return jsonify({"pump_reading_end": 0.0, "meter_reading_end": 0.0})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- 3. YOUR ORIGINAL LOGIC: FINALIZE SHIFT ---
@app.route('/api/finalize-shift', methods=['POST'])
def finalize_shift():
    try:
        sb = get_supabase()
        if not sb:
            return jsonify({"error": "DB Keys Missing"}), 500
            
        data = request.json
        # This is your exact insert logic
        res = sb.table("shift_logs").insert(data).execute()
        return jsonify({"message": "Shift finalized successfully", "data": res.data}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Required for Vercel to find the app
app = app