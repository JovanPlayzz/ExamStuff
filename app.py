import streamlit as st
import pandas as pd
import io
import os

# --- LEAN LOGIC FUNCTIONS ---
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

input_file = 'variables.xlsx'

if not os.path.exists(input_file):
    st.error("❌ variables.xlsx missing!")
else:
    # --- ROW 1: INPUTS ---
    col1, col2 = st.columns(2)
    with col1:
        section = st.selectbox("Section", ["Core", "Ryzen"])
    with col2:
        # Simple, direct number input
        s_num = st.number_input("Student Number", min_value=1, step=1)

    # --- THE SEARCH DROPDOWN ---
    with st.expander("🔍 Find my number"):
        # Textbox stays active while open
        query = st.text_input("Type name...", placeholder="Search...", key="search_box").lower()
        
        # Load only necessary columns to save memory/speed
        lookup_df = pd.read_excel(input_file, sheet_name=section, usecols=[0, 1], header=None, engine='openpyxl')
        lookup_df.columns = ["ID", "Name"]
        
        if query:
            match = lookup_df[lookup_df['Name'].str.lower().str.contains(query, na=False)]
            for _, row in match.head(5).iterrows():
                c1, c2 = st.columns([3, 1])
                c1.write(f"`{row['ID']}` {row['Name']}")
                # This just gives the ID; you type it into the Student Number box above
                if c2.button("Copy ID", key=f"cp_{row['ID']}", use_container_width=True):
                    st.info(f"ID is {row['ID']} - Type it above!")

    logic = st.radio("Logic", ["Java", ".NET"], horizontal=True)

    # --- FAST PROCESSING ---
    try:
        # Load name
        names_df = pd.read_excel(input_file, sheet_name=section, header=None, engine='openpyxl')
        student_name = names_df[names_df[0] == s_num].iloc[0, 1]
        st.success(f"✅ **{student_name}**")

        # Load only the required student's data range
        lower = ((s_num - 1) // 10) * 10 + 1
        data_tab = f"Student {lower} to {lower + 9}"
        df = pd.read_excel(input_file, sheet_name=data_tab, header=None, engine='openpyxl')
        
        start_col = ((s_num - 1) % 10 * 6) + 1
        raw_data = df.iloc[0:100, start_col:start_col+5].values.tolist()

        # Calculate everything in one go
        results = [process_java(r) if logic == "Java" else process_net(r) for r in raw_data]
        
        final_df = pd.DataFrame(results, columns=['Output 1', 'Output 2', 'Output 3']).astype(int)
        final_df.index = final_df.index + 1

        # Excel Export
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            final_df.to_excel(writer, index_label='#', sheet_name='Results')

        st.download_button(
            label="📥 Download Result",
            data=output.getvalue(),
            file_name=f"[{s_num}] {student_name}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            type="primary"
        )

        st.dataframe(final_df, height=350, use_container_width=True)

    except:
        st.info("Select a valid student ID.")
