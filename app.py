import streamlit as st
import pandas as pd
from io import BytesIO

# Variable to store the selected input file
file_name = ""

st.title("WGCNA File Trimmer")
# Sidebar
st.sidebar.header("Select Operation")
operation = st.sidebar.radio("", ["Remove Blanks", "Remove Insignificance"])

# File selection
st.sidebar.header("File Selection")
file = st.sidebar.file_uploader('input file', type='.xlsx')

# Process
if st.sidebar.button("Process"):
    if operation == "Remove Blanks":
        try:
            # Load the Excel file into a DataFrame
            df = pd.read_excel(file, engine='openpyxl')
            df = df.dropna()
            file_name = file.name.removesuffix('.xlsx')
            st.dataframe(df)
            out_file = df.to_csv()
            st.download_button('download file', out_file, f"{file_name}_blanks_removed.csv")
            st.success(f"Filtered data saved to {file_name}_blanks_removed")
        except FileNotFoundError:
            st.error("File not found. Please check the file path.")
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

    elif operation == "Remove Insignificance":
        try:
            # Get the original file name and prepare an appended name for it
            file_name = file.name.removesuffix('.xlsx')
            file_name = file_name.rstrip(file_name[-1])
            file_name = f"{file_name}_significant"
            excel_output = BytesIO()

            # read in the orig file and begin to filter it, sheet by sheet. df = dataframe
            xls = pd.ExcelFile(file)
            combined_df = pd.DataFrame()
            for sheet_name in xls.sheet_names:
                df = pd.read_excel(xls, sheet_name, engine='openpyxl')
                sig_column = list(df.columns)[1]
                # Filter (keep) rows where the "significant" column contains the BOOLEAN true (NOT A STRING)
                df = df[df[sig_column] == True]
                st.write(df)  # debugging, prints in console
                df['sheet_name'] = sheet_name
                # combined_df = pd.concat([combined_df, df], ignore_index=True)
                # Identify and remove all occurrences of duplicate values (INCLUDING ORIGINAL) in the "term_id" column
                df = df[~df['term_id'].duplicated(keep=False)]
                df.to_excel(excel_output, sheet_name= sheet_name, index = False, engine='openpyxl')
                # end of for loop

            # Save the filtered DataFrame as an Excel file
            # combined_df.to_excel(excel_output, index=False, engine='openpyxl')
            excel_output.seek(0)
            # Provide BytesIO object as data for the download button
            st.download_button('download file', excel_output, f"{file_name}.xlsx")

            st.success(f"Filtered data saved to {file_name}")
        except FileNotFoundError:
            st.error("File not found. Please check the file path.")
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
