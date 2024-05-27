from PyQt5.QtWidgets import  QHBoxLayout, QWidget, QLabel, QLineEdit


#background-color: rgba(255, 255, 255, 0)

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
                    font-weight: bold;
                    color: #555555
                """
button_style = """
            QPushButton { 
                background-color: #B0C4DE;
                color: black;
                border-style: outset; 
                border-width: 2px; 
                border-radius: 5px; 
                border-color: beige; padding: 4px; 
                font-weight: bold
            } 
            
            QPushButton:pressed { 
                background-color: #5F9EA0; 
                border-style: inset; }"
        """
combobox_style = """
                    color: #444; 
                    font-weight: bold; 
                    background-color: #ff9999; 
                    border: 2px solid #999; 
                    border-radius: 5px
                """

def convert_mappings_to_list_for_mainDisplay(mappings):
    list_of_strings = []
    for item in mappings:
        print(item)
        item = ','.join(str(x) for x in item)
        list_of_strings.append(item)
     
    return list_of_strings

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


def extract_widgets(layout):
    widgets = []
    for i in range(layout.count()):
        item = layout.itemAt(i)
        if isinstance(item, QHBoxLayout):
            widgets.extend(extract_widgets(item))
        elif isinstance(item, QWidget):
            widgets.extend(extract_widgets(item.layout()))
        elif isinstance(item.widget(), QLabel) or isinstance(item.widget(), QLineEdit):
            widgets.append(item.widget())
    return widgets