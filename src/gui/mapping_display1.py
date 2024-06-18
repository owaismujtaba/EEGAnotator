from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QHeaderView
from PyQt5.QtWidgets import QVBoxLayout, QLabel,QLineEdit ,QTableWidget,QTableWidgetItem, QFileDialog, QMessageBox
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QUrl
from PyQt5.QtGui import QIcon, QColor
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
import pyqtgraph as pg
import numpy as np
from scipy.io.wavfile import write
import soundfile as sf
import json
import pandas as pd
import config
from gui.utils import getRowBackgroundColorFromTable, layoutStyleItems, getFileNameFromPath
from gui.utils import  wrapLayoutInWidget, createQLabel, createQPushButton, createQComboBox
from gui.utils import createQLineEdit,layoutStyle, extractWidgets, extractRowDataFromTable
from classes.eeg import EegData
from classes.audio import AudioData
import config
import os
from pathlib import Path
import pyxdf
class SaveWorker(QThread):
    finished = pyqtSignal()
    error = pyqtSignal(str)
    def __init__(self, app):
        super().__init__()
        self.app = app

    def run(self):
        try:
            saveDir = self.app.subjectAndSessionDir
            self.eegFileNameWithPath = Path(saveDir, f'{self.app.fullFilePathBidsFormat}.fif')
            self.sideCarJsonFileNameWithPath = Path(saveDir, f'{self.app.fullFilePathBidsFormat}.json')
            self.audioFileNameWithPath = Path(saveDir, f'{self.app.fullFilePathBidsFormat}.wav')
            self.eventsFileNameWithPath = Path(saveDir, f'{self.app.fullFilePathBidsFormat}.tsv')
            self.saveFiles()
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))

    def saveFiles(self):
        print('Saving Files')
        self.saveSideCar()
        self.saveAudioFile()
        self.saveEventsFile()
        self.saveEEGFile()
        
    def saveEEGFile(self):
        filePath = self.eegFileNameWithPath
        self.app.eegSampleData.save(filePath, overwrite=True)

    def saveEventsFile(self):
        filePath = self.eventsFileNameWithPath
        eventsData = { "onset": [self.app.eegStartTime], "duration": [self.app.eegDuration], "trial_type": [self.app.currentBlock]}
        eventsData = pd.DataFrame(eventsData)
        eventsData.to_csv(filePath, sep='\t', index=False)

    def saveAudioFile(self):
        filePath = self.audioFileNameWithPath
        write(filePath, int(self.app.audioSamplingRate), self.app.audioSampleData)
    
    def saveSideCar(self):
        jsonMetaData = {}
        filepath = self.sideCarJsonFileNameWithPath

        jsonMetaData['TaskName'] = self.app.currentActivity
        jsonMetaData['Modality'] = self.app.currentBlock
        jsonMetaData['BlackName'] = self.app.currentTask
        jsonMetaData['PatientID'] = self.app.subjectID.text()
        jsonMetaData['SessionID'] = self.app.sessionID.text()
        jsonMetaData['Word'] = self.app.currentWord
        jsonMetaData['EEGSamplingFrequency'] = self.app.eegSamplingRate
        jsonMetaData['AudioSamplingFrequency'] = self.app.audioSamplingRate
        jsonMetaData['EEGStartTime'] = self.app.eegStartTime
        jsonMetaData['EEGEndTime'] = self.app.eegEndTime
        jsonMetaData['AudioStartTime'] = self.app.audioStartTime
        jsonMetaData['EEGStartIndex'] = self.app.eegStartIndex
        jsonMetaData['EEGEndIndex'] = self.app.eegEndIndex
        jsonMetaData['AudioStartIndex'] = self.app.audioStartIndex
        jsonMetaData['AudioEndIndex'] = self.app.audioEndIndex
        jsonMetaData['EEGDuration'] = self.app.eegDuration
        jsonMetaData['EEGReference'] = 'n/a'
        jsonMetaData['EEGChannelCount'] = self.app.eegAudioData.eegData.nChannels
        jsonMetaData['GoodChannels'] = self.app.eegAudioData.eegData.goodChannels
        jsonMetaData['BadChannels'] = self.app.eegAudioData.eegData.badChannels
        
        
        with open(filepath, 'w') as jsonFile:
            json.dump(jsonMetaData, jsonFile, indent=4)


class LoadXDFThread(QThread):
    finished = pyqtSignal(object)
    error = pyqtSignal(str)

    def __init__(self, filePath):
        super().__init__()
        self.filePath = filePath

    def run(self):
        try:
            xdf = pyxdf.load_xdf(self.filePath)
            self.finished.emit(xdf)
        except Exception as e:
            self.error.emit(str(e))


class PilotDataWindow(QMainWindow):
    aboutToClose = pyqtSignal()
    def __init__(self):
        super().__init__()
        self.xdfFilePath = None
        self.setWindowTitle('Pilot Experiment')
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
        #self.setMappingTableData()

        #self.timer = QTimer()
        #self.timer.timeout.connect(self.updateAudioPlot)
        #self.audioIndex = 0

        #self.mediaPlayer = QMediaPlayer()
    
    def setupLayouts(self):
        mappingsLayout = self.setupMappingsLayout()
        plotsAndOtherLayout = self.setupPlotsAndOtherLayout()
        self.connectSignals()
        
        return mappingsLayout, plotsAndOtherLayout

    def connectSignals(self):
        self.connectMappingsSignals()
        self.connectAudioSignals() 
        self.connectPreviousNextSaveDiscardSignals()
        self.connectSaveBIDSSignals()

    def connectMappingsSignals(self):
        self.mappingTableWidget.cellClicked.connect(self.mappingDataCellClicked)
        self.xdfSelectFileButton.clicked.connect(self.browseXDFFile)
        self.xdfLoadFileButton.clicked.connect(self.loadXDFFile)
    
    def connectAudioSignals(self):
        self.playAudioButton.clicked.connect(self.playAudioFile)
        self.stopAudioButton.clicked.connect(self.stopAudioButtonFunction)

    def connectPreviousNextSaveDiscardSignals(self):
        self.previousButton.clicked.connect(self.previousMappingInfoLayout)
        self.nextButton.clicked.connect(self.nextMappingInfoLayout)
        self.discardButton.clicked.connect(self.nextMappingInfoLayout)

    def connectSaveBIDSSignals(self):
        self.saveButton.clicked.connect(self.saveFilesInBIDSFormat)
        self.saveAllMappingsButton.clicked.connect(self.saveeAllFilesInBIDSFormat)
 
    
    ################################################################################
    #############################  Mappings Table Layout ###########################
    ################################################################################

    def setupMappingsLayout(self):
        mainLayout = QVBoxLayout()
        fileUplodalayoutWidget = self.setupXdfFileLoadingLayout()
        self.mappingTableWidget = QTableWidget()
        self.mappingTableWidget.setStyleSheet(layoutStyle)
        self.mappingTableWidget.setRowCount(0)
        self.mappingTableWidget.setColumnCount(9)
        headers = ["activity", "task", "word",  "eegStartIndex", "eegEndIndex","eegDuration", "audioStartIndex", "audioStartIndex","audioDuration"]
        self.mappingTableWidget.setHorizontalHeaderLabels(headers)
        header = self.mappingTableWidget.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        self.mappingTableWidget.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        mainLayout.addWidget(fileUplodalayoutWidget)
        mainLayout.addWidget(self.mappingTableWidget)
        
        return mainLayout
        
    def setupXdfFileLoadingLayout(self):
        rowLayout = QHBoxLayout()
        rowLayoutWidget = wrapLayoutInWidget(rowLayout)

        audioFileNameLabel = createQLabel('XDF (.xdf) File')
        self.xdfFilenameTextBox = createQLineEdit('Filename will appear here!!!')
        self.xdfSelectFileButton = createQPushButton('Select File')
        self.xdfLoadFileButton = createQPushButton('Load File')

        rowLayout.addWidget(audioFileNameLabel)
        rowLayout.addWidget(self.xdfFilenameTextBox)
        rowLayout.addWidget(self.xdfSelectFileButton)
        rowLayout.addWidget(self.xdfLoadFileButton)

        return rowLayoutWidget
        
    def browseXDFFile(self):
        fileDialog = QFileDialog()
        filePath, _ = fileDialog.getOpenFileName(self, "Open XDF File", "", "XDF Files (*.xdf)")
        if filePath:
            self.xdfFilePath = filePath
            self.xdfFileName = getFileNameFromPath(filePath)
            self.xdfFilenameTextBox.setText(self.xdfFileName)
    
    def loadXDFFile(self):
        self.xdfData = None
        if self.xdfFilePath:
            self.waitingMessageBox = self.showWaitingMessage("Loading XDF data. Please wait...")
            self.loadThread = LoadXDFThread(self.xdfFilePath)
            self.loadThread.finished.connect(self.onLoadFinishedXDF)
            self.loadThread.error.connect(self.onLoadError)
            self.loadThread.start()
    ################################################################################
    #############################  Plots and Other Layout ##########################
    ################################################################################
    def onLoadFinishedXDF(self, xdfData):
        self.xdfData = xdfData
        self.updateMappingInformation()
        #self.waitingMessageBox.accept()

    def updateMappingInformation():
        self.triggersTimestamps = self.xdfData[0][1]['time_stamps']
        self.triggers = self.xdfData[0][1]['time_series']
        self.audio = self.xdfData[0][3]['time_series']
        self.audioTimestamps = self.xdfData[0][3]['time_stamps']
        self.eegData = self.xdfData[0][2]['time_series']
        self.eegTimestamps = self.xdfData[0][2]['time_stamps']
        
    def setupPlotsAndOtherLayout(self):
        mainlayout = QVBoxLayout()
        

        plotsLayoutWidget = self.setupPlotsLayout()
        playAndStopButtonsLayoutWidget = self.setupPlayAndStopButtonsLayout()
        mappingInformationLayoutWidget = self.setupMappingInformationLayout()
        bidsInfoLayoutWidget = self.setupBIDSInfoLayout()
        saveNextPreviousDiscardLayoutWidget = self.setupSaveNextPreviousDiscardLayout()
        saveAllMappingsLayoutWidget = self.setupSaveAllMappingsLayout()
        
        mainlayout.addWidget(plotsLayoutWidget)
        mainlayout.addWidget(playAndStopButtonsLayoutWidget)
        mainlayout.addWidget(mappingInformationLayoutWidget)
        mainlayout.addWidget(bidsInfoLayoutWidget)
        mainlayout.addWidget(saveNextPreviousDiscardLayoutWidget)
        mainlayout.addWidget(saveAllMappingsLayoutWidget)
       

        return mainlayout

    def setupSaveAllMappingsLayout(self):
        rowLayout = QHBoxLayout()
        rowLayoWidget = wrapLayoutInWidget(rowLayout)

        self.saveAllMappingsButton = createQPushButton('Save All')
        rowLayout.addWidget(self.saveAllMappingsButton)

        return rowLayoWidget
    
    def setupBIDSInfoLayout(self):
        rowLayout = QHBoxLayout()
        rowLayoWidget = wrapLayoutInWidget(rowLayout)


        subjectID = createQLabel('PatientID: ')
        self.subjectID = createQLineEdit('', enable=False)
        sessionID = createQLabel('Session No.')
        self.sessionID = createQLineEdit('', enable=False)
        taskTypeLabel = createQLabel('Task Type')
        self.taskType = createQComboBox('PictureNaming')
        self.taskType.addItem('VCV')


        rowLayout.addWidget(subjectID)
        rowLayout.addWidget(self.subjectID)
        rowLayout.addWidget(sessionID)
        rowLayout.addWidget(self.sessionID)
        rowLayout.addWidget(taskTypeLabel)
        rowLayout.addWidget(self.taskType)

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

    def setMappingTableData(self):
        data = self.eegAudioData.mappingEegEventsWithMarkers
        nRows = len(data)
        self.mappingTableWidget.setRowCount(nRows)
        insertRowCount = 0
        for rowIndex in range(nRows):
            blockName = data[rowIndex][0]
            for colIndex in range(9):
                if colIndex == 0:
                    value = str(data[rowIndex][colIndex])
                    if 'EndReading' in value:
                        value = 'ITI'
                    elif 'EndSaying' in value:
                        value = 'Fixation'
                    else:
                        value = str(data[rowIndex][colIndex])
                else:
                    value = str(data[rowIndex][colIndex])
            
                self.mappingTableWidget.setItem(insertRowCount, colIndex, QTableWidgetItem(value))
            insertRowCount += 1
            if 'Block' in blockName:
                marker, word = 'Fixation', '.'
                eegStartTime, eegEndTime = data[rowIndex+1][2]-2, data[rowIndex+1][2]
                eegStartIndex, eegEndIndex =  data[rowIndex+1][4]-1024,  data[rowIndex+1][4]
                audioStartIndex, duration =  data[rowIndex+1][6]-44100*2, 1024
                audioStartTime = data[rowIndex+1][8]-2
                newRow = [marker, word, eegStartTime, eegEndTime, eegStartIndex, eegEndIndex, audioStartIndex, duration, audioStartTime ]
                for index in range(9):
                    self.mappingTableWidget.setItem(insertRowCount, index, QTableWidgetItem(str(newRow[index])))
                print(newRow)
                insertRowCount += 1
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
        rowData = extractRowDataFromTable(self.mappingTableWidget, self.currentMappingRow +1)         
        self.currentMappingRow += 1
        self.updateMappingInfoLayout(rowData)

    def previousMappingInfoLayout(self):
        if self.currentMappingRow != 0:
            rowData = extractRowDataFromTable(self.mappingTableWidget, self.currentMappingRow -1)     
            self.currentMappingRow -= 1
            self.updateMappingInfoLayout(rowData)

    def playAudioFile(self):
        os.makedirs(config.audioPlayDir, exist_ok=True)
        self.extractAudioForPlay()

    def initialiseMappingInfo(self):
        rowData = extractRowDataFromTable(self.mappingTableWidget, self.currentMappingRow)
        self.audioStartIndex = int(rowData[6])
        self.marker = rowData[0]
        self.word = rowData[1]
        self.eegStartTime = float(rowData[2])
        self.eegEndTime = float(rowData[3])
        self.eegStartIndex = int(rowData[4])
        self.eegEndIndex = int(rowData[5])
        self.audioStartIndex = int(rowData[6])
        self.eegDuration = int(rowData[7])
        self.audioStartTime = float(rowData[8])
        
    def extractAudioForPlay(self):
        self.initialiseMappingInfo()
        self.audioEndIndex = self.audioStartIndex + int((self.eegDuration / self.eegSamplingRate) * self.audioSamplingRate)
        self.audioSampleData = self.eegAudioData.audioData.audio[self.audioStartIndex: self.audioEndIndex].reshape(-1, 1)
        name = f'{self.audioStartIndex}.wav'
        filePathWithName = Path(config.audioPlayDir, name)
        print(filePathWithName)
        if not os.path.exists(filePathWithName):
            write(filePathWithName, int(self.eegAudioData.audioData.samplingFrequency), self.audioSampleData)
        self.audioData, self.sampleRate = sf.read(filePathWithName, dtype='int16')
        self.audioIndex = 0
        mediaContent = QMediaContent(QUrl.fromLocalFile(str(filePathWithName)))
        self.mediaPlayer.setMedia(mediaContent)
        self.mediaPlayer.play()
        self.timer.start(30)

    def stopAudioButtonFunction(self):
        self.mediaPlayer.stop()
        self.timer.stop()

    def updateAudioPlot(self):
        if self.audioSampleData is not None:
            chunkSize = 1024
            endIndex = self.audioIndex + chunkSize
            if endIndex >= len(self.audioSampleData):
                endIndex = len(self.audioSampleData)
                self.timer.stop()
            dataChunk = self.audioData[self.audioIndex:endIndex]
            self.audioPlotDataItem.setData(dataChunk)
            self.audioIndex = endIndex

    def extractDataForCurrentRun(self):
        self.initialiseMappingInfo()
        self.audioEndIndex = self.audioStartIndex + int((self.eegDuration / self.eegSamplingRate) * self.audioSamplingRate)
        self.audioSampleData = self.eegAudioData.audioData.audio[self.audioStartIndex: self.audioEndIndex].reshape(-1, 1)
        self.eegSampleData = self.eegAudioData.eegData.rawData.copy().crop(
            tmin = self.eegStartIndex/self.eegSamplingRate,
            tmax = self.eegEndIndex/self.eegSamplingRate
        )
        self.channelNames = self.eegAudioData.eegData.channelNames

    def saveFilesInBIDSFormat(self):
        if self.subjectID.text() != '' and self.sessionID.text() != '':
            self.saveMessageBox = self.showWaitingMessage('Saving files')
            self.saveMessageBox.setWindowTitle("Saving")
            self.setupDirsForSavingFiles()
            self.setupFilePathsForSavingFilesBIDSFormat()
            self.extractDataForCurrentRun()
            self.saveWorker = SaveWorker(self)
            self.saveWorker.finished.connect(self.onSaveFinished)
            self.saveWorker.error.connect(self.onSaveError)
            self.runCount += 1
            self.saveWorker.start()
        else:
            QMessageBox.critical(self, "Error", f"Enter Subject ID and Session ID")
        
    def saveeAllFilesInBIDSFormat(self):
        if self.subjectID.text() != '' and self.sessionID.text() != '':         
            self.saveMessageBox = self.showWaitingMessage('Saving All files')
            self.saveMessageBox.setWindowTitle("Saving")
            for run in range(self.mappingTableWidget.rowCount()):
                self.setupDirsForSavingFiles()
                self.setupFilePathsForSavingFilesBIDSFormat()
                self.extractDataForCurrentRun()
                self.saveWorker = SaveWorker(self)
                self.currentMappingRow += 1
                self.saveWorker.finished.connect(self.onSaveFinished)
                self.saveWorker.error.connect(self.onSaveError)
                self.runCount += 1
                self.saveWorker.start()
        else:
            QMessageBox.critical(self, "Error", f"Enter Subject ID and Session ID")

    def setupDirsForSavingFiles(self):
        if not self.checkDirectorySetup:
            if self.subjectID.text() != '' and self.sessionID.text() != '':
                self.checkDirectorySetup = True
                self.subjectDirName = f'sub-{self.subjectID.text()}'
                self.SessionDirName = f'ses-{self.sessionID.text()}'
                self.subjectAndSessionDir = Path(config.bidsDir, self.subjectDirName, self.SessionDirName)
                os.makedirs(self.subjectAndSessionDir, exist_ok=True)
                self.subjectAndSessionDirName = f'{self.subjectDirName}_{self.SessionDirName}'
            else:
                QMessageBox.critical(self, "Error", f"Enter Subject ID and Session ID")

    def setupFilePathsForSavingFilesBIDSFormat(self):
        if self.checkDirectorySetup:
            rowData = extractRowDataFromTable(self.mappingTableWidget, self.currentMappingRow)
            word = rowData[1]
            self.currentWord = word
            backgroundColor = getRowBackgroundColorFromTable(self.mappingTableWidget, self.currentMappingRow)
            if backgroundColor == self.backgroundColorSayingBlock:
                self.currentBlock = 'Saying'
            if backgroundColor == self.backgroundColorImaginingBlock:
                self.currentBlock = 'Thinking'
            
            self.currentTask = rowData[0]
            self.filePathsUntillBlock = f'{self.subjectAndSessionDirName}_activity-{self.taskType.currentText()}_block-{self.currentBlock}_task-{self.currentTask}'
            self.currentActivity = self.taskType.currentText()
            
            if self.currentBlock == 'Saying':
                self.fullFilePathBidsFormat = f'{self.filePathsUntillBlock}_word-{word}_run-{self.runCount}'

            if self.currentBlock == 'Thinking':
                self.fullFilePathBidsFormat = f'{self.filePathsUntillBlock}_word-{word}_run-{self.runCount}'
            print(self.fullFilePathBidsFormat)

    def changeRowColors(self):
        color = "#ffff00"
        for row in range(self.mappingTableWidget.rowCount()):
            item = self.mappingTableWidget.item(row, 0) 
            value = item.text()
            print(value)
            if value == 'StartBlockThinking':
                color = self.backgroundColorImaginingBlock
            if value == 'StartBlockSaying':
                color = self.backgroundColorSayingBlock
          
            for col in range(self.mappingTableWidget.columnCount()):
                item = self.mappingTableWidget.item(row, col)
                if item is not None:
                    item.setBackground(QColor(color))

    
    def updateEegPlot(self):
        eegData = np.random.normal(size=1000)
        self.plotDataItem.setData(eegData)

    def closeEvent(self, event):
        self.aboutToClose.emit()
        event.accept()

    def onSaveError(self, errorMessage):
        self.saveMessageBox.accept()
        QMessageBox.critical(self, "Error", f"Failed to load EEG data: {errorMessage}")
        return 'Error'

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
        self.mappingTableWidget.removeRow(self.currentMappingRow)
        self.currentMappingRow = 0
        self.saveMessageBox.accept()
        
    def onLoadError(self, error_message):
        self.waitingMessageBox.accept()
        QMessageBox.critical(self, "Error", f"Failed to load EEG data: {error_message}")
    
    def calaculateMappings(self):
        activity = None
        task = None
        word = None
        mappings = []
        for index in range(0, self.triggers.shape[0], 2):
            activity, action = self.triggers[index].split(':')
            task, word = action.split('_')
            activity = self.getActivity(activity)
            startTime = self.triggersTimestamps[index]
            endTime = self.triggersTimestamps[index+1]
            audioStartIndex = self.findClosestIndex(self.audioTimestamps, startTime)
            audioEndIndex = self.findClosestIndex(self.audioTimestamps, endTime)
            eegStartIndex = self.findClosestIndex(self.eegTimestamps, startTime)
            eegEndIndex = self.findClosestIndex(self.eegTimestamps, endTime)
            mappings.append([startTime, endTime, audioStartIndex, audioEndIndex, eegStartIndex, eegEndIndex])
        
        self.mappingsList = mappings
        
    
    def findClosestIndex(self, timepoints, target):
        timepoints = np.asarray(timepoints)  # Ensure the input is a NumPy array
        idx = np.searchsorted(timepoints, target, side="left")
        if idx == 0:
            return 0
        if idx == len(timepoints):
            return len(timepoints) - 1
        
        before = idx - 1
        after = idx
        
        if after < len(timepoints) and abs(timepoints[after] - target) < abs(timepoints[before] - target):
            return after
        else:
            return before
    def getActivity(self,activity):
        if 'Fixation' in activity:
            return 'Fixation'
        elif 'ITI' in activity:
            return 'ITI'
        elif 'ISI' in activity:
            return 'ISI'
        elif 'Speech' in activity:
            return 'Speech'
        elif 'Stimulus' in activity:
            return 'Stimulus'
        else:
            return 'None'