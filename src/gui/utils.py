from PyQt5.QtWidgets import QHBoxLayout, QWidget, QLabel, QLineEdit, QSizePolicy
from PyQt5.QtWidgets import QPushButton, QComboBox, QListWidget
from PyQt5.QtGui import QColor

size_policy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)



textBoxStyle = """
                        color: "#444";
                        border: 2px solid green;
                        border-radius: 3px;
                        background-color: #f5f5f5;
                        font-family: Arial, sans-serif;
                        font-weight: bold;
                        font-size: 10px;
                    """        

labelStyle = """
                    color: "green";
                    border: 2px solid red;
                    border-radius: 0px;
                    background-color: yellow;
                    font-family: Arial, sans-serif;
                    font-weight: bold;
                    font-size: 10px;
                """

buttonStyle = """
            QPushButton { 
                background-color: #ADD8E6;
                color: black;
                border-style: outset; 
                border-width: 2px; 
                border-radius: 3px; 
                border-color: red; padding: 4px; 
                font-weight: bold;
                color : black
            } 
            
            QPushButton:pressed { 
                background-color: #5F9EA0; 
                border-style: inset; }"
        """

comboBoxStyle = """
                    color: black; 
                    font-weight: bold; 
                    background-color: #ff9999; 
                    border: 2px solid #999; 
                    border-radius: 5px
                """

layoutStyle = """
        border: 2px solid black;
        border-radius: 5px;
        background-color: #E0FFFF;        
    """
layoutStyleItems = """
        border: 0px solid black;
        border-radius: 1px;
        background-color: #E0FFFF;
    """
def jsonSideCar(metadata):
    pass

def setTextProperty(item, value):
    item.setText(str(value))

def createQLabel(title):
    label = QLabel(title)
    label.setStyleSheet(labelStyle)
    label.setSizePolicy(size_policy)

    return label

def createQPushButton(title):
    button = QPushButton(title)
    button.setStyleSheet(buttonStyle)
    button.setSizePolicy(size_policy)

    return button

def createQLineEdit(title):
    text = QLineEdit(title)
    text.setStyleSheet(textBoxStyle)
    text.setSizePolicy(size_policy)
    text.setReadOnly(True)

    return text

def createQComboBox(title):
    box = QComboBox()
    box.addItem(title)
    box.setStyleSheet(comboBoxStyle)

    return box

def createQListWidget():

    listWidget = QListWidget()
    listWidget.setStyleSheet(comboBoxStyle)

    return listWidget

def createMappingListColors(mappings):
        mappingsWithColor = []
        color = 'red'
        for mapping in mappings:
            block = mapping.split(',')[0]
            if block == 'StartBlockSaying':
                color = 'red'
            if block == 'StartBlockThinking':
                color ='green'

            mappingsWithColor.append([mapping, QColor(color)])
            
        return mappingsWithColor

def wrapLayoutInWidget(layout, layoutStyle = layoutStyle):
        widget = QWidget()
        widget.setLayout(layout)
        widget.setStyleSheet(layoutStyle)  
        return widget


def convertMarkerEventsToList(markerEvents):
    listOfStrings = []
    for item in markerEvents:
        print(item)
        item = '   :::   '.join(str(x) for x in item)
        listOfStrings.append(item)
     
    return listOfStrings

def convertMappingsToListForMainDisplay(mappings):
    listOfStrings = []
    for item in mappings:
        
        item = ','.join(str(x) for x in item)
        listOfStrings.append(item)
     
    return listOfStrings

def getFileNameFromPath(filePath):
    filename = filePath.split('/')[-1]
    return filename
      
def convertEegEventsToList(events):
    outputList = []
    for row in events:
        print(row)
        action = row[0]
        startTime = row[1]
        endTime = row[2]
        startIndex = row[3]
        endIndex = row[4]
        duration = row[5]
        outputList.append(f"{action} ::: {round(startTime)}  :::     {round(endTime)} ::: {startIndex} ::: {endIndex} ::: {duration}")
    return outputList

def extractWidgets(layout):
    widgets = []
    for i in range(layout.count()):
        item = layout.itemAt(i)
        if isinstance(item, QHBoxLayout):
            widgets.extend(extractWidgets(item))
        elif isinstance(item, QWidget):
            widgets.extend(extractWidgets(item.layout()))
        elif isinstance(item.widget(), QLabel) or isinstance(item.widget(), QLineEdit):
            widgets.append(item.widget())
    return widgets
