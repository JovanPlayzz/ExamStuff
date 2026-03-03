import streamlit as st
import pandas as pd
import io
import os
import hashlib
from PIL import Image

# 1. Config must be FIRST
try:
    img = Image.open("icon.png")
    st.set_page_config(page_title="Answerinator PRO", page_icon=img, layout="wide")
except:
    st.set_page_config(page_title="Answerinator PRO", page_icon="🚀", layout="wide")

# 2. Hide Streamlit Branding & Fix Padding
st.markdown(
    """
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;} /* HIDES 'BUILT WITH STREAMLIT' */
        header {visibility: hidden;}
        .stApp {
            background-color: #0e1117;
            color: white;
            margin-top: -80px; /* PUSHES CONTENT TO TOP */
        }
        /* Full width buttons for mobile */
        .stButton>button {
            width: 100%;
            border-radius: 12px;
            height: 3.5em;
            background-color: #007bff;
            color: white;
            font-weight: bold;
            border: none;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# --- REST OF YOUR LOGIC (Security, Java/Net Logic, etc.) ---
# (Keep your generate_key, process_java, etc. as they were)
