
text_box_style = """
                        color: "#444";
                        border: 2px solid #999;
                        border-radius: 5px;
                        background-color: #f5f5f5;
                        font-family: Arial, sans-serif;
                        font-weight: bold;
                        font-size: 14px;
                    """        
label_style = """
                    font-weight: bold; 
                    border: 0px solid black; 
                    border-radius: 5px;
                    font-size: 14px;
                    font-weight: bold
                """
button_style = """
                QPushButton {
                    background-color: #ff6666;
                    color: black;
                    border-radius: 5px;
                    padding: 5px;
                    border: 1px solid #999;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #ff9999;
                }
            """
combobox_style = """
                    color: #444; 
                    font-weight: bold; 
                    background-color: #ff9999; 
                    border: 2px solid #999; 
                    border-radius: 5px
                """



def get_file_name_from_path(file_path):
    filename = file_path.split('/')[-1]
    return filename
      
def convert_eeg_events_to_list(events):
    output_list = []
    for row in events:
        action = row[0]
        start_time = row[1]
        end_time = row[2]
        start_index = row[3]
        end_index = row[4]
        duration = row[5]
        output_list.append(f"{action} ::: {start_time}  :::     {end_time} ::: {start_index} ::: {end_index} ::: {duration}")
    return output_list