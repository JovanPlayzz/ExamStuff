import st_shredder  # Not a real lib, just keepin' it clean
import streamlit as st
import pandas as pd
import io
import os
import hashlib

# --- 1. SECURITY VAULT ---
try:
    SALT_VIEW = st.secrets["SALT_VIEW"]
    SALT_DL = st.secrets["SALT_DOWNLOAD"]
    MASTER_PASS = st.secrets["MASTER_PASS"] 
    GCASH_NUMBER = "09924649443" 
    FB_LINK = "https://www.facebook.com/your.profile.name" 
except:
    st.error("Secrets missing in Dashboard!")
    st.stop()

# Initialize Admin Overrides so they don't disappear when the page reloads
if 'admin_mode' not in st.session_state:
    st.session_state.admin_mode = "None" # Options: "None", "View", "Full"

def generate_key(student_id, salt):
    combined = f"{student_id}{salt}"
    hash_hex = hashlib.sha256(combined.encode()).hexdigest()
    return str(int(hash_hex[:8], 16))[:6]

# ... (process_java and process_net functions stay the same)

# --- 3. UI SETUP ---
st.set_page_config(page_title="Answerinator PRO", layout="centered")
st.title("🚀 Java & Net Answerinator [PRO]")

# --- DISCLAIMERS ---
st.error("**⚠️ EXTREME DISCLAIMER:** USE AT YOUR OWN RISK.", icon="🚫")
with st.expander("Message for Sir Pids"):
    st.info("Sir, this is a logic-to-code experiment...")

st.divider()

# --- STUDENT INPUT ---
if 's_num' not in st.session_state: st.session_state.s_num = 1
input_file = 'variables.xlsx'

if os.path.exists(input_file):
    col1, col2 = st.columns(2)
    with col1: section = st.selectbox("Section", ["Core", "Ryzen"])
    with col2: s_num = st.number_input("Student Number", min_value=1, step=1, key="s_num")

    # (Search expander and Name display logic goes here...)

    logic = st.radio("Logic Mode", ["Java", ".NET"], horizontal=True)
    st.divider()

    # --- 4. ACCESS CONTROL LOGIC ---
    correct_view_key = generate_key(s_num, SALT_VIEW)
    correct_dl_key = generate_key(s_num, SALT_DL)
    
    # User Input Box
    user_key = st.text_input(f"Enter Key for Student #{s_num}:", type="password").strip()

    # THE MASTER CHECK (Key Match OR Admin God Mode)
    # This is the "God Mode" logic you asked for
    is_view = (user_key == correct_view_key) or (st.session_state.admin_mode in ["View", "Full"])
    is_dl = (user_key == correct_dl_key) or (st.session_state.admin_mode == "Full")

    if is_view or is_dl:
        if st.session_state.admin_mode != "None":
            st.warning(f"🛠️ ADMIN OVERRIDE ACTIVE: {st.session_state.admin_mode} Mode")
        else:
            st.toast("Access Granted!", icon="🔓")

        # --- DATA PROCESSING & TABLE DISPLAY ---
        # (Insert your data processing block here...)
        # When showing buttons:
        if is_dl:
            st.download_button("📥 Download Excel", data="...", file_name="results.xlsx")
        else:
            st.button("📥 Download Excel (Locked)", disabled=True)
            
        # (Table display goes here...)

# --- 5. THE ULTIMATE ADMIN PANEL (Bottom) ---
st.write("---")
with st.expander("🛠️ Internal Admin Controls"):
    pwd = st.text_input("Admin Password", type="password")
    if pwd == MASTER_PASS:
        st.success("Developer Mode Enabled")
        
        # This is where you choose your mode without typing keys
        choice = st.radio(
            "Set My Access Level:",
            ["None", "View Only (₱200)", "Full Access (₱250)"],
            index=0 if st.session_state.admin_mode == "None" else (1 if st.session_state.admin_mode == "View" else 2)
        )
        
        if st.button("Apply Changes"):
            if "None" in choice: st.session_state.admin_mode = "None"
            elif "View" in choice: st.session_state.admin_mode = "View"
            else: st.session_state.admin_mode = "Full"
            st.rerun()

        st.divider()
        st.write(f"**Customer Support:** Key for ID {s_num}")
        st.code(f"₱200: {correct_view_key}\n₱250: {correct_dl_key}")
    elif pwd != "":
        st.error("Incorrect Password")
