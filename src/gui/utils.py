from PyQt5.QtWidgets import QHBoxLayout, QWidget, QLabel, QLineEdit

# Background-color: rgba(255, 255, 255, 0)

textBoxStyle = """
                        color: "#444";
                        border: 2px solid #999;
                        border-radius: 5px;
                        background-color: #f5f5f5;
                        font-family: Arial, sans-serif;
                        font-weight: bold;
                        font-size: 14px;
                    """        
labelStyle = """
                    font-weight: bold; 
                    border: 0px solid black; 
                    border-radius: 5px;
                    font-size: 14px;
                    font-weight: bold;
                    color: #555555
                """
buttonStyle = """
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
comboBoxStyle = """
                    color: #444; 
                    font-weight: bold; 
                    background-color: #ff9999; 
                    border: 2px solid #999; 
                    border-radius: 5px
                """

layoutStyle = """
        border: 2px solid #ccc;
        border-radius: 5px;
        background: transparent        
    """
def ConvertMarkerEventsToList(markerEvents):
    listOfStrings = []
    for item in markerEvents:
        print(item)
        item = '   :::   '.join(str(x) for x in item)
        listOfStrings.append(item)
     
    return listOfStrings

def ConvertMappingsToListForMainDisplay(mappings):
    listOfStrings = []
    for item in mappings:
        print(item)
        item = ','.join(str(x) for x in item)
        listOfStrings.append(item)
     
    return listOfStrings

def GetFileNameFromPath(filePath):
    filename = filePath.split('/')[-1]
    return filename
      
def ConvertEegEventsToList(events):
    outputList = []
    for row in events:
        action = row[0]
        startTime = row[1]
        endTime = row[2]
        startIndex = row[3]
        endIndex = row[4]
        duration = row[5]
        outputList.append(f"{action} ::: {startTime}  :::     {endTime} ::: {startIndex} ::: {endIndex} ::: {duration}")
    return outputList

def ExtractWidgets(layout):
    widgets = []
    for i in range(layout.count()):
        item = layout.itemAt(i)
        if isinstance(item, QHBoxLayout):
            widgets.extend(ExtractWidgets(item))
        elif isinstance(item, QWidget):
            widgets.extend(ExtractWidgets(item.layout()))
        elif isinstance(item.widget(), QLabel) or isinstance(item.widget(), QLineEdit):
            widgets.append(item.widget())
    return widgets
