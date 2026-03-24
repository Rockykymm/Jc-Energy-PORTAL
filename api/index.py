import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from supabase import create_client
from datetime import datetime

# Initialize Flask
app = Flask(__name__)
CORS(app)

# 1. DATABASE CONNECTION (Using your Vercel Environment Variables)
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

# Create client safely so it doesn't crash the whole app if keys are missing
supabase = None
if url and key:
    try:
        supabase = create_client(url, key)
    except Exception as e:
        print(f"Supabase Init Error: {e}")

# 2. STATUS ROUTE (The one that fixes the "Initializing" screen)
@app.route('/api/status', methods=['GET'])
def get_status():
    if supabase:
        return jsonify({"status": "online", "message": "Backend Connected"}), 200
    return jsonify({"status": "error", "message": "Supabase Connection Failed"}), 500

# 3. YOUR ORIGINAL LOGIC (DO NOT LOSE THIS)
@app.route('/api/last-reading', methods=['GET'])
def get_last_reading():
    """Fetches the previous shift's end readings from your Supabase table"""
    try:
        if not supabase:
            return jsonify({"error": "No database connection"}), 500
        
        # Using the logic you built previously
        res = supabase.table("shift_logs").select("pump_reading_end, meter_reading_end").order("created_at", desc=True).limit(1).execute()
        
        if res.data:
            return jsonify(res.data[0])
        return jsonify({"pump_reading_end": 0.0, "meter_reading_end": 0.0})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/finalize-shift', methods=['POST'])
def finalize_shift():
    """Handles the shift closing logic you developed"""
    try:
        if not supabase:
            return jsonify({"error": "No database connection"}), 500
            
        data = request.json
        # Your specific shift calculations and Supabase insert logic goes here
        # (Assuming you are passing the form data from React)
        
        res = supabase.table("shift_logs").insert(data).execute()
        return jsonify({"message": "Shift finalized successfully", "data": res.data}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 4. VERCEL REQUIREMENT
# This ensures Vercel's Serverless Function finds the app instance
app = app