import streamlit as st
import pandas as pd
import io
import os

# --- LOGIC FUNCTIONS (Java & .NET) ---
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
st.markdown("Automated result generation for Core and Ryzen sections. Select your details below to preview and download results.")
st.divider()

input_file = 'variables.xlsx'

if not os.path.exists(input_file):
    st.error(f"❌ '{input_file}' not found in GitHub!")
else:
    # --- NEW: STUDENT NUMBER LOOKUP EXPANDER ---
    with st.expander("Don't know student number? Click here"):
        tab_core, tab_ryzen = st.tabs(["Core Section", "Ryzen Section"])
        
        with tab_core:
            core_names = pd.read_excel(input_file, sheet_name="Core", header=None, engine='openpyxl')
            core_names.columns = ["ID", "Name"]
            st.dataframe(core_names, hide_index=True, use_container_width=True)
            
        with tab_ryzen:
            ryzen_names = pd.read_excel(input_file, sheet_name="Ryzen", header=None, engine='openpyxl')
            ryzen_names.columns = ["ID", "Name"]
            st.dataframe(ryzen_names, hide_index=True, use_container_width=True)

    # --- MAIN INPUTS ---
    section_choice = st.selectbox("Select Section", ["Core", "Ryzen"])
    student_num = st.number_input("Enter Student Number", min_value=1, value=1)
    logic_choice = st.radio("Select Logic", ["Java", ".NET"], horizontal=True)

    try:
        # 1. Name Lookup
        names_df = pd.read_excel(input_file, sheet_name=section_choice, header=None, engine='openpyxl')
        student_row = names_df[names_df[0] == student_num]
        
        if student_row.empty:
            st.warning(f"Student {student_num} not found in {section_choice}.")
        else:
            student_name = str(student_row.iloc[0, 1]).strip()
            st.success(f"✅ Selected: **{student_name}**")

            # 2. Data Extraction & Full Calculation
            lower = ((student_num - 1) // 10) * 10 + 1
            upper = lower + 9
            data_tab = f"Student {lower} to {upper}"
            
            full_df = pd.read_excel(input_file, sheet_name=data_tab, header=None, engine='openpyxl')
            pos_in_tab = (student_num - 1) % 10 
            start_col = (pos_in_tab * 6) + 1
            end_col = start_col + 5

            all_results = []
            for i in range(len(full_df)):
                if len(all_results) >= 100: break
                raw_row = full_df.iloc[i, start_col:end_col].tolist()
                try:
                    nums = [int(float(str(v).strip())) for v in raw_row]
                    all_results.append(process_java(nums) if logic_choice == "Java" else process_net(nums))
                except: continue

            final_df = pd.DataFrame(all_results, columns=['Output 1', 'Output 2', 'Output 3'])
            final_df.index = final_df.index + 1
            final_df = final_df.astype(int)

            # --- ACTION BUTTON ---
            logic_label = "Java" if logic_choice == "Java" else "Net"
            filename = f"[{student_num}] {student_name} - {logic_label}.xlsx"
            
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                final_df.to_excel(writer, index_label='#', sheet_name='Results')

            st.download_button(
                label=f"📥 Download Excel for {student_name}",
                data=output.getvalue(),
                file_name=filename,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
                type="primary"
            )

            # --- PREVIEW ---
            st.subheader("📊 Full Results Preview")
            st.dataframe(final_df, height=400, use_container_width=True)

    except Exception as e:
        st.error(f"Error: {e}")
