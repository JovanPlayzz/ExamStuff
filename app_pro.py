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

# Initialize Admin Mode in Session State so it persists
if 'admin_mode' not in st.session_state:
    st.session_state.admin_mode = "None"

def generate_key(student_id, salt):
    combined = f"{student_id}{salt}"
    hash_hex = hashlib.sha256(combined.encode()).hexdigest()
    return str(int(hash_hex[:8], 16))[:6]

# --- 2. LOGIC FUNCTIONS ---
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

def select_id(new_id):
    st.session_state.s_num = int(new_id)

# --- 3. UI SETUP ---
st.set_page_config(page_title="Answerinator PRO", layout="centered")
st.title("🚀 Java & Net Answerinator [PRO]")

st.error("**⚠️ EXTREME DISCLAIMER:** IF THE ANSWERS YOU SUBMIT IN THE EXAM ARE WRONG, DO NOT BLAME THE ONE WHO MADE THIS. USE AT YOUR OWN RISK.", icon="🚫")

with st.expander("Message for Sir Pids"):
    st.info("Sir, I noticed classmates using unreliable AI, so I built this to ensure the logic follows what you taught us. It's a coding experiment! Please have mercy.", icon="👨‍🏫")

st.divider()

if 's_num' not in st.session_state: st.session_state.s_num = 1

input_file = 'variables.xlsx'
if not os.path.exists(input_file):
    st.error("❌ File 'variables.xlsx' not found!")
else:
    # --- INPUTS ---
    col1, col2 = st.columns(2)
    with col1: section = st.selectbox("Section", ["Core", "Ryzen"])
    with col2: s_num = st.number_input("Student Number", min_value=1, step=1, key="s_num")

    # SEARCH
    with st.expander("🔍 Find my number"):
        ldf = pd.read_excel(input_file, sheet_name=section, header=None)
        ldf.columns = ["ID", "Name"]
        query = st.text_input("Type name...", key="search_box").lower()
        if query:
            match = ldf[ldf['Name'].astype(str).str.lower().str.contains(query, na=False)]
            for _, row in match.head(5).iterrows():
                c1, c2 = st.columns([3, 1])
                c1.write(f"`{int(row['ID'])}` {row['Name']}")
                c2.button("Pick", key=f"sel_{row['ID']}", on_click=select_id, args=(row['ID'],), use_container_width=True)

    # NAME DISPLAY
    try:
        names_df = pd.read_excel(input_file, sheet_name=section, header=None)
        student_match = names_df[pd.to_numeric(names_df[0], errors='coerce') == s_num]
        if not student_match.empty:
            student_name = str(student_match.iloc[0, 1]).strip()
            st.success(f"📍 **Selected:** Student #{s_num} - {student_name}")
    except: pass

    logic = st.radio("Logic Mode", ["Java", ".NET"], horizontal=True)

    # --- 4. ACCESS CONTROL ---
    st.divider()
    st.markdown(f"### 💸 Premium Access\n| Option | Price |\n| :--- | :--- |\n| **View Key** | ₱200 |\n| **Full Key** | ₱250 |\n\n**GCash:** `{GCASH_NUMBER}`", unsafe_allow_html=True)
    st.link_button("📤 Send Receipt to Facebook", FB_LINK, use_container_width=True)
    
    user_key = st.text_input(f"Enter Key for Student #{s_num}:", type="password").strip()
    
    # GOD MODE CHECK
    correct_view_key = generate_key(s_num, SALT_VIEW)
    correct_dl_key = generate_key(s_num, SALT_DL)
    
    is_view = (user_key == correct_view_key) or (st.session_state.admin_mode in ["View", "Full"])
    is_dl = (user_key == correct_dl_key) or (st.session_state.admin_mode == "Full")

    if is_view or is_dl:
        if st.session_state.admin_mode != "None":
            st.warning(f"🛠️ ADMIN OVERRIDE: {st.session_state.admin_mode} Mode Active")
        
        try:
            lower = ((int(s_num) - 1) // 10) * 10 + 1
            df = pd.read_excel(input_file, sheet_name=f"Student {lower} to {lower + 9}", header=None)
            start_col = ((int(s_num) - 1) % 10 * 6) + 1
            raw_vars = df.iloc[0:101, start_col:start_col+5]
            
            results = []
            inputs_used = []
            
            for _, r in raw_vars.iterrows():
                try:
                    clean_r = [int(float(v)) for v in r.values if pd.notna(v)]
                    if len(clean_r) == 5:
                        inputs_used.append(clean_r)
                        results.append(process_java(clean_r) if logic == "Java" else process_net(clean_r))
                except: continue
                if len(results) >= 100: break
            
            if results:
                res_df = pd.DataFrame(results, columns=['Output 1', 'Output 2', 'Output 3'])
                res_df.index = range(1, len(res_df) + 1)
                
                if is_dl:
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                        res_df.to_excel(writer, index=True, header=True, sheet_name='Results')
                    st.download_button("📥 Download Excel", output.getvalue(), file_name=f"Result_{s_num}.xlsx", use_container_width=True, type="primary")
                else:
                    st.button("📥 Download Excel (Locked)", disabled=True, use_container_width=True)

                st.table(res_df.astype(int))
                
                with st.expander("📚 View Variables Used"):
                    in_df = pd.DataFrame(inputs_used, columns=['V1', 'V2', 'V3', 'V4', 'V5'])
                    in_df.index = range(1, len(in_df) + 1)
                    st.dataframe(in_df, use_container_width=True)
        except: st.error("Data error.")

# --- 5. ADMIN PANEL ---
st.write("---")
with st.expander("🛠️ Admin Controls"):
    pwd = st.text_input("Admin Password", type="password", key="admin_pwd_input")
    if pwd == MASTER_PASS:
        choice = st.radio("Set My Access Level:", ["None", "View", "Full"], 
                          index=0 if st.session_state.admin_mode=="None" else (1 if st.session_state.admin_mode=="View" else 2))
        if st.button("Apply Admin Mode"):
            st.session_state.admin_mode = choice
            st.rerun()
        
        st.divider()
        st.write(f"**Customer Keys for Student #{s_num}:**")
        st.code(f"View: {correct_view_key}\nFull: {correct_dl_key}")
    elif pwd != "":
        st.error("Wrong Password")
