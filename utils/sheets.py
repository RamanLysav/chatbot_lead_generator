from config import sheet

def append_row_to_sheet(row_data):
    sheet.append_row(row_data, value_input_option="USER_ENTERED")