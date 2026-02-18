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

# --- CALLBACK: UPDATE ID & SHOW TOAST ---
def select_id(new_id):
    st.session_state.s_num = int(new_id)
    st.toast("Inputted successfully!", icon="✅")

# --- UI SETUP ---
st.set_page_config(page_title="Logic Processor", layout="centered")
st.title("📱 Logic Processor")

# Initialize Session State if not exists
if 's_num' not in st.session_state:
    st.session_state.s_num = 1

input_file = 'variables.xlsx'

if not os.path.exists(input_file):
    st.error("❌ variables.xlsx missing!")
else:
    # --- ROW 1: INPUTS ---
    col1, col2 = st.columns(2)
    with col1:
        section = st.selectbox("Section", ["Core", "Ryzen"])
    with col2:
        # Use key="s_num" to link it directly to session state
        s_num = st.number_input("Student Number", min_value=1, max_value=40, step=1, key="s_num")

    # --- SEARCH DROPDOWN ---
    with st.expander("🔍 Find my number"):
        query = st.text_input("Type name...", placeholder="Search...", key="search_box").lower()
        
        lookup_df = pd.read_excel(input_file, sheet_name=section, usecols=[0, 1], header=None)
        lookup_df.columns = ["ID", "Name"]
        
        if query:
            match = lookup_df[lookup_df['Name'].str.lower().str.contains(query, na=False)]
            match = match[match['ID'] <= 40] # Keep within your 40-student limit
            
            for _, row in match.head(5).iterrows():
                c1, c2 = st.columns([3, 1])
                c1.write(f"`{row['ID']}` {row['Name']}")
                c2.button("Pick", key=f"sel_{row['ID']}", on_click=select_id, args=(row['ID'],), use_container_width=True)

    logic = st.radio("Logic", ["Java", ".NET"], horizontal=True)

    # --- PROCESSING (The Table and Button part) ---
    try:
        # Load Name List
        names_df = pd.read_excel(input_file, sheet_name=section, header=None)
        
        # Find the specific student
        student_match = names_df[names_df[0] == s_num]
        
        if not student_match.empty:
            student_name = str(student_match.iloc[0, 1]).strip()
            st.success(f"✅ **{student_name}**")

            # Calculate which tab to open
            lower_bound = ((s_num - 1) // 10) * 10 + 1
            data_tab = f"Student {lower_bound} to {lower_bound + 9}"
            
            # Load the data for calculations
            df = pd.read_excel(input_file, sheet_name=data_tab, header=None)
            
            # Find the starting column for this specific student
            start_col = ((s_num - 1) % 10 * 6) + 1
            
            # Extract the 5 variables across 100 rows
            raw_data = df.iloc[0:100, start_col:start_col+5].values.tolist()

            # Process the logic
            results = [process_java(r) if logic == "Java" else process_net(r) for r in raw_data]
            
            # Create the Result DataFrame
            final_df = pd.DataFrame(results, columns=['Output 1', 'Output 2', 'Output 3']).astype(int)
            final_df.index = final_df.index + 1

            # --- ACTION BUTTONS ---
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                final_df.to_excel(writer, index_label='#', sheet_name='Results')

            st.download_button(
                label=f"📥 Download Excel",
                data=output.getvalue(),
                file_name=f"[{s_num}] {student_name}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
                type="primary"
            )

            # Display the full table
            st.dataframe(final_df, height=350, use_container_width=True)
        else:
            st.warning(f"ID {s_num} not found in {section} section.")

    except Exception as e:
        st.info("Select a valid ID (1-40) to see results.")
