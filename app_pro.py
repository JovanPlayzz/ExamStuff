import streamlit as st
import pandas as pd
import io
import os
import hashlib

# --- 1. CONFIG & UI ---
st.set_page_config(page_title="Answerinator PRO", page_icon="🚀", layout="wide")

st.markdown(
    """
    <style>
        /* 1. TOP & BOTTOM FADE: Blends white bar at top, hides footer at bottom */
        .stApp {
            background: linear-gradient(
                to bottom, 
                #FFFFFF 0%, 
                #0e1117 10%, 
                #0e1117 90%, 
                #FFFFFF 100%
            ) !important;
        }

        /* 2. DELETE BRANDING: Kills footer, crown, and header */
        footer {display: none !important; visibility: hidden !important;}
        #MainMenu {display: none !important;}
        header {display: none !important;}
        .viewerBadge_container__1QSob {display: none !important;}
        
        /* 3. LAYOUT: Center everything and clear the fade zones */
        .block-container {
            padding-top: 5rem !important; 
            padding-bottom: 5rem !important;
        }

        /* 4. TEXT & BUTTONS: Clean white text and pro blue buttons */
        h1, h2, h3, p, span, label { color: white !important; }
        .stButton>button {
            width: 100%;
            border-radius: 12px;
            height: 3.5em;
            background-color: #007bff;
            color: white;
            border: none;
            font-weight: bold;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# --- 2. SECURITY ---
try:
    SALT_VIEW = st.secrets["SALT_VIEW"]
    SALT_DL = st.secrets["SALT_DOWNLOAD"]
    MASTER_PASS = st.secrets["MASTER_PASS"]
    GCASH = "09924649443"
except:
    st.error("Check Secrets!")
    st.stop()

if 'admin_mode' not in st.session_state: st.session_state.admin_mode = "None"
if 's_num' not in st.session_state: st.session_state.s_num = 1

def generate_key(sid, salt):
    return str(int(hashlib.sha256(f"{sid}{salt}".encode()).hexdigest()[:8], 16))[:6]

# --- 3. MAIN APP ---
st.title("🚀 Answerinator PRO")

input_file = 'variables.xlsx'
if os.path.exists(input_file):
    col1, col2 = st.columns(2)
    with col1: sec = st.selectbox("Section", ["Core", "Ryzen"])
    with col2: 
        s_num = st.number_input("ID", min_value=1, step=1, value=st.session_state.s_num)
        st.session_state.s_num = s_num

    logic = st.radio("Logic", ["Java", ".NET"], horizontal=True)
    
    st.divider()
    st.write(f"💸 **GCash:** `{GCASH}`")
    
    user_key = st.text_input("Enter Key:", type="password").strip()
    
    # Validation logic
    vk, dk = generate_key(s_num, SALT_VIEW), generate_key(s_num, SALT_DL)
    is_v = (user_key == vk) or (st.session_state.admin_mode in ["View", "Full"])
    is_d = (user_key == dk) or (st.session_state.admin_mode == "Full")

    if is_v or is_d:
        st.success("Access Granted")
        # Your data processing table goes here...

# --- 4. ADMIN ---
with st.expander("🛠️ Admin"):
    if st.text_input("Pass", type="password") == MASTER_PASS:
        if st.button("Full Access"):
            st.session_state.admin_mode = "Full"
            st.rerun()
        st.code(f"V: {vk} | D: {dk}")
