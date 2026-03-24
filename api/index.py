import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from supabase import create_client

app = Flask(__name__)
CORS(app)

def get_supabase():
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    if not url or not key:
        return None
    try:
        return create_client(url, key)
    except Exception:
        return None

@app.route('/api/status', methods=['GET'])
def get_status():
    return jsonify({"status": "online", "message": "Backend Connected"}), 200

@app.route('/api/last-reading', methods=['GET'])
def get_last_reading():
    try:
        sb = get_supabase()
        if not sb:
            return jsonify({"error": "DB Keys Missing"}), 500
        
        # We keep your exact query logic here
        res = sb.table("shift_logs").select("pump_reading_end, meter_reading_end").order("created_at", desc=True).limit(1).execute()
        
        # FIX: We check if 'res' exists and has a '.data' attribute before accessing it
        # This prevents the "AttributeError" seen in your Vercel logs
        if res and hasattr(res, 'data') and res.data:
            return jsonify(res.data[0]), 200
            
        return jsonify({"pump_reading_end": 0.0, "meter_reading_end": 0.0}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/finalize-shift', methods=['POST'])
def finalize_shift():
    try:
        sb = get_supabase()
        if not sb:
            return jsonify({"error": "DB Keys Missing"}), 500
        
        data = request.json
        res = sb.table("shift_logs").insert(data).execute()
        
        # Applying the same safe-check here for the insert response
        if res and hasattr(res, 'data'):
            return jsonify({"message": "Shift finalized successfully", "data": res.data}), 201
        
        return jsonify({"message": "Shift recorded"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
