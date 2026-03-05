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
        /* 1. TIGHT TOP & BOTTOM FADE: Blends white bar (5%) and hides footer (5%) */
        .stApp {
            background: linear-gradient(
                to bottom, 
                #FFFFFF 0%, 
                #0e1117 5%, 
                #0e1117 95%, 
                #FFFFFF 100%
            ) !important;
        }

        /* 2. HIDE BRANDING: Deletes footer and badge */
        footer {display: none !important; visibility: hidden !important;}
        #MainMenu {display: none !important;}
        header {display: none !important;}
        .viewerBadge_container__1QSob {display: none !important;}
        
        /* 3. COMPACT LAYOUT: Minimal padding to keep it tight */
        .block-container {
            padding-top: 2.5rem !important; 
            padding-bottom: 2.5rem !important;
        }

        /* 4. TEXT & INPUTS: Smaller fonts to save space */
        h1 { font-size: 1.5rem !important; color: white !important; margin-bottom: 0.5rem !important; }
        p, span, label { color: white !important; font-size: 0.9rem !important; }
        
        .stButton>button {
            width: 100%;
            border-radius: 10px;
            height: 2.8em;
            background-color: #007bff;
            color: white;
            font-weight: bold;
            font-size: 0.9rem;
        }

        /* Shrink input spacing */
        div[data-testid="stVerticalBlock"] { gap: 0.5rem !important; }
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
    # Condense Inputs into 3 columns
    c1, c2, c3 = st.columns([1, 1, 1])
    with c1: sec = st.selectbox("Sec", ["Core", "Ryzen"])
    with c2: 
        s_num = st.number_input("ID", min_value=1, step=1, value=st.session_state.s_num)
        st.session_state.s_num = s_num
    with c3: logic = st.selectbox("Logic", ["Java", ".NET"])
    
    st.write(f"💸 **GCash:** `{GCASH}`")
    
    user_key = st.text_input("Key:", type="password").strip()
    
    vk, dk = generate_key(s_num, SALT_VIEW), generate_key(s_num, SALT_DL)
    is_v = (user_key == vk) or (st.session_state.admin_mode in ["View", "Full"])
    is_d = (user_key == dk) or (st.session_state.admin_mode == "Full")

    if is_v or is_d:
        # Mini results table area
        st.success("Access Granted")
        # [Insert your processing code here]

# --- 4. ADMIN (Hidden in small expander) ---
with st.expander("🛠️"):
    if st.text_input("Pass", type="password") == MASTER_PASS:
        if st.button("Unlock"):
            st.session_state.admin_mode = "Full"
            st.rerun()
        st.code(f"V:{vk} | D:{dk}")
