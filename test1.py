import pandas as pd

def get_sheet_names(file_path):
    # Load the Excel file
    excel_data = pd.ExcelFile(file_path)
    
    # Get the list of sheet names
    sheet_names = excel_data.sheet_names
    
    return sheet_names