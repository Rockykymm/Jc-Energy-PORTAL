import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from supabase import create_client

app = Flask(__name__)
# 1. Allow all origins for the /api/ routes to kill CORB/CORS issues
CORS(app, resources={r"/api/*": {"origins": "*"}})

def get_supabase():
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    if not url or not key:
        return None
    try:
        return create_client(url, key)
    except Exception:
        return None

def add_cors_headers(response):
    """Helper to add headers to every response"""
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "*")
    response.headers.add("Access-Control-Allow-Methods", "*")
    return response

@app.route('/api/status', methods=['GET'])
def get_status():
    response = jsonify({"status": "online", "message": "Backend Connected"})
    return add_cors_headers(response), 200

@app.route('/api/last-reading', methods=['GET'])
def get_last_reading():
    try:
        sb = get_supabase()
        if not sb:
            return add_cors_headers(jsonify({"error": "DB Keys Missing"})), 500
        
        res = sb.table("shift_logs").select("pump_reading_end, meter_reading_end").order("created_at", desc=True).limit(1).execute()
        
        if res and hasattr(res, 'data') and res.data:
            response = jsonify(res.data[0])
        else:
            response = jsonify({"pump_reading_end": 0.0, "meter_reading_end": 0.0})
            
        return add_cors_headers(response), 200
    except Exception as e:
        return add_cors_headers(jsonify({"error": str(e)})), 500

@app.route('/api/finalize-shift', methods=['POST'])
def finalize_shift():
    try:
        sb = get_supabase()
        if not sb:
            return add_cors_headers(jsonify({"error": "DB Keys Missing"})), 500
        
        data = request.json
        res = sb.table("shift_logs").insert(data).execute()
        
        if res and hasattr(res, 'data'):
            response = jsonify({"message": "Shift finalized successfully", "data": res.data})
        else:
            response = jsonify({"message": "Shift recorded"})
            
        return add_cors_headers(response), 201
    except Exception as e:
        return add_cors_headers(jsonify({"error": str(e)})), 500