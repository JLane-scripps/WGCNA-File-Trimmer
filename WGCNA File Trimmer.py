import tkinter as tk
from tkinter import filedialog
import pandas as pd
import os

# Variable to store the selected input file
selected_input_file = ""
default_output_filename = ""


# Function to open a file dialog and set the input directory for frame1, which will remove blanks
def find_file_blanks():
    global selected_input_file
    selected_input_file = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])
    if selected_input_file:
        directory_entry.delete(0, tk.END)
        directory_entry.insert(0, os.path.dirname(selected_input_file))
        input_filename_entry.delete(0, tk.END)
        input_filename_entry.insert(0, os.path.basename(selected_input_file))

        # Set the default output filename to the original filename with "blanks removed" added
        original_filename = os.path.splitext(os.path.basename(selected_input_file))[0]
        default_output_filename = f"{original_filename}_blanks_removed"
        output_filename_entry.delete(0, tk.END)
        output_filename_entry.insert(0, default_output_filename)

# File finder for frame2, which will remove insignificant values.
def find_file_significants():
    global selected_input_file
    selected_input_file = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])
    if selected_input_file:
        directory_entry2.delete(0, tk.END)
        directory_entry2.insert(0, os.path.dirname(selected_input_file))
        input_filename_entry2.delete(0, tk.END)
        input_filename_entry2.insert(0, os.path.basename(selected_input_file))

        # Set the default output filename to the original filename with "significants" added
        original_filename = os.path.splitext(os.path.basename(selected_input_file))[0]
        default_output_filename = f"{original_filename}_significants"
        output_filename_entry2.delete(0, tk.END)
        output_filename_entry2.insert(0, default_output_filename)


# Function to read and filter the Excel file (previously "second_function")
def remove_blanks():
    try:
        # Get the directory path and input filename from the text fields
        input_directory = directory_entry.get()
        input_filename = input_filename_entry.get()
        output_filename = output_filename_entry.get()

        # Construct the full input and output file paths
        input_excel_file = os.path.join(input_directory, input_filename)
        output_excel_file = os.path.join(input_directory, f"{output_filename}.xlsx")

        # Load the Excel file into a DataFrame and ensure all columns are read as text
        df = pd.read_excel(input_excel_file, engine='openpyxl', dtype=str)

        # Temporarily replace missing values with a unique placeholder
        placeholder_value = "MISSING"
        df = df.fillna(placeholder_value)

        # Debugging: Print the DataFrame after filling missing values for verification
        print("DataFrame after filling missing values:\n", df)

        # Remove rows containing the placeholder
        df = df[~df.isin([placeholder_value]).any(axis=1)]

        # Debugging: Print the DataFrame after removing rows with the placeholder
        print("DataFrame after removing rows with placeholder values:\n", df)

        # Save the filtered DataFrame as an Excel file
        df.to_excel(output_excel_file, index=False, engine='openpyxl')

        result_label.config(text=f"Filtered data saved to {output_excel_file}")
    except FileNotFoundError:
        result_label.config(text="File not found. Please check the file path.")
    except Exception as e:
        result_label.config(text=f"An error occurred: {str(e)}")


def find_significance():
    try:
        # Get the directory path and input filename from the text fields
        input_directory = directory_entry2.get()
        input_filename = input_filename_entry2.get()
        output_filename = output_filename_entry2.get()

        # Construct the full input and output file paths
        input_excel_file = os.path.join(input_directory, input_filename)
        output_excel_file = os.path.join(input_directory, f"{output_filename}.xlsx")

        # Read all sheets from the Excel file
        xls = pd.ExcelFile(input_excel_file)

        # Create an empty DataFrame to store the combined data
        combined_df = pd.DataFrame()

        for sheet_name in xls.sheet_names:
            print("Now reading sheet ", sheet_name, "\n")
            # Load the sheet into a DataFrame
            df = pd.read_excel(xls, sheet_name, engine='openpyxl')

            # Find the "significant" column (technically unnecessary, can be deleted)
            sig_column = list(df.columns)[1]

            # Filter (keep) rows where the "significant" column contains the BOOLEAN true (NOT A STRING)
            df = df[df[sig_column] == True]

            # For debugging, and to view the number of columns marked true per sheet in the console.
            print(df)

            # Add a new column for the sheet name
            df['sheet_name'] = sheet_name

            # Append the filtered DataFrame to the combined DataFrame. All sheets are combined into one
            combined_df = pd.concat([combined_df, df], ignore_index=True)

        # Identify and remove all occurrences of duplicate values (INCLUDING ORIGINAL) in the "term_id" column
        combined_df = combined_df[~combined_df['term_id'].duplicated(keep=False)]

        # Save the filtered DataFrame as an Excel file
        combined_df.to_excel(output_excel_file, index=False, engine='openpyxl')

        result_label2.config(text=f"Filtered data saved to {output_excel_file}")
    except FileNotFoundError:
        result_label2.config(text="File not found. Please check the file path.")
    except Exception as e:
        result_label2.config(text=f"An error occurred: {str(e)}")



# Create the main application window
app = tk.Tk()
app.title("WGCNA File Trimmer")

# Set the window size to fit both frames and adjust the height
app.geometry("890x360+50+50")

# ---- FRAME 1 ----
# Create a container frame for the first operation
frame1 = tk.Frame(app, padx=10, pady=10, bd=1, relief=tk.RAISED)
frame1.grid(row=0, column=0, padx=10, pady=10)

# Create and pack a label at the top of frame1. This step is for data before analysis.
frame1_label = tk.Label(frame1, text="Remove Proteins with Blank Values", font=("Arial", 14))
frame1_label.grid(row=0, columnspan=2, pady=10)

# Create and pack a "Find File" button in frame1
find_file_button = tk.Button(frame1, text="Find Excel File", command=find_file_blanks)
find_file_button.grid(row=1, column=0, pady=10)

# Create and pack a label and text entry field for the directory in frame1 (adjusted width)
directory_label = tk.Label(frame1, text="Enter Directory:")
directory_label.grid(row=2, column=0, pady=5)
directory_entry = tk.Entry(frame1, width=50)
directory_entry.grid(row=2, column=1, pady=5)

# Create and pack a label and text entry field for the input filename in frame1 (adjusted width)
input_filename_label = tk.Label(frame1, text="Input Filename:")
input_filename_label.grid(row=3, column=0, pady=5)
input_filename_entry = tk.Entry(frame1, width=50)
input_filename_entry.grid(row=3, column=1, pady=5)

# Create and pack a label and text entry field for the output filename in frame1 (adjusted width)
output_filename_label = tk.Label(frame1, text="Output Filename:")
output_filename_label.grid(row=4, column=0, pady=5)
output_filename_entry = tk.Entry(frame1, width=50)
output_filename_entry.grid(row=4, column=1, pady=5)

# Set the default output filename to the original filename with "removed_blanks" added
output_filename_entry.insert(0, default_output_filename)

# Create and pack a process button in frame1
process_button = tk.Button(frame1, text="Remove Blanks", command=remove_blanks)
process_button.grid(row=5, column=0, columnspan=2, pady=10)

# Create and pack a result label in frame1
result_label = tk.Label(frame1, text="This step is for data files before WGCNA analysis", wraplength=350)
result_label.grid(row=6, column=0, columnspan=2, pady=30)

# ---- FRAME 2 ----
# Duplicate frame1 to create frame2
frame2 = tk.Frame(app, padx=10, pady=10, bd=1, relief=tk.RAISED)
frame2.grid(row=0, column=1, padx=10, pady=10)

# Create and pack a label at the top of frame2 ("Remove Insignificance")
frame2_label = tk.Label(frame2, text="Remove Insignificance", font=("Arial", 14))
frame2_label.grid(row=0, columnspan=2, pady=10)

# Create and pack a "Find File" button in frame2
find_file_button2 = tk.Button(frame2, text="Find Excel File", command=find_file_significants)
find_file_button2.grid(row=1, column=0, pady=10)

# Create and pack a label and text entry field for the directory in frame2 (adjusted width)
directory_label2 = tk.Label(frame2, text="Enter Directory:")
directory_label2.grid(row=2, column=0, pady=5)
directory_entry2 = tk.Entry(frame2, width=50)
directory_entry2.grid(row=2, column=1, pady=5)

# Create and pack a label and text entry field for the input filename in frame2 (adjusted width)
input_filename_label2 = tk.Label(frame2, text="Input Filename:")
input_filename_label2.grid(row=3, column=0, pady=5)
input_filename_entry2 = tk.Entry(frame2, width=50)
input_filename_entry2.grid(row=3, column=1, pady=5)

# Create and pack a label and text entry field for the output filename in frame2 (adjusted width)
output_filename_label2 = tk.Label(frame2, text="Output Filename:")
output_filename_label2.grid(row=4, column=0, pady=5)
output_filename_entry2 = tk.Entry(frame2, width=50)
output_filename_entry2.grid(row=4, column=1, pady=5)

# Create and pack a process button in frame2 ("Remove Insignificance")
process_button2 = tk.Button(frame2, text="Remove Insignificance", command=find_significance)
process_button2.grid(row=5, column=0, columnspan=2, pady=10)

# Create and pack a result label in frame2 with text wrapping (in pixels)
result_label2 = tk.Label(frame2, text="This step is for gprofiler results given from analysis", wraplength=350)
result_label2.grid(row=6, column=0, columnspan=2, pady=30)

# Run the main application loop
app.mainloop()
