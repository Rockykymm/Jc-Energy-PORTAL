🚀 The Engineering Evolution: From Script to System
The JC Energy Portal began as a Python-based prototype and evolved into a production-ready Full-Stack ERP. This transition represents a significant leap in technical architecture and user experience.

Phase 1: The Python Prototype (Streamlit)
Objective: Fast proof-of-concept to digitize manual paper records.

Tech: Python, Streamlit, Pandas.

Limitation: Synchronous execution (the page reran on every click) and limited UI flexibility for complex station management.

Phase 2: The Modern ERP (React & Supabase)
Objective: A high-performance, real-time dashboard capable of handling multi-staff shifts and secure auditing.

Tech: React (Vite), Supabase (PostgreSQL), Tailwind CSS, Vercel.

Key Upgrades:

State Management: Implemented complex UI states for seamless tab switching (Dipstick → Handover → History).

Relational Database: Migrated from flat files to a structured PostgreSQL schema, enabling deep auditing of staff performance and fuel sales.

Security & Auth: Integrated Supabase Auth to ensure sensitive price settings are only accessible to authorized personnel.

Deployment: Transitioned to a CI/CD workflow via GitHub and Vercel for instant production updates.
