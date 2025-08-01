
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import re

st.set_page_config(page_title="EV CAN Dashboard - RSOC & Current", layout="wide")
st.title("🔋 Battery Current and RSOC from CAN ID 0x419")
st.markdown("Upload a decoded CAN Excel file to visualize Battery Current and RSOC for CAN ID `0x419`.")

uploaded_file = st.file_uploader("Choose an Excel file", type=["xlsx", "xls"])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)
        st.success("File uploaded successfully.")

        # Step 1: Filter rows where CAN ID is 0x419
        filtered_df = df[
            df.apply(lambda row: (
                '0x419' in str(row.get('CAN ID', '')).lower() or
                '0x419' in str(row.get('Decoded Name', '')).lower()
            ), axis=1)
        ]

        # Step 2: Identify columns
        time_col = next((col for col in filtered_df.columns if 'time' in col.lower()), None)
        decoded_col = next((col for col in filtered_df.columns if 'battery current' in str(filtered_df[col].iloc[0]).lower()), None)

        if not time_col or not decoded_col:
            st.error("❌ Required columns (Timestamp and Decoded Summary) not found.")
        else:
            # Step 3: Extract values using regex
            def extract_values(text):
                current_match = re.search(r"Battery Current:\s*([-+]?\d*\.?\d+)", text)
                rsoc_match = re.search(r"RSOC:\s*(\d+)", text)
                current = float(current_match.group(1)) if current_match else None
                rsoc = float(rsoc_match.group(1)) if rsoc_match else None
                return current, rsoc

            filtered_df['Battery Current'] = filtered_df[decoded_col].apply(lambda x: extract_values(str(x))[0])
            filtered_df['RSOC'] = filtered_df[decoded_col].apply(lambda x: extract_values(str(x))[1])

            # Plotting
            fig, ax1 = plt.subplots(figsize=(12, 6))

            ax1.set_xlabel("Time")
            ax1.set_ylabel("Battery Current (A)", color="tab:red")
            ax1.plot(filtered_df[time_col], filtered_df['Battery Current'], color="tab:red")
            ax1.tick_params(axis='y', labelcolor="tab:red")

            ax2 = ax1.twinx()
            ax2.set_ylabel("RSOC (%)", color="tab:blue")
            ax2.plot(filtered_df[time_col], filtered_df['RSOC'], color="tab:blue", linestyle='--')
            ax2.tick_params(axis='y', labelcolor="tab:blue")

            plt.title("Battery Current and RSOC from CAN ID 0x419")
            plt.grid(True)
            st.pyplot(fig)

            with st.expander("📄 View Extracted Data"):
                st.dataframe(filtered_df[[time_col, 'Battery Current', 'RSOC']])

    except Exception as e:
        st.error(f"❌ Error: {e}")
else:
    st.info("Please upload a decoded CAN Excel file to begin.")
