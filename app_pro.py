import streamlit as st
import pandas as pd
import io
import os
import hashlib

# --- 1. APP CONFIG (MUST BE FIRST) ---
st.set_page_config(
    page_title="Answerinator PRO",
    page_icon="🚀",
    layout="centered"
)

# --- 2. THE ICON & PWA "FORCE" HACK ---
# This block tells iOS Safari: "I am a standalone app, use this icon."
st.markdown(
    """
    <head>
        <meta name="apple-mobile-web-app-capable" content="yes">
        <meta name="apple-mobile-web-app-status-bar-style" content="black">
        <link rel="apple-touch-icon" href="https://i.pinimg.com/originals/1c/4b/0b/1c4b0b07f185ae358ade34c326d60445.jpg">
        <link rel="icon" href="https://i.pinimg.com/originals/1c/4b/0b/1c4b0b07f185ae358ade34c326d60445.jpg">
    </head>
    <style>
        /* Hide UI elements to look like a real app */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .stApp { 
            margin-top: -70px; 
            background-color: #0e1117; 
            color: white; 
        }
        /* Mobile-friendly buttons */
        .stButton>button {
            width: 100%;
            border-radius: 12px;
            height: 3.5em;
            background-color: #007bff;
            color: white;
            border: none;
            font-weight: bold;
        }
        /* Clean table for dark mode */
        table { 
            background-color: #161b22; 
            color: white; 
            border-radius: 10px; 
        }
    </style>
    """, 
    unsafe_allow_html=True
)

# --- 3. SECURITY VAULT ---
try:
    SALT_VIEW = st.secrets["SALT_VIEW"]
    SALT_DL = st.secrets["SALT_DOWNLOAD"]
    MASTER_PASS = st.secrets["MASTER_PASS"] 
    GCASH_NUMBER = "09924649443" 
    FB_LINK = "https://www.facebook.com/your.profile.name" 
except:
    st.error("⚠️ Secrets missing! Go to Streamlit Dashboard -> Settings -> Secrets.")
    st.stop()

if 'admin_mode' not in st.session_state: st.session_state.admin_mode = "None"
if 's_num' not in st.session_state: st.session_state.s_num = 1

def generate_key(student_id, salt):
    combined = f"{student_id}{salt}"
    hash_hex = hashlib.sha256(combined.encode()).hexdigest()
    return str(int(hash_hex[:8], 16))[:6]

# --- 4. EXAM LOGIC ---
def process_java(n):
    arr = [0, 0, 0]
    for x in range(3):
        if (n[2] < x) and (x > n[3]): arr[x] = n[0] + n[4] + x
        elif (x > n[0]) and (n[2] > x): arr[x] = n[1] + n[3] + x
        elif (n[0] < x) or (x > n[2]): arr[x] = n[0] + n[2] + x
        else: arr[x] = n[1] + n[3] + n[4]
    return [arr[2], arr[1], arr[0]]

def process_net(n):
    arr = [0, 0, 0]
    for x in range(2, -1, -1):
        if (n[0] <= x) and (n[4] >= x): arr[x] = n[0] + n[1] + x
        elif (n[1] >= x) and (n[2] >= x): arr[x] = n[2] + n[4] + x
        elif (n[3] >= x) or (n[0] >= x): arr[x] = n[0] + n[3] + x
        else: arr[x] = n[1] + n[4] + x
    return arr

def select_id(new_id): st.session_state.s_num = int(new_id)

# --- 5. MAIN UI ---
st.title("🚀 Java & Net Answerinator")
st.error("**⚠️ EXTREME DISCLAIMER:** USE AT YOUR OWN RISK.", icon="🚫")

with st.expander("Message for Sir Pids"):
    st.info("hi ser HAHAA", icon="👨‍🏫")

st.divider()

input_file = 'variables.xlsx'
if os.path.exists(input_file):
    col1, col2 = st.columns(2)
    with col1: section = st.selectbox("Section", ["Core", "Ryzen"])
    with col2: s_num = st.number_input("Student Number", min_value=1, step=1, key="s_num")

    with st.expander("🔍 Find my ID"):
        ldf = pd.read_excel(input_file, sheet_name=section, header=None)
        ldf.columns = ["ID", "Name"]
        query = st.text_input("Type name...", key="search_box").lower()
        if query:
            match = ldf[ldf['Name'].astype(str).str.lower().str.contains(query, na=False)]
            for _, row in match.head(5).iterrows():
                c1, c2 = st.columns([3, 1])
                c1.write(f"`{int(row['ID'])}` {row['Name']}")
                c2.button("Pick", key=f"sel_{row['ID']}", on_click=select_id, args=(row['ID'],), use_container_width=True)

    logic = st.radio("Logic Mode", ["Java", ".NET"], horizontal=True)

    st.divider()
    st.markdown(f"### 💸 Premium Access\n**GCash:** `{GCASH_NUMBER}`", unsafe_allow_html=True)
    st.link_button("📤 Send Receipt to Facebook", FB_LINK, use_container_width=True)
    
    user_key = st.text_input(f"Enter Key for Student #{s_num}:", type="password").strip()
    
    correct_view_key = generate_key(s_num, SALT_VIEW)
    correct_dl_key = generate_key(s_num, SALT_DL)
    
    is_view = (user_key == correct_view_key) or (st.session_state.admin_mode in ["View", "Full"])
    is_dl = (user_key == correct_dl_key) or (st.session_state.admin_mode == "Full")

    if is_view or is_dl:
        try:
            lower = ((int(s_num) - 1) // 10) * 10 + 1
            df = pd.read_excel(input_file, sheet_name=f"Student {lower} to {lower + 9}", header=None)
            start_col = ((int(s_num) - 1) % 10 * 6) + 1
            raw_vars = df.iloc[0:101, start_col:start_col+5]
            
            results = []
            for _, r in raw_vars.iterrows():
                try:
                    clean_r = [int(float(v)) for v in r.values if pd.notna(v)]
                    if len(clean_r) == 5:
                        results.append(process_java(clean_r) if logic == "Java" else process_net(clean_r))
                except: continue
            
            if results:
                res_df = pd.DataFrame(results, columns=['Out 1', 'Out 2', 'Out 3'])
                res_df.index = range(1, len(res_df) + 1)
                if is_dl:
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                        res_df.to_excel(writer, index=True, header=True, sheet_name='Results')
                    st.download_button("📥 Download Excel", output.getvalue(), file_name=f"Result_{s_num}.xlsx", use_container_width=True, type="primary")
                st.table(res_df.astype(int))
        except: st.error("Data error.")

# --- 6. ADMIN ---
st.write("---")
with st.expander("🛠️ Admin Controls"):
    pwd = st.text_input("Admin Password", type="password")
    if pwd == MASTER_PASS:
        choice = st.radio("Access:", ["None", "View", "Full"])
        if st.button("Set Mode"):
            st.session_state.admin_mode = choice
            st.rerun()
        st.code(f"View: {correct_view_key}\nFull: {correct_dl_key}")
