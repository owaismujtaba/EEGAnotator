from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout,
    QVBoxLayout, QLabel, QPushButton, QComboBox, QFileDialog, 
    QMessageBox,  QLineEdit,  QListWidget
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QIcon,  QPixmap
from src.gui.utils import getFileNameFromPath, convertEegEventsToList, convertMarkerEventsToList, textBoxStyle, labelStyle, buttonStyle, comboBoxStyle, layoutStyle
from src.classes.eeg import EegData
from src.classes.audio import AudioData
from src.classes.eeg_audio import EegAudioData
from src.gui.mapping_display import EEGAudioApp
import config as config

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
        self.mappingDisplay = None

        self.setWindowTitle('EEG_AUDIO_Anotator')
        self.setGeometry(500, 300, 1200, 300)
        self.setWindowIcon(QIcon(config.windowIconPath))  
        self.setStyleSheet("background-color: #f0f0f0;")

        self.backgroundLabel = QLabel(self)
        self.backgroundLabel.setGeometry(0, 0, self.width(), self.height())
        pixmap = QPixmap(config.backgroundImagePath)

        self.backgroundLabel.setPixmap(pixmap)
        self.backgroundLabel.setScaledContents(True)
        self.backgroundLabel.setAlignment(Qt.AlignCenter)

        centralWidget = QWidget()
        self.setCentralWidget(centralWidget)
        self.mainLayout = QHBoxLayout()
        centralWidget.setLayout(self.mainLayout)

        self.setupLeftLayout()
        self.setupRightLayout()
        self.connectSignals()

    def setupLeftLayout(self):
        self.leftLayout = QVBoxLayout()
        self.leftLayoutWidget = self.wrapLayoutInWidget(self.leftLayout)
        self.leftLayoutWidget.setStyleSheet(layoutStyle)

        self.createFileInformationSectionForEEG()
        self.createEventInformationSectionForEEG()
        self.createChannelSelectionSectionForEEG()
        self.createVisualizationButtonForEEG()

        self.mainLayout.addWidget(self.leftLayoutWidget)

    def createFileInformationSectionForEEG(self):
        headerLabel = QLabel('<center><b><font color="#8B0000" size="5"><u> EEG (*.edf) FILE INFORMATION<u></font></b></center>')
        self.leftLayout.addWidget(headerLabel)

        #***********************************ROW 2***********************************
        self.eegFileNameLabel = QLabel('EEG (.edf) File :')
        self.eegFileNameLabel.setStyleSheet(labelStyle)
        self.eegFileNameTextbox = QLineEdit('Filename will appear here!!!')
        self.eegFileNameTextbox.setReadOnly(True)
        self.eegFileNameTextbox.setStyleSheet(textBoxStyle)
        self.eegSelectFileButton = QPushButton('Select File')
        self.eegSelectFileButton.setStyleSheet(buttonStyle)
        self.eegLoadFileButton = QPushButton('Load File')
        self.eegLoadFileButton.setStyleSheet(buttonStyle)

        rowLayout = QHBoxLayout()
        rowLayoutWidget = self.wrapLayoutInWidget(rowLayout)
        rowLayoutWidget.setStyleSheet(layoutStyle)
        rowLayout.addWidget(self.eegFileNameLabel)
        rowLayout.addWidget(self.eegFileNameTextbox)
        rowLayout.addWidget(self.eegSelectFileButton)
        rowLayout.addWidget(self.eegLoadFileButton)
        self.leftLayout.addWidget(rowLayoutWidget)

        #***********************************ROW 3***********************************
        self.eegSamplingFreqLabel = QLabel('Sampling Frequency :')
        self.eegSamplingFreqLabel.setStyleSheet(labelStyle)
        self.eegSamplingFreqText = QLineEdit('')
        self.eegSamplingFreqText.setStyleSheet(textBoxStyle)
        self.eegSamplingFreqText.setReadOnly(True)
        self.eegDurationLabel = QLabel('Duration: ')
        self.eegDurationLabel.setStyleSheet(labelStyle)
        self.eegDurationText = QLineEdit('')
        self.eegDurationText.setStyleSheet(textBoxStyle)
        self.eegDurationText.setReadOnly(True)

        rowLayout = QHBoxLayout()
        rowLayoutWidget = self.wrapLayoutInWidget(rowLayout)
        rowLayoutWidget.setStyleSheet(layoutStyle)
        rowLayout.addWidget(self.eegSamplingFreqLabel)
        rowLayout.addWidget(self.eegSamplingFreqText)
        rowLayout.addWidget(self.eegDurationLabel)
        rowLayout.addWidget(self.eegDurationText)
        self.leftLayout.addWidget(rowLayoutWidget)

        #***********************************ROW 4**********************************
        self.eegNChannelsLabel = QLabel('No. Channels :')        
        self.eegNChannelsLabel.setStyleSheet(labelStyle)
        self.eegNChannelsText = QLineEdit('')
        self.eegNChannelsText.setStyleSheet(textBoxStyle)
        self.eegNChannelsText.setReadOnly(True)
        self.eegNBadChannelsLabel = QLabel('No. bad channels')
        self.eegNBadChannelsLabel.setStyleSheet(labelStyle)
        self.eegNBadChannelsText = QLineEdit('')
        self.eegNBadChannelsText.setStyleSheet(textBoxStyle)
        self.eegNBadChannelsText.setReadOnly(True)

        rowLayout = QHBoxLayout()
        rowLayoutWidget = self.wrapLayoutInWidget(rowLayout)
        rowLayoutWidget.setStyleSheet(layoutStyle)
        rowLayout.addWidget(self.eegNChannelsLabel)
        rowLayout.addWidget(self.eegNChannelsText)
        rowLayout.addWidget(self.eegNBadChannelsLabel)
        rowLayout.addWidget(self.eegNBadChannelsText)
        self.leftLayout.addWidget(rowLayoutWidget)

        #***********************************ROW 5***********************************
        self.eegStartTimeLabel = QLabel('Start Time :')
        self.eegStartTimeLabel.setStyleSheet(labelStyle)
        self.eegStartTimeText = QLineEdit('')
        self.eegStartTimeText.setStyleSheet(textBoxStyle)
        self.eegStartTimeText.setReadOnly(True)
        self.eegEndTimeLabel = QLabel('End Time :')
        self.eegEndTimeLabel.setStyleSheet(labelStyle)
        self.eegEndTimeText = QLineEdit('')
        self.eegEndTimeText.setStyleSheet(textBoxStyle)
        self.eegEndTimeText.setReadOnly(True)

        rowLayout = QHBoxLayout()
        rowLayoutWidget = self.wrapLayoutInWidget(rowLayout)
        rowLayoutWidget.setStyleSheet(layoutStyle)
        rowLayout.addWidget(self.eegStartTimeLabel)
        rowLayout.addWidget(self.eegStartTimeText)
        rowLayout.addWidget(self.eegEndTimeLabel)
        rowLayout.addWidget(self.eegEndTimeText)
        self.leftLayout.addWidget(rowLayoutWidget)

        #***********************************ROW 5**********************************        
        self.eegNTriggersLabel = QLabel('No. Triggers :')
        self.eegNTriggersLabel.setStyleSheet(labelStyle)
        self.eegNTriggersText = QLineEdit('')
        self.eegNTriggersText.setStyleSheet(textBoxStyle)
        self.eegNTriggersText.setReadOnly(True)
        self.eegInterruptionLabel = QLabel('Interruptions Flag: ')
        self.eegInterruptionLabel.setStyleSheet(labelStyle)
        self.eegInterruptionsText = QLineEdit('')
        self.eegInterruptionsText.setStyleSheet(textBoxStyle)
        self.eegInterruptionsText.setReadOnly(True)

        rowLayout = QHBoxLayout()
        rowLayoutWidget = self.wrapLayoutInWidget(rowLayout)
        rowLayoutWidget.setStyleSheet(layoutStyle)
        rowLayout.addWidget(self.eegNTriggersLabel)
        rowLayout.addWidget(self.eegNTriggersText)
        rowLayout.addWidget(self.eegInterruptionLabel)
        rowLayout.addWidget(self.eegInterruptionsText)
        self.leftLayout.addWidget(rowLayoutWidget)
    
    def createEventInformationSectionForEEG(self):
        #***********************************ROW 6**********************************
        self.eegBadChannelsCBox = QComboBox()
        self.eegBadChannelsCBox.addItem('Bad Channels')
        self.eegBadChannelsCBox.setStyleSheet(comboBoxStyle)
        self.eegEventsCBox = QComboBox()
        self.eegEventsCBox.addItem('Event Name:       Start Time:   End Time:  Start Index:     End Index:   Duration')
        self.eegEventsCBox.setStyleSheet(comboBoxStyle)

        rowLayout = QHBoxLayout()
        rowLayout.addWidget(self.eegBadChannelsCBox)
        rowLayout.addWidget(self.eegEventsCBox)
        self.leftLayout.addLayout(rowLayout)

    def createChannelSelectionSectionForEEG(self):
        #***********************************ROW 1**********************************
        channelsLayout = QHBoxLayout()

        self.eegChannelsAvailableList = QListWidget()
        self.eegChannelsSelectedList = QListWidget()

        self.eegChannelAddBtn = QPushButton('Add >>')
        self.eegChannelAddBtn.setStyleSheet(buttonStyle)
        self.eegChannelRemoveBtn = QPushButton('<< Remove')
        self.eegChannelRemoveBtn.setStyleSheet(buttonStyle)
        self.eegChannelAddAllBtn = QPushButton('Add All >>')
        self.eegChannelAddAllBtn.setStyleSheet(buttonStyle)
        self.eegChannelRemoveAllBtn = QPushButton('<< Remove All')
        self.eegChannelRemoveAllBtn.setStyleSheet(buttonStyle)

        buttonsLayout = QVBoxLayout()
        buttonsLayout.addWidget(self.eegChannelAddBtn)
        buttonsLayout.addWidget(self.eegChannelRemoveBtn)
        buttonsLayout.addWidget(self.eegChannelAddAllBtn)
        buttonsLayout.addWidget(self.eegChannelRemoveAllBtn)
        buttonsLayout.addStretch()

        channelsLayout.addWidget(self.eegChannelsAvailableList)
        channelsLayout.addLayout(buttonsLayout)
        channelsLayout.addWidget(self.eegChannelsSelectedList)

        self.leftLayout.addLayout(channelsLayout)
    
    def createVisualizationButtonForEEG(self):
        self.visualizeEEGBtn = QPushButton('Visualize selected channels')
        self.visualizeEEGBtn.setStyleSheet(buttonStyle)
        self.leftLayout.addWidget(self.visualizeEEGBtn)


    def setupRightLayout(self):
        self.rightLayout = QVBoxLayout()
        self.rightLayoutWidget = self.wrapLayoutInWidget(self.rightLayout)
        self.rightLayoutWidget.setStyleSheet(layoutStyle)

        self.createFileInformationSectionForAudio()
        self.createEventInformationSectionForAudio()
        self.createMappingButtonForEEGAndAudio()

        self.mainLayout.addWidget(self.rightLayoutWidget)     

    def createFileInformationSectionForAudio(self):
        headerLabel = QLabel('<center><b><font color="#8B0000" size="5"><u> Audio (*.xdf) FILE INFORMATION<u></font></b></center>')
        self.rightLayout.addWidget(headerLabel)

        #***********************************ROW 2***********************************
        self.audioFileNameLabel = QLabel('EEG (.edf) File :')
        self.audioFileNameLabel.setStyleSheet(labelStyle)
        self.audioFileNameTextbox = QLineEdit('Filename will appear here!!!')
        self.audioFileNameTextbox.setReadOnly(True)
        self.audioFileNameTextbox.setStyleSheet(textBoxStyle)
        self.audioSelectFileButton = QPushButton('Select File')
        self.audioSelectFileButton.setStyleSheet(buttonStyle)
        self.audioLoadFileButton = QPushButton('Load File')
        self.audioLoadFileButton.setStyleSheet(buttonStyle)

        rowLayout = QHBoxLayout()
        rowLayoutWidget = self.wrapLayoutInWidget(rowLayout)
        rowLayoutWidget.setStyleSheet(layoutStyle)
        rowLayout.addWidget(self.audioFileNameLabel)
        rowLayout.addWidget(self.audioFileNameTextbox)
        rowLayout.addWidget(self.audioSelectFileButton)
        rowLayout.addWidget(self.audioLoadFileButton)
        self.rightLayout.addWidget(rowLayoutWidget)

        #***********************************ROW 3***********************************
        self.audioSamplingFreqLabel = QLabel('Sampling Frequency :')
        self.audioSamplingFreqLabel.setStyleSheet(labelStyle)
        self.audioSamplingFreqText = QLineEdit('')
        self.audioSamplingFreqText.setStyleSheet(textBoxStyle)
        self.audioSamplingFreqText.setReadOnly(True)
        self.audioDurationLabel = QLabel('Audio Duration: ')
        self.audioDurationLabel.setStyleSheet(labelStyle)
        self.audioDurationText = QLineEdit('')
        self.audioDurationText.setStyleSheet(textBoxStyle)
        self.audioDurationText.setReadOnly(True)

        rowLayout = QHBoxLayout()
        rowLayoutWidget = self.wrapLayoutInWidget(rowLayout)
        rowLayoutWidget.setStyleSheet(layoutStyle)
        rowLayout.addWidget(self.audioSamplingFreqLabel)
        rowLayout.addWidget(self.audioSamplingFreqText)
        rowLayout.addWidget(self.audioDurationLabel)
        rowLayout.addWidget(self.audioDurationText)
        self.rightLayout.addWidget(rowLayoutWidget)

        #***********************************ROW 4***********************************
        self.audioStartTimeLabel = QLabel('Audio Start Time :')
        self.audioStartTimeLabel.setStyleSheet(labelStyle)
        self.audioStartTimeText = QLineEdit('')
        self.audioStartTimeText.setStyleSheet(textBoxStyle)
        self.audioStartTimeText.setReadOnly(True)
        self.audioEndTimeLabel = QLabel('Audio End Time :')
        self.audioEndTimeLabel.setStyleSheet(labelStyle)
        self.audioEndTimeText = QLineEdit('')
        self.audioEndTimeText.setStyleSheet(textBoxStyle)
        self.audioEndTimeText.setReadOnly(True)

        rowLayout = QHBoxLayout()
        rowLayoutWidget = self.wrapLayoutInWidget(rowLayout)
        rowLayoutWidget.setStyleSheet(layoutStyle)
        rowLayout.addWidget(self.audioStartTimeLabel)
        rowLayout.addWidget(self.audioStartTimeText)
        rowLayout.addWidget(self.audioEndTimeLabel)
        rowLayout.addWidget(self.audioEndTimeText)
        self.rightLayout.addWidget(rowLayoutWidget)

    def createEventInformationSectionForAudio(self):

        self.audioNMarkersLabel = QLabel('No. Markers :')
        self.audioNMarkersLabel.setStyleSheet(labelStyle)
        self.audioNMarkersText = QLineEdit('')
        self.audioNMarkersText.setStyleSheet(textBoxStyle)
        self.audioNMarkersText.setReadOnly(True)
        self.audioMarkersStartLabel = QLabel('Markers Start Time :')
        self.audioMarkersStartLabel.setStyleSheet(labelStyle)
        self.audioMarkersStartText = QLineEdit('')
        self.audioMarkersStartText.setStyleSheet(textBoxStyle)
        self.audioMarkersStartText.setReadOnly(True)

        rowLayout = QHBoxLayout()
        rowLayoutWidget = self.wrapLayoutInWidget(rowLayout)
        rowLayoutWidget.setStyleSheet(layoutStyle)
        rowLayout.addWidget(self.audioNMarkersLabel)
        rowLayout.addWidget(self.audioNMarkersText)
        rowLayout.addWidget(self.audioMarkersStartLabel)
        rowLayout.addWidget(self.audioMarkersStartText)
        self.rightLayout.addWidget(rowLayoutWidget)

        #***********************************ROW 2***********************************

        self.audioMarkersEndTimeLabel = QLabel('Markers End Time :')
        self.audioMarkersEndTimeLabel.setStyleSheet(labelStyle)
        self.audioMarkersEndTimeText = QLineEdit('')
        self.audioMarkersEndTimeText.setStyleSheet(textBoxStyle)
        self.audioMarkersEndTimeText.setReadOnly(True)
        self.audioMarkersDurationLabel = QLabel('Markers Duration :')
        self.audioMarkersDurationLabel.setStyleSheet(labelStyle)
        self.audioMarkersDurationText = QLineEdit('')
        self.audioMarkersDurationText.setStyleSheet(textBoxStyle)
        self.audioMarkersDurationText.setReadOnly(True)

        rowLayout = QHBoxLayout()
        rowLayoutWidget = self.wrapLayoutInWidget(rowLayout)
        rowLayoutWidget.setStyleSheet(layoutStyle)
        rowLayout.addWidget(self.audioMarkersEndTimeLabel)
        rowLayout.addWidget(self.audioMarkersEndTimeText)
        rowLayout.addWidget(self.audioMarkersDurationLabel)
        rowLayout.addWidget(self.audioMarkersDurationText)
        self.rightLayout.addWidget(rowLayoutWidget)

        #***********************************ROW 3**********************************
        self.audioMarkersWithTimeAndAudioIndex = QComboBox()
        self.audioMarkersWithTimeAndAudioIndex.setStyleSheet(comboBoxStyle)
        self.audioMarkersWithTimeAndAudioIndex.addItem('Marker Name:   ::: Word:   ::: Time:  ::: Audio Index:')

        rowLayout = QHBoxLayout()
        rowLayout.addWidget(self.audioMarkersWithTimeAndAudioIndex)
        rowLayoutWidget = self.wrapLayoutInWidget(rowLayout)
        rowLayoutWidget.setStyleSheet(layoutStyle)
        self.rightLayout.addWidget(rowLayoutWidget)

    def createMappingButtonForEEGAndAudio(self):
        self.mappingButtonForEEGAndAudio = QPushButton('Map Audio and EEG')
        self.mappingButtonForEEGAndAudio.setStyleSheet(buttonStyle)
        self.rightLayout.addWidget(self.mappingButtonForEEGAndAudio)
 
    def connectSignals(self):
        self.eegSelectFileButton.clicked.connect(self.browseEegFile)
        self.eegLoadFileButton.clicked.connect(self.loadEdfFile)
        self.audioSelectFileButton.clicked.connect(self.browseXdfFile)
        self.audioLoadFileButton.clicked.connect(self.loadXdfFile)

        self.eegChannelAddBtn.clicked.connect(self.addItemToChannelSelectedList)
        self.eegChannelAddAllBtn.clicked.connect(self.addAllItemsToChannelSelected)
        self.eegChannelRemoveBtn.clicked.connect(self.removeItemFromChannelSelected)
        self.eegChannelRemoveAllBtn.clicked.connect(self.removeAllItemsFromChannelSelected)
        self.visualizeEEGBtn.clicked.connect(self.visualizeEegChannels)
        self.mappingButtonForEEGAndAudio.clicked.connect(self.mapEegAndAudioBasedOnTriggersAndTime)
    
    def mapEegAndAudioBasedOnTriggersAndTime(self):
        if self.eegData and self.audioData:
            self.eegAudioData = EegAudioData(self.eegData, self.audioData)
            self.hide()
            self.mappingPageViewer = EEGAudioApp(self.eegAudioData)
            self.mappingPageViewer.aboutToClose.connect(self.showMainWindow)
            self.mappingPageViewer.show()
    
    def showMainWindow(self):
        self.show()
    
    def wrapLayoutInWidget(self, layout):
        widget = QWidget()
        widget.setLayout(layout)
        return widget

    def browseEegFile(self):
        fileDialog = QFileDialog()
        filePath, _ = fileDialog.getOpenFileName(self, "Open EDF File", "", "EDF Files (*.edf)")
        if filePath:
            self.edfFilePath = filePath
            self.edfFileName = getFileNameFromPath(filePath)
            self.eegFileNameTextbox.setText(self.edfFileName)
            print(filePath)
           
    def browseXdfFile(self):
        fileDialog = QFileDialog()
        filePath, _ = fileDialog.getOpenFileName(self, "Open XDF File", "", "XDF Files (*.xdf)")
        if filePath:
            self.xdfFilePath = filePath
            self.xdfFileName = getFileNameFromPath(filePath)
            self.audioFileNameTextbox.setText(self.xdfFileName)
    
    def loadXdfFile(self):
        if self.xdfFilePath:
            self.waitingMessageBox = self.showWaitingMessage("Loading XDF data. Please wait...")
            self.loadThread = LoadAudioThread(self.xdfFilePath)
            self.loadThread.finished.connect(self.onLoadFinishedAudio)
            self.loadThread.error.connect(self.onLoadError)
            self.loadThread.start()

    def updateAudioInfo(self):
        self.audioSamplingFreqText.setText(str(self.audioData.samplingFrequency))
        self.audioDurationText.setText(str(self.audioData.audioDuration))
        self.audioStartTimeText.setText(str(self.audioData.audioStartTime))
        self.audioEndTimeText.setText(str(self.audioData.audioEndTime))
        self.audioNMarkersText.setText(str(self.audioData.nMarkers))
        self.audioMarkersStartText.setText(str(self.audioData.markersStartTime))
        self.audioMarkersEndTimeText.setText(str(self.audioData.audioEndTime))
        self.audioMarkersDurationText.setText(str(self.audioData.markersDuration))
        
        makerEvents = convertMarkerEventsToList(self.audioData.markersWordsTimestampsAudioStartIndex)
        self.audioMarkersWithTimeAndAudioIndex.addItems(makerEvents)

    def onLoadFinishedAudio(self, audioData):
        self.audioData = audioData
        self.updateAudioInfo()
        self.waitingMessageBox.accept()

    def loadEdfFile(self):
        if self.edfFilePath:
            self.waitingMessageBox = self.showWaitingMessage("Loading EEG data. Please wait...")
            self.loadThreadEeg = LoadEegThread(self.edfFilePath)
            self.loadThreadEeg.finished.connect(self.onLoadFinishedEEG)
            self.loadThreadEeg.error.connect(self.onLoadError)
            self.loadThreadEeg.start()

    def onLoadFinishedEEG(self, eegData):
        self.eegData = eegData
        self.updateEEGInfo()
        self.waitingMessageBox.accept()

    def updateEEGInfo(self):
        self.eegSamplingFreqText.setText(str(self.eegData.samplingFrequency))
        self.eegDurationText.setText(str(self.eegData.duration))
        self.eegNChannelsText.setText(str(self.eegData.nChannels))
        self.eegNBadChannelsText.setText(str(len(self.eegData.badChannels)))
        self.eegStartTimeText.setText(str(self.eegData.startTime))
        self.eegEndTimeText.setText(str(self.eegData.endTime))
        self.eegNTriggersText.setText(str(len(self.eegData.triggers)))
        self.eegInterruptionsText.setText(str(self.eegData.interruptionsCheck))
        events = convertEegEventsToList(self.eegData.events)
        self.eegEventsCBox.addItems(events)
        self.eegChannelsAvailableList.addItems(self.eegData.channelNames)

    def showWaitingMessage(self, message):
        waitingMsgBox = QMessageBox()
        waitingMsgBox.setText(message)
        waitingMsgBox.setStandardButtons(QMessageBox.NoButton)
        waitingMsgBox.setWindowFlags(Qt.Window | Qt.CustomizeWindowHint | Qt.WindowTitleHint)
        waitingMsgBox.setWindowTitle('Processing')
        waitingMsgBox.show()
        QApplication.processEvents()
        return waitingMsgBox

    def onLoadError(self, error_message):
        self.waitingMessageBox.accept()
        QMessageBox.critical(self, "Error", f"Failed to load EEG data: {error_message}")

    def addAllItemsToChannelSelected(self):
        while self.eegChannelsAvailableList.count() > 0:
            item = self.eegChannelsAvailableList.takeItem(0)
            self.eegChannelsSelectedList.addItem(item.text())

    def removeAllItemsFromChannelSelected(self):
        while self.eegChannelsSelectedList.count() > 0:
            item = self.eegChannelsSelectedList.takeItem(0)
            self.eegChannelsAvailableList.addItem(item.text())

    def addItemToChannelSelectedList(self):
        selectedItems = self.eegChannelsAvailableList.selectedItems()
        for item in selectedItems:
            self.eegChannelsSelectedList.addItem(item.text())
            self.eegChannelsAvailableList.takeItem(self.eegChannelsAvailableList.row(item))
        
    def removeItemFromChannelSelected(self):
        selectedItems = self.eegChannelsSelectedList.selectedItems()
        for item in selectedItems:
            self.eegChannelsAvailableList.addItem(item.text())
            self.eegChannelsSelectedList.takeItem(self.eegChannelsSelectedList.row(item))

    def visualizeEegChannels(self):
        selectedChannels = [self.eegChannelsSelectedList.item(i).text() for i in range(self.eegChannelsSelectedList.count())]
        plotData = self.eegData.rawData.copy()
        eegDataSelectedChannels = plotData.pick(selectedChannels)
        eegDataSelectedChannels.plot(duration=60, show_options=True)

