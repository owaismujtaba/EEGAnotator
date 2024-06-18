from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QHeaderView
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
from classes.eeg_audio import EegAudioData
from gui.mapping_display import MappingWindow
from gui.mapping_display1 import PilotDataWindow

class LoadEegThread(QThread):
    finished = pyqtSignal(object)
    error = pyqtSignal(str)

    def __init__(self, filePath):
        super().__init__()
        self.filePath = filePath

    def run(self):
        try:
            eegData = EegData(self.filePath)
            self.finished.emit(eegData)
        except Exception as e:
            self.error.emit(str(e))

class LoadAudioThread(QThread):
    finished = pyqtSignal(object)
    error = pyqtSignal(str)

    def __init__(self, filePath):
        super().__init__()
        self.filePath = filePath

    def run(self):
        try:
            audioData = AudioData(self.filePath)
            self.finished.emit(audioData)
        except Exception as e:
            self.error.emit(str(e))



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.eegData = None
        self.audioData = None
        self.edfFilePath = None
        self.xdfFilePath = None

        self.setWindowTitle('EEG_AUDIO_Anotator')
        self.setGeometry(500, 300, 1300, 300)
        self.setWindowIcon(QIcon(config.windowIconPath)) 
        self.setStyleSheet("background-color: #f0f0f0;")
        
        centralWidget = QWidget()
        self.setCentralWidget(centralWidget)
        self.mainLayout = QHBoxLayout()
        centralWidget.setLayout(self.mainLayout)

        eegLayout, audioLayout = self.setupLayouts()

        self.mainLayout.addLayout(eegLayout, 20)  
        self.mainLayout.addLayout(audioLayout, 19)

    def setupLayouts(self):
        eegLayout = self.setupEEGLayout()
        audioLayout = self.setupAudioLayout()

        self.connectSignals()
        return eegLayout, audioLayout
    
    def connectSignals(self):
        self.connectEEGSignals()
        self.connectAudioSignals()
        self.pilotDataButton.clicked.connect(self.startPilotDataPage)

    def connectEEGSignals(self):
        self.eegSelectFileButton.clicked.connect(self.browseEEGFile)
        self.eegLoadFileButton.clicked.connect(self.loadEdfFile)
        self.eegAddChannelButton.clicked.connect(self.eegAddChannelToSelectedChannelsList)
        self.eegRemoveChannelButton.clicked.connect(self.eegRemoveChannelFromSelectedChannelsList)
        self.eegRemoveAllChannelsButton.clicked.connect(self.eegRemoveAllChannelsFromSelectedList)
        self.eegAddAllChannelsButton.clicked.connect(self.eegAddAllChannelsToSelectedChannelsList)
        self.eegVisualizeSelectedChannelsButton.clicked.connect(self.eegVisualizeSelectedChannels)
    
    def connectAudioSignals(self):
        self.audioSelectFileButton.clicked.connect(self.browseXDFFile)
        self.audioLoadFileButton.clicked.connect(self.loadXDFFile)
        self.eegAndAudioMappingButton.clicked.connect(self.loadMappingWindow)

    
    def startPilotDataPage(self,):
        self.hide()
        self.mappingPageViewer = PilotDataWindow()
        self.mappingPageViewer.aboutToClose.connect(self.showMainWindow)
        self.mappingPageViewer.show()

    ################################################################################
    ############################## EEG Layout Functions ############################
    ################################################################################


    def setupEEGLayout(self):
        mainLayout = QVBoxLayout()
        headerWidget = self.setupHeaderLayout(title='EEG (.edf) File Information')

        fileLoadingWidget = self.setupEEGFileLoadingLayout()
        fileInfoSFreqAndDurationWidget = self.setupEEGSFreqAndDurationLayout()
        goodAndBadChannels = self.setupGoodAndBadChannelsLayout()
        startAndEndTime = self.setupEEGStartAndEndTimeLayout()
        nChannelssAndInterruptionCheck = self.setupNoChannelssAndInterupptionsLayout() 
        self.eegEventsTable = self.setupEEGEventsLayout()
        visualizeEEG = self.visualiseEEGLayout()
        self.eegVisualizeSelectedChannelsButton = createQPushButton('Visualize Selected Channels')
        self.pilotDataButton = createQPushButton('Click if Pilot Experiment')


        mainLayout.addWidget(headerWidget)
        mainLayout.addWidget(fileLoadingWidget)
        mainLayout.addWidget(fileInfoSFreqAndDurationWidget)
        mainLayout.addWidget(goodAndBadChannels)
        mainLayout.addWidget(startAndEndTime)
        mainLayout.addWidget(nChannelssAndInterruptionCheck)
        mainLayout.addWidget(self.eegEventsTable)
        mainLayout.addWidget(visualizeEEG)
        mainLayout.addWidget(self.eegVisualizeSelectedChannelsButton)
        mainLayout.addWidget(self.pilotDataButton)

        return mainLayout
    
    def visualiseEEGLayout(self):
        columnLayout = QHBoxLayout()
        columnLayoutWidget = wrapLayoutInWidget(columnLayout)

        self.eegAvailableChannelsList = createQListWidget()
        buttonsWidget = self.setupButtonsForVisualation()
        self.eegSelectedChannelsList = createQListWidget()
        
        columnLayout.addWidget(self.eegAvailableChannelsList)
        columnLayout.addWidget(buttonsWidget)
        columnLayout.addWidget(self.eegSelectedChannelsList)

        return columnLayoutWidget
    
    def setupButtonsForVisualation(self):
        rowLayout = QVBoxLayout()
        rowLayoutWidget = wrapLayoutInWidget(rowLayout)

        self.eegAddChannelButton = createQPushButton('Add >>')
        self.eegRemoveChannelButton = createQPushButton('Remove <<')
        self.eegAddAllChannelsButton = createQPushButton('Add All >>')
        self.eegRemoveAllChannelsButton = createQPushButton('Remove All <<')

        rowLayout.addWidget(self.eegAddChannelButton)
        rowLayout.addWidget(self.eegRemoveChannelButton)
        rowLayout.addWidget(self.eegAddAllChannelsButton)
        rowLayout.addWidget(self.eegRemoveAllChannelsButton)

        return rowLayoutWidget

    def setupEEGEventsLayout(self):
        eegTableWidget = QTableWidget()
        eegTableWidget.setStyleSheet(layoutStyle)
        eegTableWidget.setRowCount(0)
        eegTableWidget.setColumnCount(6)
        headers = ["Action", "Start Time", "End Time", "Start Index", "End Index", "Duration"]
        eegTableWidget.setHorizontalHeaderLabels(headers)
        header = eegTableWidget.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        eegTableWidget.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)


        return eegTableWidget

    def setupNoChannelssAndInterupptionsLayout(self):
        rowLayout = QHBoxLayout()
        rowLayoutWidget = wrapLayoutInWidget(rowLayout)

        noChannelsLabel = createQLabel('No. Channels :')
        self.eegNoChannelsText = createQLineEdit('')
        interruptionsCheck = createQLabel('Interruptions Check ')
        self.eegInterruptionsCheck = createQLineEdit('')

        rowLayout.addWidget(noChannelsLabel)
        rowLayout.addWidget(self.eegNoChannelsText)
        rowLayout.addWidget(interruptionsCheck)
        rowLayout.addWidget(self.eegInterruptionsCheck)

        return rowLayoutWidget

    def setupEEGStartAndEndTimeLayout(self):
        rowLayout = QHBoxLayout()
        rowLayoutWidget = wrapLayoutInWidget(rowLayout)

        eegStartTimeLabel = createQLabel('Start Time :')
        self.eegStartTimeText = createQLineEdit('')
        eegEndTimeLabel = createQLabel('End Time: ')
        self.eegEndTimeText = createQLineEdit('')

        rowLayout.addWidget(eegStartTimeLabel)
        rowLayout.addWidget(self.eegStartTimeText)
        rowLayout.addWidget(eegEndTimeLabel)
        rowLayout.addWidget(self.eegEndTimeText)

        return rowLayoutWidget
    
    def setupGoodAndBadChannelsLayout(self):
        rowLayout = QHBoxLayout()
        rowLayoutWidget = wrapLayoutInWidget(rowLayout)
        
        self.eegGoodChannelsCombobox = createQComboBox('Good Channels')
        self.eegBadChannelsCombobox = createQComboBox('Bad Channels')

        rowLayout.addWidget(self.eegGoodChannelsCombobox)
        rowLayout.addWidget(self.eegBadChannelsCombobox)

        return rowLayoutWidget
    
    def setupEEGFileLoadingLayout(self):
        rowLayout = QHBoxLayout()
        rowLayoutWidget = wrapLayoutInWidget(rowLayout)

        eegFileNameLabel = createQLabel('EEG (.edf) File')
        self.eegFileNameTextbox = createQLineEdit('Filename will appear here!!!')
        self.eegSelectFileButton = createQPushButton('Select File')
        self.eegLoadFileButton = createQPushButton('Load File')

        rowLayout.addWidget(eegFileNameLabel)
        rowLayout.addWidget(self.eegFileNameTextbox)
        rowLayout.addWidget(self.eegSelectFileButton)
        rowLayout.addWidget(self.eegLoadFileButton)

        return rowLayoutWidget
    
    def setupEEGSFreqAndDurationLayout(self):
        rowLayout = QHBoxLayout()
        rowLayoutWidget = wrapLayoutInWidget(rowLayout)

        eegSamplingFreqLabel = createQLabel('Sampling Frequency :')
        self.eegSamplingFreqText = createQLineEdit('')
        eegDurationLabel = createQLabel('Duration: ')
        self.eegDurationText = createQLineEdit('')
        

        rowLayout.addWidget(eegSamplingFreqLabel)
        rowLayout.addWidget(self.eegSamplingFreqText)
        rowLayout.addWidget(eegDurationLabel)
        rowLayout.addWidget(self.eegDurationText)

        return rowLayoutWidget


    ################################################################################
    ############################ Audio Layout Functions ############################
    ################################################################################


    def setupAudioLayout(self):
        mainLayout = QVBoxLayout()
        headerWidget = self.setupHeaderLayout(title='AUDIO (.xdf) File Information')
        fileLoadingWidget = self.setupAudioFileLoadingLayout()
        audioSamplingFreqAndDurationWidget = self.setupAudioSamplingFreqAndDurationLayout()
        audioStartAndEndTimeWidget = self.setupAudioStartAndEndTimeLayout()
        markersStartAndEndTimeWidget = self.setupMarkersStartAndEndTimeLayout()
        nMarkersAndDurationWidget = self.setupNoMarkersAndDurationLayout() 
        self.audioAndMarkersBundledTable = self.setupAudioAnadMarkersBundledTableLayout()
        self.eegAndAudioMappingButton = createQPushButton('Map Audio and EEG Data (Using Triggers & Time)')

        mainLayout.addWidget(headerWidget)
        mainLayout.addWidget(fileLoadingWidget)
        mainLayout.addWidget(audioSamplingFreqAndDurationWidget)
        mainLayout.addWidget(audioStartAndEndTimeWidget)
        mainLayout.addWidget(markersStartAndEndTimeWidget)
        mainLayout.addWidget(nMarkersAndDurationWidget)
        mainLayout.addWidget(self.audioAndMarkersBundledTable)
        mainLayout.addWidget(self.eegAndAudioMappingButton)

        return mainLayout
    
    def setupAudioAnadMarkersBundledTableLayout(self):
        audioMarkersBundledTable = QTableWidget()
        audioMarkersBundledTable.setStyleSheet(layoutStyle)
        audioMarkersBundledTable.setRowCount(0)
        audioMarkersBundledTable.setColumnCount(4)

        headers = ['Marker and Action', 'Word', 'Marker Time', 'Audio Time']
        audioMarkersBundledTable.setHorizontalHeaderLabels(headers)

        header = audioMarkersBundledTable.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        audioMarkersBundledTable.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

        return audioMarkersBundledTable

    def setupNoMarkersAndDurationLayout(self):
        rowLayout = QHBoxLayout()
        rowLayoutWidget = wrapLayoutInWidget(rowLayout)

        nMarkersLabel = createQLabel('No. of Markers:')
        self.audioNoMarkersText = createQLineEdit('')
        markersDurationLabel = createQLabel('Markers ::: Duration :')
        self.audioMarkersDurationText = createQLineEdit('')

        rowLayout.addWidget(nMarkersLabel)
        rowLayout.addWidget(self.audioNoMarkersText)
        rowLayout.addWidget(markersDurationLabel)
        rowLayout.addWidget(self.audioMarkersDurationText)

        return rowLayoutWidget

    def setupAudioFileLoadingLayout(self):
        rowLayout = QHBoxLayout()
        rowLayoutWidget = wrapLayoutInWidget(rowLayout)

        audioFileNameLabel = createQLabel('Audio (.xdf) File')
        self.audioFileNameTextbox = createQLineEdit('Filename will appear here!!!')
        self.audioSelectFileButton = createQPushButton('Select File')
        self.audioLoadFileButton = createQPushButton('Load File')

        rowLayout.addWidget(audioFileNameLabel)
        rowLayout.addWidget(self.audioFileNameTextbox)
        rowLayout.addWidget(self.audioSelectFileButton)
        rowLayout.addWidget(self.audioLoadFileButton)

        return rowLayoutWidget
    
    def setupAudioSamplingFreqAndDurationLayout(self):
        rowLayout = QHBoxLayout()
        rowLayoutWidget = wrapLayoutInWidget(rowLayout)

        audioSamplingFreqLabel = createQLabel('Sampling Frequency :')
        self.audioAudioSamplingFreqText = createQLineEdit('')
        audioDurationLabel = createQLabel('Audio ::: Duration :')
        self.audioAudioDurationText = createQLineEdit('')

        rowLayout.addWidget(audioSamplingFreqLabel)
        rowLayout.addWidget(self.audioAudioSamplingFreqText)
        rowLayout.addWidget(audioDurationLabel)
        rowLayout.addWidget(self.audioAudioDurationText)

        return rowLayoutWidget

    def setupAudioStartAndEndTimeLayout(self):
        rowLayout = QHBoxLayout()
        rowLayoutWidget = wrapLayoutInWidget(rowLayout)
        
        audioStartTimeLabel = createQLabel('Audio ::: Start Time: ')
        self.audioAudioStartTimeText = createQLineEdit('')
        audioEndTimeLabel  = createQLabel('Audio ::: End Time :')
        self.audioAudioEndTimeText = createQLineEdit('')

        rowLayout.addWidget(audioStartTimeLabel)
        rowLayout.addWidget(self.audioAudioStartTimeText)
        rowLayout.addWidget(audioEndTimeLabel)
        rowLayout.addWidget(self.audioAudioEndTimeText)

        return rowLayoutWidget

    def setupMarkersStartAndEndTimeLayout(self):
        rowLayout = QHBoxLayout()
        rowLayoutWidget = wrapLayoutInWidget(rowLayout)
        
        markersStartTimeLabel = createQLabel('Markers ::: Start Time: ')
        self.audioMarkersStartTimeText = createQLineEdit('')
        markersEndTimeLabel  = createQLabel('Markers ::: End Time :')
        self.audioMarkersEndTimeText = createQLineEdit('')

        rowLayout.addWidget(markersStartTimeLabel)
        rowLayout.addWidget(self.audioMarkersStartTimeText)
        rowLayout.addWidget(markersEndTimeLabel)
        rowLayout.addWidget(self.audioMarkersEndTimeText)

        return rowLayoutWidget




    ################################################################################
    ############################# EEG Related Functions ############################
    ################################################################################

    def browseEEGFile(self):
        fileDialog = QFileDialog()
        filePath, _ = fileDialog.getOpenFileName(self, "Open EDF File", "", "EDF Files (*.edf)")
        if filePath:
            self.edfFilePath = filePath
            self.edfFileName = getFileNameFromPath(filePath)
            self.eegFileNameTextbox.setText(self.edfFileName)
            

    def loadEdfFile(self):
        if self.edfFilePath:
            self.waitingMessageBox = self.showWaitingMessage("Loading EEG data. Please wait...")
            self.loadThreadEeg = LoadEegThread(self.edfFilePath)
            self.loadThreadEeg.finished.connect(self.onLoadFinishedEEG)
            self.loadThreadEeg.error.connect(self.onLoadError)
            self.loadThreadEeg.start()

    def onLoadFinishedEEG(self, eegData):
        self.eegData = eegData
        self.updateEEGInformation()
        self.waitingMessageBox.accept()    

    def updateEEGInformation(self):
        setTextProperty(self.eegSamplingFreqText, self.eegData.samplingFrequency)
        setTextProperty(self.eegDurationText, self.eegData.duration)
        setTextProperty(self.eegNoChannelsText, self.eegData.nChannels)
        setTextProperty(self.eegInterruptionsCheck, self.eegData.interruptionsCheck)
        setTextProperty(self.eegStartTimeText, self.eegData.startTime)
        setTextProperty(self.eegEndTimeText, self.eegData.endTime)
        self.eegGoodChannelsCombobox.addItems(self.eegData.goodChannels)
        self.eegBadChannelsCombobox.addItems(self.eegData.badChannels)
        self.eegAvailableChannelsList.addItems(self.eegData.channelNames)
        self.eegAddDataToEventsTable()
    
    def eegRemoveAllChannelsFromSelectedList(self):
        while self.eegSelectedChannelsList.count() > 0:
            item = self.eegSelectedChannelsList.takeItem(0)
            self.eegAvailableChannelsList.addItem(item.text())

    def eegAddAllChannelsToSelectedChannelsList(self):
        while self.eegAvailableChannelsList.count() > 0:
            item = self.eegAvailableChannelsList.takeItem(0)
            self.eegSelectedChannelsList.addItem(item.text())

    def eegRemoveChannelFromSelectedChannelsList(self):
        selectedChannels = self.eegSelectedChannelsList.selectedItems()
        for channel in selectedChannels:
            self.eegAvailableChannelsList.addItem(channel.text())
            self.eegSelectedChannelsList.takeItem(self.eegSelectedChannelsList.row(channel))
    
    def eegAddChannelToSelectedChannelsList(self):
        selectedChannels = self.eegAvailableChannelsList.selectedItems()
        for channel in selectedChannels:
            self.eegSelectedChannelsList.addItem(channel.text())
            self.eegAvailableChannelsList.takeItem(self.eegAvailableChannelsList.row(channel))

    def eegVisualizeSelectedChannels(self):
        if self.eegData:
            selectedChannels = [self.eegSelectedChannelsList.item(i).text() for i in range(self.eegSelectedChannelsList.count())]
            plotData = self.eegData.rawData.copy()
            eegDataSelectedChannels = plotData.pick(selectedChannels)
            eegDataSelectedChannels.plot(duration=60, show_options=True)

    def eegAddDataToEventsTable(self):
        data = self.eegData.events
        nRows = len(data)
        self.eegEventsTable.setRowCount(nRows)
        for rowIndex in range(nRows):
            for colIndex in range(6):
                self.eegEventsTable.setItem(rowIndex, colIndex, QTableWidgetItem(str(data[rowIndex][colIndex])))



    ################################################################################
    ############################ Audio Related Functions ###########################
    ################################################################################
    
    def onLoadFinishedAudio(self, audioData):
        self.audioData = audioData
        self.updateAudioInformation()
        self.waitingMessageBox.accept()


    def updateAudioInformation(self):
        setTextProperty(self.audioAudioSamplingFreqText, self.audioData.samplingFrequency)
        setTextProperty(self.audioAudioDurationText, self.audioData.audioDuration)
        setTextProperty(self.audioAudioStartTimeText, self.audioData.audioStartTime )
        setTextProperty(self.audioAudioEndTimeText, self.audioData.audioEndTime)
        setTextProperty(self.audioMarkersStartTimeText, self.audioData.markersStartTime)
        #setTextProperty(self.audioMarkersEndTimeText, self.audioData.)
        setTextProperty(self.audioNoMarkersText, self.audioData.nMarkers)
        setTextProperty(self.audioMarkersDurationText, self.audioData.markersDuration)
        self.audioAddDataToMarkersBundledTable()

    def browseXDFFile(self):
        fileDialog = QFileDialog()
        filePath, _ = fileDialog.getOpenFileName(self, "Open XDF File", "", "XDF Files (*.xdf)")
        if filePath:
            self.xdfFilePath = filePath
            self.xdfFileName = getFileNameFromPath(filePath)
            self.audioFileNameTextbox.setText(self.xdfFileName)
    
    def loadXDFFile(self):
        self.audioData = None
        if self.xdfFilePath:
            self.waitingMessageBox = self.showWaitingMessage("Loading XDF data. Please wait...")
            self.loadThread = LoadAudioThread(self.xdfFilePath)
            self.loadThread.finished.connect(self.onLoadFinishedAudio)
            self.loadThread.error.connect(self.onLoadError)
            self.loadThread.start()

    def audioAddDataToMarkersBundledTable(self):
        data = self.audioData.markersWordsTimestampsAudioStartIndex
        nRows = len(data)
        self.audioAndMarkersBundledTable.setRowCount(nRows)
        for rowIndex in range(nRows):
            for colIndex in range(4):
                self.audioAndMarkersBundledTable.setItem(rowIndex, colIndex, QTableWidgetItem(str(data[rowIndex][colIndex])))
        self.audioAndMarkersBundledTable.verticalHeader().setSectionResizeMode(self.audioAndMarkersBundledTable.verticalHeader().ResizeToContents)


    def loadMappingWindow(self):
        self.eegAudioData = EegAudioData(self.eegData, self.audioData)
        self.hide()
        self.mappingPageViewer = MappingWindow(self.eegAudioData)
        self.mappingPageViewer.aboutToClose.connect(self.showMainWindow)
        self.mappingPageViewer.show()


    ################################################################################
    ################################ Common Functions ###############################
    ################################################################################

    def setupHeaderLayout(self, title):
        rowLayout = QVBoxLayout()
        rowLayoutWidget = wrapLayoutInWidget(rowLayout)

        styleTitle = f'<center><b><font color="#000080" size="8">{title} </font></b></center>'
        headerWidget = QLabel(styleTitle)
        rowLayout.addWidget(headerWidget)
        return rowLayoutWidget

    def showMainWindow(self):
        self.show()
    
    def onLoadError(self, error_message):
        self.waitingMessageBox.accept()
        QMessageBox.critical(self, "Error", f"Failed to load EEG data: {error_message}")

    def showWaitingMessage(self, message):
        waitingMsgBox = QMessageBox()
        waitingMsgBox.setText(message)
        waitingMsgBox.setStandardButtons(QMessageBox.NoButton)
        waitingMsgBox.setWindowFlags(Qt.Window | Qt.CustomizeWindowHint | Qt.WindowTitleHint)
        waitingMsgBox.setWindowTitle('Processing')
        waitingMsgBox.show()
        QApplication.processEvents()
        return waitingMsgBox

    
   
        
        
    
    
    
