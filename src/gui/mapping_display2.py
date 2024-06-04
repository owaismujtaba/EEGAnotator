from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout
from PyQt5.QtWidgets import QVBoxLayout, QLabel, QTableWidget,QTableWidgetItem, QFileDialog, QMessageBox
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QIcon
import pyqtgraph as pg
import numpy as np
import config
from gui.utils import getFileNameFromPath, createQListWidget, setTextProperty
from gui.utils import  wrapLayoutInWidget, createQComboBox ,createQLabel, createQPushButton
from gui.utils import createQLineEdit,layoutStyle
from classes.eeg import EegData
from classes.audio import AudioData


class MappingWindow(QMainWindow):
    aboutToClose = pyqtSignal()
    def __init__(self):
        super().__init__()
        
        self.eegAudioData = None
        print('inside mapping')

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

    def setupLayouts(self):
        mappingsLayout = self.setupMappingsLayout()
        plotsAndOtherLayout = self.setupPlotsAndOtherLayout()

        #self.connectSignals()
        return mappingsLayout, plotsAndOtherLayout
    
    def connectSignals(self):
        pass
        #self.connectEEGSignals()
        #self.connectAudioSignals() 


    ################################################################################
    ############################## EEG Layout Functions ############################
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
    
    def setupPlotsAndOtherLayout(self):
        mainlayout = QVBoxLayout()
        

        plotsLayoutWidget = self.setupPlotsLayout()
        playAndStopButtonsLayoutWidget = self.setupPlayAndStopButtonsLayout()
        mappingInformationLayout = self.setupMappingInformationLayout()
        #saveNextPreviousDiscardLayout = self.createSaveNextPreviousDiscardLayout()
        mainlayout.addWidget(plotsLayoutWidget)
        mainlayout.addWidget(playAndStopButtonsLayoutWidget)
        mainlayout.addWidget(mappingInformationLayout)
        

        return mainlayout
    
    def setupMappingInformationLayout(self):
        rowLayout = QVBoxLayout()
        rowLayoWidget = wrapLayoutInWidget(rowLayout)

        markerWordEEGStartTimeWidget = self.setupMarkerWordEEGStartTimeWidget()
        #eegEndTimeEEGStartIndexEEGEndeIndexWidget = self.setupeegEndTimeEEGStartIndexEEGEndeIndexWidget()
        #audioStartIndexDurationAudioStartTimeWidget = self.setupaudioStartIndexDurationAudioStartTime()

        rowLayout.addWidget(markerWordEEGStartTimeWidget)
        #rowLayout.addWidget(eegEndTimeEEGStartIndexEEGEndeIndexWidget)
        #rowLayout.addWidget(audioStartIndexDurationAudioStartTimeWidget)

        return rowLayoWidget

    def setupMarkerWordEEGStartTimeWidget(self):
        rowLayout = QVBoxLayout()
        rowLayoWidget = wrapLayoutInWidget(rowLayout)

        columnLayout = QHBoxLayout()
        columnLayoutWidget = wrapLayoutInWidget(columnLayout)

        markerLabel = createQLabel('Marker')
        wordLabel = createQLabel('Word')
        eegStartTime = createQLabel('Start Time EEG')

        columnLayout.addWidget(markerLabel)
        columnLayout.addWidget(wordLabel)
        columnLayout.addWidget(eegStartTime)
        
        rowLayout.addWidget(columnLayoutWidget)

        columnLayout = QHBoxLayout()
        columnLayoutWidget = wrapLayoutInWidget(columnLayout)

        self.markerText = createQLineEdit('')
        self.WordText = createQLineEdit('')
        self.eegStartTimeText = createQLineEdit('')

        columnLayout.addWidget(self.markerText)
        columnLayout.addWidget(self.WordText)
        columnLayout.addWidget(self.eegStartTimeText)

        rowLayout.addWidget(columnLayoutWidget)
       
        return rowLayoWidget

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