import streamlit as st
import pandas as pd
from io import BytesIO

# Variable to store the selected input file
file_name = ""

st.title("WGCNA File Trimmer")
st.markdown(body="Welcome. This program is a very simple tool to benefit the researcher using WGCNA "
        "(weighted gene co-expression network analysis), specifically the MetaNetwork "
        "( https://github.com/avcarr2/MetaNetwork/tree/master ). ")
st.divider()
st.header("Remove Blanks:")
st.markdown(body="This function is useful for formatting data BEFORE entering files into the WGCNA MetaNetwork. MetaNetwork does "
        "not handle blank values well, crashing mid-job or attributing incorrect values; therefore it is necessary to "
        "remove all rows that contain blank values before running the analysis. Note that entering 0's for all blanks "
        "may affect data integrity and give very incorrect results. This function copies the original input dataframe, "
        "removes every row (usually the entire protein) that contains a blank cell, and saves the result as a new "
        "file. File names are automatically generated from the original file's name with an appended 'blanks_removed' --"
        " no original data is altered or lost. Files are found using the 'Find File' button opening user directory. "
        "The console will print contracted versions of the dataframe ater it is read and after it is adjusted.  "
        "Known Issue*: If two or more columns share the same name, each duplicate will have a '.X' appended to them "
        "where X = the number of duplicates.")
st.divider()
st.header("Remove Insignificance:")
st.markdown(body="This function is useful for formatting data AFTER a WGCNA MetaNetwork analysis has "
        "been run, and the results have been downloaded. It takes in the 'gProfiler_Enrichment_Results.' file* which "
        "should have one sheet per module created by the MetaNetwork. Again, to avoid data loss or alteration, "
        "each sheet is copied in (and again printed to console), filtered to keep only rows marked as TRUE in the "
        "'significant' column* (marked as significant by the MetaNetwork parameters) and concatenated all to the same "
        "new dataframe. The console shows the number of rows marked significant in each sheet, which may be useful to you."
        "Rows are marked by which sheet (aka which color module) they came from in a new column added to the end."
        "The function then removes all rows with Term_ID's appearing more than once. It removes duplicates AND the "
        "first to appear in the dataset. This leaves only truly unique and significant results. "
        "The file is saved with the original file's name + '_significants' next to the original.")
# Sidebar
st.sidebar.header("Select Operation")
operation = st.sidebar.radio(" ", ["Remove Blanks", "Remove Insignificance"])

# File selection
st.sidebar.header("File Selection")
file = st.sidebar.file_uploader('input file', type='.xlsx')

# Process
if st.sidebar.button("Process"):
    if operation == "Remove Blanks":
        try:
            # Load the Excel file into a DataFrame
            df = pd.read_excel(file, engine='openpyxl')

            # Temporarily replace missing values with a unique placeholder
            placeholder_value = "MISSING"
            df = df.fillna(placeholder_value)

            # Remove rows containing the placeholder
            df = df[~df.isin([placeholder_value]).any(axis=1)]

            # Name and provide new downloadable file
            file_name = file.name.removesuffix('.xlsx')
            st.dataframe(df)
            out_file = df.to_csv(index=False)
            st.download_button('download file', out_file, f"{file_name}_blanks_removed.csv")
            st.success(f"Filtered data saved to {file_name}_blanks_removed")
        except FileNotFoundError:
            st.error("File not found. Please check the file path.")
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

    elif operation == "Remove Insignificance":
        try:
            xls = pd.ExcelFile(file)
            combined_df = pd.DataFrame()
            for sheet_name in xls.sheet_names:
                df = pd.read_excel(xls, sheet_name, engine='openpyxl')
                sig_column = list(df.columns)[1]
                # Filter (keep) rows where the "significant" column contains the BOOLEAN true (NOT A STRING)
                df = df[df[sig_column] == True]
                st.write(df)  # debugging, prints in console
                df['sheet_name'] = sheet_name
                combined_df = pd.concat([combined_df, df], ignore_index=True)
                # end of for loop
            # Identify and remove all occurrences of duplicate values (INCLUDING ORIGINAL) in the "term_id" column
            combined_df = combined_df[~combined_df['term_id'].duplicated(keep=False)]
            file_name = file.name.removesuffix('.xlsx')  # removes file type from name, obviously
            file_name = file_name.rstrip(file_name[-1])  # removes annoying extra period MetaNetwork gives the file
            file_name = f"{file_name}_significant"
            excel_output = BytesIO()  # necessary step for making the file savable in streamlit

            # re-sort unique results back into separate sheets
            with pd.ExcelWriter(excel_output, engine='openpyxl') as writer:
                for sheet_name in xls.sheet_names:
                    df_sheet = combined_df[combined_df['sheet_name'] == sheet_name]
                    df_sheet.to_excel(writer, sheet_name=sheet_name, index=False)
                # end of for loop
            # combined_df.to_excel(excel_output, index=False, engine='openpyxl')
            excel_output.seek(0)
            # Provide BytesIO object as data for the download button
            st.download_button('download file', excel_output, f"{file_name}.xlsx")

            st.success(f"Filtered data saved to {file_name}")
        except FileNotFoundError:
            st.error("File not found. Please check the file path.")
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
