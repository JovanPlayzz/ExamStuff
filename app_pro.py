import streamlit as st
import pandas as pd
import io
import os
import hashlib

# --- 1. THE SECURITY VAULT ---
try:
    SALT_VIEW = st.secrets["SALT_VIEW"]
    SALT_DL = st.secrets["SALT_DOWNLOAD"]
    GCASH_NUMBER = st.secrets["GCASH_NUMBER"]
except:
    st.error("Secrets missing! Set SALT_VIEW and SALT_DOWNLOAD in Dashboard.")
    st.stop()

def generate_key(student_id, salt):
    """Generates a unique 6-digit hash based on the specific salt provided."""
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
st.markdown("*Dont know the answers? just use this! it answers for you because your stupid.*")
st.divider()

if 's_num' not in st.session_state: st.session_state.s_num = 1

input_file = 'variables.xlsx'
if not os.path.exists(input_file):
    st.error("❌ File 'variables.xlsx' not found!")
else:
    # Inputs & Search
    col1, col2 = st.columns(2)
    with col1: section = st.selectbox("Section", ["Core", "Ryzen"])
    with col2: s_num = st.number_input("Student Number", min_value=1, step=1, key="s_num")

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

    logic = st.radio("Logic", ["Java", ".NET"], horizontal=True)

    # --- 4. DOUBLE HASH PAYWALL ---
    st.divider()
    st.subheader("💰 Unlock Answers")
    st.info(f"🔹 **₱200**: View Key\n🔹 **₱250**: Download Key\n\nGCash: **{GCASH_NUMBER}**")
    
    user_key = st.text_input(f"Enter Key for Student #{s_num}:", type="password").strip()
    
    # Calculate both possible correct hashes
    correct_view_key = generate_key(s_num, SALT_VIEW)
    correct_dl_key = generate_key(s_num, SALT_DL)

    # Access Logic
    is_view = (user_key == correct_view_key)
    is_dl = (user_key == correct_dl_key)

    if is_view or is_dl:
        st.success(f"🔓 Access Granted!")
        try:
            # Data Processing
            names_df = pd.read_excel(input_file, sheet_name=section, header=None)
            student_match = names_df[pd.to_numeric(names_df[0], errors='coerce') == s_num]
            if not student_match.empty:
                student_name = str(student_match.iloc[0, 1]).strip()
                lower = ((int(s_num) - 1) // 10) * 10 + 1
                df = pd.read_excel(input_file, sheet_name=f"Student {lower} to {lower + 9}", header=None)
                start_col = ((int(s_num) - 1) % 10 * 6) + 1
                raw_vars = df.iloc[0:101, start_col:start_col+5]
                
                results = []
                for _, r in raw_vars.iterrows():
                    clean_r = [int(float(v)) for v in r.values if pd.notna(v)]
                    if len(clean_r) == 5:
                        results.append(process_java(clean_r) if logic == "Java" else process_net(clean_r))
                    if len(results) >= 100: break
                
                if results:
                    # RENDER DOWNLOAD (Only for DL Key)
                    if is_dl:
                        file_label = f"{s_num}: {student_name}-{'Java' if logic == 'Java' else 'Net'}.xlsx"
                        output = io.BytesIO()
                        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                            pd.DataFrame(results).to_excel(writer, index=False, header=False, sheet_name='Results')
                        st.download_button("📥 Download Excel", output.getvalue(), file_name=file_label, use_container_width=True, type="primary")
                    else:
                        st.warning("💡 View-Only. Send ₱50 more for the Download Key.")

                    # RENDER TABLE (For both)
                    st.table(pd.DataFrame(results, columns=['Output 1', 'Output 2', 'Output 3']).astype(int))
        except: st.error("Data error.")
    elif user_key != "":
        st.error("❌ Invalid Key.")
