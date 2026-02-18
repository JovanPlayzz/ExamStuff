import streamlit as st
import pandas as pd
import io
import os
import streamlit.components.v1 as components

# --- LOGIC FUNCTIONS ---
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

# --- CUSTOM BOTTOM NOTIFICATION LOGIC ---
def show_custom_toast():
    # This injects a hidden HTML element that triggers a bottom-center popup
    components.html(
        """
        <div id="toast" style="
            position: fixed; 
            bottom: 20px; 
            left: 50%; 
            transform: translateX(-50%); 
            background-color: #28a745; 
            color: white; 
            padding: 12px 24px; 
            border-radius: 25px; 
            font-family: sans-serif; 
            z-index: 9999; 
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            animation: slideUp 0.5s, fadeOut 0.5s 2.5s forwards;
            cursor: pointer;
        " onclick="this.style.display='none'">
            ✅ Inputted successfully!
        </div>
        <style>
            @keyframes slideUp { from { bottom: -50px; opacity: 0; } to { bottom: 20px; opacity: 1; } }
            @keyframes fadeOut { from { opacity: 1; } to { opacity: 0; } }
        </style>
        """,
        height=0
    )

def select_id(new_id):
    st.session_state.s_num = int(new_id)
    st.session_state.show_toast = True

# --- UI SETUP ---
st.set_page_config(page_title="Logic Processor", layout="centered")
st.title("📱 Logic Processor")

if 's_num' not in st.session_state: st.session_state.s_num = 1
if 'show_toast' not in st.session_state: st.session_state.show_toast = False

# Trigger the custom toast if the flag is set
if st.session_state.show_toast:
    show_custom_toast()
    st.session_state.show_toast = False

input_file = 'variables.xlsx'

if not os.path.exists(input_file):
    st.error("❌ File 'variables.xlsx' not found!")
else:
    # --- INPUTS ---
    col1, col2 = st.columns(2)
    with col1:
        section = st.selectbox("Section", ["Core", "Ryzen"])
    with col2:
        s_num = st.number_input("Student Number", min_value=1, step=1, key="s_num")

    # --- SEARCH ---
    with st.expander("🔍 Find my number"):
        query = st.text_input("Type name...", placeholder="Search...", key="search_box").lower()
        lookup_df = pd.read_excel(input_file, sheet_name=section, header=None)
        lookup_df.columns = ["ID", "Name"]
        
        if query:
            match = lookup_df[lookup_df['Name'].astype(str).str.lower().str.contains(query, na=False)]
            for _, row in match.head(5).iterrows():
                c1, c2 = st.columns([3, 1])
                c1.write(f"`{row['ID']}` {row['Name']}")
                c2.button("Pick", key=f"sel_{row['ID']}", on_click=select_id, args=(row['ID'],), use_container_width=True)

    logic = st.radio("Logic", ["Java", ".NET"], horizontal=True)

    # --- PROCESSING ---
    try:
        names_df = pd.read_excel(input_file, sheet_name=section, header=None)
        names_df[0] = pd.to_numeric(names_df[0], errors='coerce')
        student_match = names_df[names_df[0] == s_num]
        
        if not student_match.empty:
            student_name = str(student_match.iloc[0, 1]).strip()
            st.success(f"✅ **{student_name}**")

            lower = ((int(s_num) - 1) // 10) * 10 + 1
            data_tab = f"Student {lower} to {lower + 9}"
            df = pd.read_excel(input_file, sheet_name=data_tab, header=None)
            
            start_col = ((int(s_num) - 1) % 10 * 6) + 1
            raw_data = df.iloc[0:100, start_col:start_col+5].values.tolist()
            
            results = [process_java(r) if logic == "Java" else process_net(r) for r in raw_data]

            if results:
                final_df = pd.DataFrame(results, columns=['Output 1', 'Output 2', 'Output 3']).astype(int)
                final_df.index = final_df.index + 1

                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    final_df.to_excel(writer, index_label='#', sheet_name='Results')

                st.download_button(
                    label="📥 Download Excel",
                    data=output.getvalue(),
                    file_name=f"[{s_num}] {student_name}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                    type="primary"
                )
                st.dataframe(final_df, height=350, use_container_width=True)
    except:
        st.info("Searching for data...")
