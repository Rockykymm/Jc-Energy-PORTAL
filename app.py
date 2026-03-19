import streamlit as st
import base64
from PIL import Image
import io

# --- ENHANCED BRANDING (High Detail & Responsive) ---
def apply_branding():
    try:
        # 1. Open the original high-detail file
        img = Image.open("Gemini_Generated_Image_ykd8mjykd8mjykd8.jpg")
        
        # 2. Convert to high-quality Base64 to prevent compression loss
        buffered = io.BytesIO()
        img.save(buffered, format="JPEG", quality=100) # Force 100% quality
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        # 3. Inject high-quality CSS for sharp rendering on Android & PC
        st.markdown(
            f"""
            <style>
            .stApp {{
                background-color: #072a07;
            }}
            
            /* Professional Logo Container */
            .logo-wrapper {{
                display: flex;
                justify-content: center;
                align-items: center;
                padding: 20px 0;
            }}
            
            .logo-img {{
                max-width: 280px; /* Slightly larger for detail */
                width: 70%;       /* Fluid for mobile */
                height: auto;
                border-radius: 12px;
                box-shadow: 0px 4px 15px rgba(0,0,0,0.3);
                image-rendering: -webkit-optimize-contrast; /* Sharpens for mobile */
            }}

            h1, h2, h3, h4, p, label, .stMarkdown {{ 
                color: white !important; 
                text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
            }}

            /* Mobile touch-friendly inputs */
            .stNumberInput input {{
                font-size: 20px !important;
                padding: 10px !important;
            }}
            </style>
            
            <div class="logo-wrapper">
                <img src="data:image/jpeg;base64,{img_str}" class="logo-img">
            </div>
            """,
            unsafe_allow_html=True
        )
    except Exception as e:
        st.markdown("<h1 style='text-align: center; color: white;'>JC ENERGY</h1>", unsafe_allow_html=True)

# Run the branding at the very top
apply_branding()
