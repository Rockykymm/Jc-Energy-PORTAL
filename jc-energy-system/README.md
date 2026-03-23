# JC Energy System — Shift Handover (Streamlit)

This folder now contains a **Streamlit** app for the fuel station shift handover system (Supabase-backed).

## Setup

1) Install dependencies:

```powershell
cd "C:\Users\admin\.cursor\projects\jc-energy-system"
py -m pip install -r requirements.txt
```

2) Configure Supabase credentials:

- Create folder `.streamlit`
- Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml`
- Paste your real Supabase anon key

3) Run the app:

```powershell
py -m streamlit run app.py
```

## Notes

- The app reads `SUPABASE_URL` and `SUPABASE_KEY` from Streamlit secrets.
- Your Supabase key should not be committed to a public repository.

