from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout
from PyQt5.QtWidgets import QVBoxLayout, QLabel,QLineEdit ,QTableWidget,QTableWidgetItem, QFileDialog, QMessageBox
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QIcon, QColor
import pyqtgraph as pg
import numpy as np
import config
from gui.utils import getFileNameFromPath, createQListWidget, setTextProperty, layoutStyleItems
from gui.utils import  wrapLayoutInWidget, createQComboBox ,createQLabel, createQPushButton
from gui.utils import createQLineEdit,layoutStyle, extractWidgets
from classes.eeg import EegData
from classes.audio import AudioData
import config
import os
from pathlib import Path

class MappingWindow(QMainWindow):
    aboutToClose = pyqtSignal()
    def __init__(self, eegAudioData):
        super().__init__()
        
        self.eegAudioData = eegAudioData
        self.audioSamplingRate = self.eegAudioData.audioData.samplingFrequency
        
        self.setWindowTitle('Mapping EEG and AUDIO Data')
        self.setGeometry(500, 300, 1300, 300)
        self.setWindowIcon(QIcon(config.windowIconPath)) 
        self.setStyleSheet("background-color: #f0f0f0;")
        
        centralWidget = QWidget()
        self.setCentralWidget(centralWidget)
        self.mainLayout = QHBoxLayout()
        centralWidget.setLayout(self.mainLayout)

        mappingsLayout, plotsAndOther = self.setupLayouts()

        self.mainLayout.addLayout(mappingsLayout, 20)  
        self.mainLayout.addLayout(plotsAndOther, 19)
        self.setMappingTableData()

    def setupLayouts(self):
        mappingsLayout = self.setupMappingsLayout()
        plotsAndOtherLayout = self.setupPlotsAndOtherLayout()
        self.connectSignals()
        
        return mappingsLayout, plotsAndOtherLayout
    
    def connectSignals(self):
        self.connectMappingsSignals()
        #self.connectAudioSignals() 
        self.connectPreviousNextSaveDiscardSignals()

    def connectPreviousNextSaveDiscardSignals(self):
        self.previousButton.clicked.connect(self.previousMappingInfoLayout)
        self.nextButton.clicked.connect(self.nextMappingInfoLayout)
        self.discardButton.clicked.connect(self.nextMappingInfoLayout)

    def connectMappingsSignals(self):
        self.mappingTableWidget.cellClicked.connect(self.mappingDataCellClicked)

    ################################################################################
    #############################  Mappings Table Layout ###########################
    ################################################################################

    def setupMappingsLayout(self):
        mainLayout = QHBoxLayout()
        
        self.mappingTableWidget = QTableWidget()
        self.mappingTableWidget.setStyleSheet(layoutStyle)
        self.mappingTableWidget.setRowCount(0)
        self.mappingTableWidget.setColumnCount(9)
        headers = ["Marker", "Word", "EEG Start Time", "EEG End Time", "EEG Start Index", "EEG End Index", "Audio Start Index", "Duration", 'Audio Start Time']
        self.mappingTableWidget.setHorizontalHeaderLabels(headers)

        mainLayout.addWidget(self.mappingTableWidget)
        return mainLayout
    

    ################################################################################
    #############################  Plots and Other Layout ##########################
    ################################################################################

    def setupPlotsAndOtherLayout(self):
        mainlayout = QVBoxLayout()
        

        plotsLayoutWidget = self.setupPlotsLayout()
        playAndStopButtonsLayoutWidget = self.setupPlayAndStopButtonsLayout()
        mappingInformationLayoutWidget = self.setupMappingInformationLayout()
        bidsInfoLayoutWidget = self.setupBIDSInfoLayout()
        saveNextPreviousDiscardLayoutWidget = self.setupSaveNextPreviousDiscardLayout()
        
        mainlayout.addWidget(plotsLayoutWidget)
        mainlayout.addWidget(playAndStopButtonsLayoutWidget)
        mainlayout.addWidget(mappingInformationLayoutWidget)
        mainlayout.addWidget(bidsInfoLayoutWidget)
        mainlayout.addWidget(saveNextPreviousDiscardLayoutWidget)
       

        return mainlayout
    
    def setupBIDSInfoLayout(self):
        rowLayout = QHBoxLayout()
        rowLayoWidget = wrapLayoutInWidget(rowLayout)


        subjectID = createQLabel('PatientID: ')
        self.subjectID = createQLineEdit('', enable=False)
        sessionID = createQLabel('Session No.')
        self.sessionID = createQLineEdit('', enable=False)

        rowLayout.addWidget(subjectID)
        rowLayout.addWidget(self.subjectID)
        rowLayout.addWidget(sessionID)
        rowLayout.addWidget(self.sessionID)

        return rowLayoWidget

    def setupSaveNextPreviousDiscardLayout(self):
        rowLayout = QHBoxLayout()
        rowLayoWidget = wrapLayoutInWidget(rowLayout)

        self.previousButton = createQPushButton('Previous')
        self.nextButton = createQPushButton('Next')
        self.saveButton = createQPushButton('Save')
        self.discardButton = createQPushButton('Discard')

        rowLayout.addWidget(self.previousButton)
        rowLayout.addWidget(self.nextButton)
        rowLayout.addWidget(self.saveButton)
        rowLayout.addWidget(self.discardButton)
     
        return rowLayoWidget
    
    def setupMappingInformationLayout(self):
        self.labels = ["Action:", "Word:", "StartTime(EEG):", "EndTime(EEG):", "StartIndex(EEG):", "EndIndex(EEG):", "StartIndex(Audio):", "Duration:", "StartTime(Audio):"]
        self.mappingInfoLayout = QVBoxLayout()
        self.mappingInfoLayoutWidget = wrapLayoutInWidget(self.mappingInfoLayout)
        count = 0
        
        for i in range(3):
            hbox1 = QHBoxLayout()
            hbox2 = QHBoxLayout()

            for j in range(3):
                label = QLabel(self.labels[count])
                count += 1
                textBox = createQLineEdit('')
                hbox1.addWidget(label)
                hbox2.addWidget(textBox)
                
            self.mappingInfoLayout.addLayout(hbox1)
            self.mappingInfoLayout.addLayout(hbox2)
        
        return self.mappingInfoLayoutWidget




        '''
        rowLayout = QVBoxLayout()
        rowLayoWidget = wrapLayoutInWidget(rowLayout)

        markerWordEEGStartTimeWidget = self.setupMarkerWordEEGStartTimeWidget()
        #eegEndTimeEEGStartIndexEEGEndeIndexWidget = self.setupeegEndTimeEEGStartIndexEEGEndeIndexWidget()
        #audioStartIndexDurationAudioStartTimeWidget = self.setupaudioStartIndexDurationAudioStartTime()

        rowLayout.addWidget(markerWordEEGStartTimeWidget)
        #rowLayout.addWidget(eegEndTimeEEGStartIndexEEGEndeIndexWidget)
        #rowLayout.addWidget(audioStartIndexDurationAudioStartTimeWidget)

        return rowLayoWidget
        '''

    def setupMarkerWordEEGStartTimeWidget(self):
        rowLayout = QVBoxLayout()
        rowLayoWidget = wrapLayoutInWidget(rowLayout, layoutStyle=layoutStyleItems)

        columnLayout = QHBoxLayout()
        columnLayoutWidget = wrapLayoutInWidget(columnLayout, layoutStyle=layoutStyleItems)

        markerLabel = createQLabel('Marker')
        wordLabel = createQLabel('Word')
        eegStartTime = createQLabel('Start Time EEG')

        columnLayout.addWidget(markerLabel)
        columnLayout.addWidget(wordLabel)
        columnLayout.addWidget(eegStartTime)
        
        rowLayout.addWidget(columnLayoutWidget)

        columnLayout = QHBoxLayout()
        columnLayoutWidget = wrapLayoutInWidget(columnLayout, layoutStyle=layoutStyleItems)

        self.markerText = createQLineEdit('')
        self.WordText = createQLineEdit('')
        self.eegStartTimeText = createQLineEdit('')

        columnLayout.addWidget(self.markerText)
        columnLayout.addWidget(self.WordText)
        columnLayout.addWidget(self.eegStartTimeText)

        rowLayout.addWidget(columnLayoutWidget)
       
        return rowLayoWidget

    ################################################################################
    ################################  Plots  Layout ################################
    ################################################################################

    def setupPlotsLayout(self):
        plotsLayout = QHBoxLayout()
        plotsLayoutWidget = wrapLayoutInWidget(plotsLayout)

        self.eegPlotWidget = self.setupEEGPlotWidget()
        self.audioPlotWidget = self.setupAudioPlotWidget()

        plotsLayout.addWidget(self.eegPlotWidget)
        plotsLayout.addWidget(self.audioPlotWidget)

        return plotsLayoutWidget
    
    def setupAudioPlotWidget(self):
        audioPlotWidget = pg.PlotWidget(title="Audio Visualizer")
        audioPlotWidget.setBackground('g')
        audioPlotWidget.getPlotItem().showGrid(True, True)
        self.audioPlotDataItem = audioPlotWidget.plot(pen='red')
        
        return audioPlotWidget

    def setupEEGPlotWidget(self):
        eegplotWidget = pg.PlotWidget(title="EEG Activity")
        eegplotWidget.setBackground('w')
        eegplotWidget.getPlotItem().showGrid(True, True)
        self.plotDataItem = eegplotWidget.plot(pen='b')
        
        return eegplotWidget

    def updateEegPlot(self):
        eegData = np.random.normal(size=1000)
        self.plotDataItem.setData(eegData)

    ################################################################################
    ########################  Play and Stop Audio  Layout ##########################
    ################################################################################

    def setupPlayAndStopButtonsLayout(self):
        rowLayout = QHBoxLayout()
        rowLayoutWidget = wrapLayoutInWidget(rowLayout)

        self.playAudioButton = createQPushButton('Play')
        self.stopAudioButton = createQPushButton('Stop')

        rowLayout.addWidget(self.playAudioButton)
        rowLayout.addWidget(self.stopAudioButton)

        return rowLayoutWidget
    
    def closeEvent(self, event):
        self.aboutToClose.emit()
        event.accept()

    def onSaveError(self, errorMessage):
        self.saveMessageBox.accept()
        QMessageBox.critical(self, "Error", f"Failed to load EEG data: {errorMessage}")

    def showWaitingMessage(self, message):
        waitingMsgBox = QMessageBox()
        waitingMsgBox.setText(message)
        waitingMsgBox.setStandardButtons(QMessageBox.NoButton)
        waitingMsgBox.setWindowFlags(Qt.Window | Qt.CustomizeWindowHint | Qt.WindowTitleHint)
        waitingMsgBox.setWindowTitle('Processing')
        waitingMsgBox.show()
        QApplication.processEvents()
        return waitingMsgBox
    
    def onSaveFinished(self):
        self.saveMessageBox.accept()

    def setMappingTableData(self):
        data = self.eegAudioData.mappingEegEventsWithMarkers
        nRows = len(data)
        self.mappingTableWidget.setRowCount(nRows)

        for rowIndex in range(nRows):
            for colIndex in range(9):
                self.mappingTableWidget.setItem(rowIndex, colIndex, QTableWidgetItem(str(data[rowIndex][colIndex])))

        self.mappingTableWidget.verticalHeader().setSectionResizeMode(self.mappingTableWidget.verticalHeader().ResizeToContents)
        self.changeRowColors()
    def mappingDataCellClicked(self, row):
        if row != 0:
            self.previousMappingRow = row - 1
        self.currentMappingRow = row
        rowData = []
        for col in range(self.mappingTableWidget.columnCount()):
            item = self.mappingTableWidget.item(row, col)
            if item is not None:
                rowData.append(item.text())
            

        self.updateMappingInfoLayout(rowData)

    def updateMappingInfoLayout(self, rowData):
        rowData[2] = str(np.array(float(rowData[2])).astype('datetime64[s]'))
        rowData[3] = str(np.array(float(rowData[3])).astype('datetime64[s]'))
        rowData[8] = str(np.array(float(rowData[8])).astype('datetime64[s]'))
        
        widgets = extractWidgets(self.mappingInfoLayout)
        count = 0
        for widget in widgets:
            if isinstance(widget, QLineEdit):
                if count == 0:
                    self.currentTask = 0
                widget.setText(rowData[count])
                count += 1

    def nextMappingInfoLayout(self):
        rowData = []
        for col in range(self.mappingTableWidget.columnCount()):
            item = self.mappingTableWidget.item(self.currentMappingRow + 1, col)
            if item is not None:
                rowData.append(item.text())
            
        self.currentMappingRow += 1
        self.updateMappingInfoLayout(rowData)

    def previousMappingInfoLayout(self):
        if self.currentMappingRow != 0:
            rowData = []
            for col in range(self.mappingTableWidget.columnCount()):
                item = self.mappingTableWidget.item(self.currentMappingRow - 1, col)
                if item is not None:
                    rowData.append(item.text())
                
            self.currentMappingRow -= 1

            self.updateMappingInfoLayout(rowData)

    def playAudioButtion(self):
        os.makedirs(config.audioPlayDir, exist_ok=True)
        if self.subjectID and self.sessionID:
            self.saveFileDir = Path(config.bidsDir, self.subjectID.text, self.sessionID.text)
            os.makedirs(self.saveFileDir, exist_ok=True)
            self.fileName = ''
        else:
            QMessageBox.critical(self, "Error", f"Enter Subject ID and Session ID")

    def changeRowColors(self):
        color = "#FFFF00"
        for row in range(self.mappingTableWidget.rowCount()):
            item = self.mappingTableWidget.item(row, 0) 
            value = item.text()  
            if value == 'StartBlockThinking':
                color = "#FFC0CB"
            if value == 'StartBlockSaying':
                color = "#FFFF00" 
          
            for col in range(self.mappingTableWidget.columnCount()):
                item = self.mappingTableWidget.item(row, col)
                if item is not None:
                    item.setBackground(QColor(color))