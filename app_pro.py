import streamlit as st
import pandas as pd
import io
import os
import hashlib
from PIL import Image

# --- 1. APP CONFIG ---
try:
    # If you have icon.png in your repo, it will use it
    img = Image.open("icon.png")
    st.set_page_config(page_title="Answerinator PRO", page_icon=img, layout="wide")
except:
    st.set_page_config(page_title="Answerinator PRO", page_icon="🚀", layout="wide")

# --- 2. THE "FADE TO WHITE" & NUCLEAR UI ---
st.markdown(
    """
    <style>
        /* 1. Create the Fade effect at the top for iPhone 16 Plus status bar */
        .stApp {
            background: linear-gradient(
                to bottom, 
                white 0%, 
                white 5%, 
                #0e1117 15%, 
                #0e1117 100%
            ) !important;
            color: white;
        }

        /* 2. Nuclear Strike: Kill the 'Built with Streamlit' footer and crown */
        footer {display: none !important; visibility: hidden !important;}
        #MainMenu {display: none !important;}
        header {display: none !important;}
        
        /* 3. Kill the floating Streamlit badge in the corner */
        .viewerBadge_container__1QSob {display: none !important;}
        button[title="View fullscreen"] {display: none !important;}
        
        /* 4. Push content down slightly so it doesn't hide behind the white fade */
        .block-container {
            padding-top: 4.5rem !important;
            padding-bottom: 2rem !important;
            max-width: 100%;
        }

        /* 5. Mobile-optimized buttons */
        .stButton>button {
            width: 100%;
            border-radius: 15px;
            height: 4em;
            background-color: #007bff;
            color: white;
            border: none;
            font-weight: bold;
            font-size: 1.1rem;
            box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.4);
        }

        /* 6. Clean table display */
        div[data-testid="stTable"] {
            background-color: #1a1c24;
            border-radius: 12px;
            padding: 5px;
            overflow-x: auto;
        }

        /* 7. Ensure text is readable against the dark background */
        h1, h2, h3, p, span, label {
            color: white !important;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# --- 3. SECURITY VAULT (From your Secrets) ---
try:
    SALT_VIEW = st.secrets["SALT_VIEW"]
    SALT_DL = st.secrets["SALT_DOWNLOAD"]
    MASTER_PASS = st.secrets["MASTER_PASS"] 
    GCASH_NUMBER = "09924649443" 
    FB_LINK = "https://www.facebook.com/your.profile.name" 
except:
    st.error("⚠️ Secrets missing! Go to Streamlit Dashboard -> Settings -> Secrets.")
    st.stop()

# Session State for Admin Persistence
if 'admin_mode' not in st.session_state: st.session_state.admin_mode = "None"
if 's_num' not in st.session_state: st.session_state.s_num = 1

def generate_key(student_id, salt):
    combined = f"{student_id}{salt}"
    hash_hex = hashlib.sha256(combined.encode()).hexdigest()
    return str(int(hash_hex[:8], 16))[:6]

# --- 4. EXAM LOGIC FUNCTIONS ---
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

# --- 5. MAIN USER INTERFACE ---
st.title("🚀 Answerinator PRO")
st.warning("**⚠️ DISCLAIMER:** Use at your own risk.")

input_file = 'variables.xlsx'
if os.path.exists(input_file):
    col1, col2 = st.columns(2)
    with col1: 
        section = st.selectbox("Section", ["Core", "Ryzen"])
    with col2: 
        # Using session state so 'Pick' button works
        s_num = st.number_input("Student Number", min_value=1, step=1, key="s_num_input", value=st.session_state.s_num)
        st.session_state.s_num = s_num

    with st.expander("🔍 Find my ID Number"):
        try:
            ldf = pd.read_excel(input_file, sheet_name=section, header=None)
            ldf.columns = ["ID", "Name"]
            query = st.text_input("Type your name...", key="search_box").lower()
            if query:
                match = ldf[ldf['Name'].astype(str).str.lower().str.contains(query, na=False)]
                for _, row in match.head(5).iterrows():
                    c1, c2 = st.columns([3, 1])
                    c1.write(f"ID: `{int(row['ID'])}` - {row['Name']}")
                    if c2.button("Select", key=f"sel_{row['ID']}"):
                        select_id(row['ID'])
                        st.rerun()
        except:
            st.info("Search unavailable for this section.")

    logic = st.radio("Select Logic Mode", ["Java", ".NET"], horizontal=True)

    st.divider()
    
    # Key Entry Area
    st.markdown(f"### 💸 Premium Key Required\n**GCash for Key:** `{GCASH_NUMBER}`", unsafe_allow_html=True)
    st.link_button("📤 Message Admin (Send Receipt)", FB_LINK, use_container_width=True)
    
    user_key = st.text_input(f"Enter Key for Student #{st.session_state.s_num}:", type="password").strip()
    
    # Security Validation
    correct_view_key = generate_key(st.session_state.s_num, SALT_VIEW)
    correct_dl_key = generate_key(st.session_state.s_num, SALT_DL)
    
    is_view = (user_key == correct_view_key) or (st.session_state.admin_mode in ["View", "Full"])
    is_dl = (user_key == correct_dl_key) or (st.session_state.admin_mode == "Full")

    if is_view or is_dl:
        try:
            # Load Data
            lower = ((int(st.session_state.s_num) - 1) // 10) * 10 + 1
            df = pd.read_excel(input_file, sheet_name=f"Student {lower} to {lower + 9}", header=None)
            
            # Extract specific student variables
            start_col = ((int(st.session_state.s_num) - 1) % 10 * 6) + 1
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
                    st.download_button("📥 Download Excel File", output.getvalue(), file_name=f"Result_S{st.session_state.s_num}.xlsx", use_container_width=True, type="primary")
                
                st.markdown("### 📊 Generated Answers")
                st.table(res_df.astype(int))
        except Exception as e:
            st.error(f"Data mapping error. Ensure variables.xlsx is formatted correctly.")
    else:
        if user_key != "":
            st.error("❌ Invalid Key for this Student Number.")

# --- 6. ADMIN CONTROL PANEL ---
st.write("---")
with st.expander("🛠️ Admin Master Access"):
    pwd = st.text_input("Master Password", type="password")
    if pwd == MASTER_PASS:
        choice = st.radio("Access Level:", ["None", "View", "Full"], index=0)
        if st.button("Apply Admin Access"):
            st.session_state.admin_mode = choice
            st.success(f"Mode set to: {choice}")
            st.rerun()
        
        st.divider()
        st.write(f"**Keys for Student #{st.session_state.s_num}:**")
        st.code(f"View Key: {correct_view_key}\nFull Key: {correct_dl_key}")
else:
    st.info("App requires variables.xlsx to function.")
