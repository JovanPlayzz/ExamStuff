import streamlit as st
import pandas as pd
import io
import os

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

# --- UI SETUP ---
st.set_page_config(page_title="Logic Processor", layout="centered")
st.title("📱 Logic Processor")

# Initialize Session State
if 's_num' not in st.session_state:
    st.session_state.s_num = 1

input_file = 'variables.xlsx'

if not os.path.exists(input_file):
    st.error("❌ File not found in GitHub!")
else:
    # 1. Main Inputs
    section_choice = st.selectbox("Section", ["Core", "Ryzen"])
    
    # We use value=st.session_state.s_num to keep it synced
    student_num = st.number_input("Student Number", min_value=1, step=1, value=st.session_state.s_num)

    # --- CLEAN INTERACTIVE TABLE ---
    with st.expander("🔍 Find my number", expanded=False):
        search_query = st.text_input("Type name...", placeholder="Search...", key="search_box").lower()
        
        lookup_df = pd.read_excel(input_file, sheet_name=section_choice, header=None, engine='openpyxl')
        lookup_df.columns = ["ID", "Name"]
        
        if search_query:
            filtered = lookup_df[lookup_df['Name'].str.lower().str.contains(search_query)]
            
            if not filtered.empty:
                # Header for our "fake" table
                st.markdown("**ID | Name**")
                for _, row in filtered.head(8).iterrows():
                    c1, c2 = st.columns([4, 1])
                    c1.write(f"`{row['ID']}` {row['Name']}")
                    # When clicked, update state and force refresh
                    if c2.button("Pick", key=f"p_{row['ID']}"):
                        st.session_state.s_num = int(row['ID'])
                        st.rerun()
            else:
                st.caption("No results found.")
        else:
            st.caption("Enter a name to search.")

    logic_choice = st.radio("Logic", ["Java", ".NET"], horizontal=True)

    try:
        # 2. Name Lookup
        names_df = pd.read_excel(input_file, sheet_name=section_choice, header=None, engine='openpyxl')
        student_row = names_df[names_df[0] == student_num]
        
        if not student_row.empty:
            student_name = str(student_row.iloc[0, 1]).strip()
            st.success(f"✅ **{student_name}**")

            # 3. Calculation Logic
            lower = ((student_num - 1) // 10) * 10 + 1
            data_tab = f"Student {lower} to {lower + 9}"
            full_df = pd.read_excel(input_file, sheet_name=data_tab, header=None, engine='openpyxl')
            
            pos_in_tab = (student_num - 1) % 10 
            start_col = (pos_in_tab * 6) + 1
            
            all_results = []
            for i in range(len(full_df)):
                if len(all_results) >= 100: break
                raw_row = full_df.iloc[i, start_col:start_col+5].tolist()
                try:
                    nums = [int(float(str(v).strip())) for v in raw_row]
                    all_results.append(process_java(nums) if logic_choice == "Java" else process_net(nums))
                except: continue

            final_df = pd.DataFrame(all_results, columns=['Output 1', 'Output 2', 'Output 3']).astype(int)
            final_df.index = final_df.index + 1

            # 4. Download Button
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                final_df.to_excel(writer, index_label='#', sheet_name='Results')

            st.download_button(
                label=f"📥 Download Result",
                data=output.getvalue(),
                file_name=f"[{student_num}] {student_name}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
                type="primary"
            )

            # 5. Result Display
            st.dataframe(final_df, height=350, use_container_width=True)

    except Exception:
        st.info("Searching for student data...")
