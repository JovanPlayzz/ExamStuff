import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import io
import os

# --- LOGIC FUNCTIONS ---
def process_java(n):
    # Mapping: n[0]=Num1, n[1]=Num2, n[2]=Num3, n[3]=Num4, n[4]=Num5
    arr = [0, 0, 0]
    for x in range(3):
        N1, N2, N3, N4, N5 = n[0], n[1], n[2], n[3], n[4]
        
        # Bottom-to-top evaluation following flowchart arrows
        if (N3 < x) and (x > N4):
            arr[x] = N1 + N5 + x
        elif (x > N1) and (N3 > x):
            arr[x] = N2 + N4 + x
        elif (N1 < x) or (x > N3):
            arr[x] = N1 + N3 + x
        else:
            arr[x] = N2 + N4 + N5
            
    return [arr[2], arr[1], arr[0]] # Descending display loop

def process_net(n):
    # Mapping: n[0]=Num1, n[1]=Num2, n[2]=Num3, n[3]=Num4, n[4]=Num5
    arr = [0, 0, 0]
    for x in range(2, -1, -1):
        # CORRECTED: Literal translation instead of operator flipping
        if (not (n[0] > x)) and (not (n[4] < x)): 
            arr[x] = n[0] + n[1] + x
        elif (not (n[1] < x)) and (not (n[2] < x)): 
            arr[x] = n[2] + n[4] + x
        elif (not (n[3] < x)) or (not (n[0] < x)): 
            arr[x] = n[0] + n[3] + x
        else: 
            arr[x] = n[1] + n[4] + x
            
    return [arr[0], arr[1], arr[2]]

def select_id(new_id):
    st.session_state.s_num = int(new_id)

# --- UI SETUP ---
st.set_page_config(page_title="Answerinator", layout="centered")

st.title("🚀 Java & Net Answerinator")
st.markdown("*Dont know the answers? just use this! it answers for you because your stupid.*")
st.divider()

if 's_num' not in st.session_state:
    st.session_state.s_num = 1

input_file = 'variables.xlsx'

if not os.path.exists(input_file):
    st.error("❌ File 'variables.xlsx' not found!")
else:
    col1, col2 = st.columns(2)
    with col1:
        section = st.selectbox("Section", ["Core", "Ryzen"])
    with col2:
        s_num = st.number_input("Student Number", min_value=1, step=1, key="s_num")

    with st.expander("🔍 Find my number"):
        query = st.text_input("Type name...", placeholder="Search...", key="search_box").lower()
        lookup_df = pd.read_excel(input_file, sheet_name=section, header=None)
        lookup_df.columns = ["ID", "Name"]
        
        if query:
            match = lookup_df[lookup_df['Name'].astype(str).str.lower().str.contains(query, na=False)]
            for _, row in match.head(5).iterrows():
                c1, c2 = st.columns([3, 1])
                c1.write(f"`{int(row['ID'])}` {row['Name']}")
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
            
            # Extract 101 rows to ensure we get 100 valid ones
            raw_vars = df.iloc[0:101, start_col:start_col+5]
            
            rows_list = []
            results = []
            
            for _, r in raw_vars.iterrows():
                try:
                    # Force conversion to integer and filter out NaNs
                    clean_r = [int(float(v)) for v in r.values if pd.notna(v)]
                    if len(clean_r) == 5:
                        rows_list.append(clean_r)
                        results.append(process_java(clean_r) if logic == "Java" else process_net(clean_r))
                except: continue
                if len(results) >= 100: break

            if results:
                clean_logic = "Java" if logic == "Java" else "Net"
                file_label = f"{s_num}: {student_name}-{clean_logic}.xlsx"
                
                # Prepare Excel Buffer
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    pd.DataFrame(results).to_excel(writer, index=False, header=False, sheet_name='Results')

                # Prepare Data for Clipboard (Tab-separated)
                final_df = pd.DataFrame(results)
                tsv_data = final_df.to_csv(index=False, sep='\t', header=False).strip().replace('\n', '\\n').replace('\r', '')

                # UI Buttons
                btn_col1, btn_col2 = st.columns(2)
                with btn_col1:
                    st.download_button(label="📥 Download Excel", data=output.getvalue(), file_name=file_label, use_container_width=True, type="primary")
                
                with btn_col2:
                    # JavaScript for Copy Button
                    copy_js = f"""
                        <button onclick="copyToClipboard()" style="
                            width: 100%; height: 38px; background-color: #262730; color: white; 
                            border: 1px solid rgba(250, 250, 250, 0.2); border-radius: 0.5rem; 
                            cursor: pointer; font-family: inherit; font-size: 14px;
                        ">📋 Copy to Clipboard</button>

                        <script>
                        function copyToClipboard() {{
                            const text = `{tsv_data}`;
                            navigator.clipboard.writeText(text.replace(/\\\\n/g, '\\n')).then(() => {{
                                alert('Copied 100 rows! You can now paste into the Spreadsheet.');
                            }});
                        }}
                        </script>
                    """
                    components.html(copy_js, height=50)
                
                # Answers Table (Integer only)
                display_df = final_df.copy()
                display_df.columns = ['Output 1', 'Output 2', 'Output 3']
                display_df.index = display_df.index + 1
                st.table(display_df.astype(int))

                # Variable List Button
                st.divider()
                if st.button("📋 List All Input Variables"):
                    with st.expander("Raw Variables Used", expanded=True):
                        var_df = pd.DataFrame(rows_list, columns=['V1', 'V2', 'V3', 'V4', 'V5']).astype(int)
                        var_df.index = var_df.index + 1
                        st.table(var_df)

    except Exception as e:
        st.info("Select a valid ID to display results.")
