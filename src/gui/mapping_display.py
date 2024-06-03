import numpy as np
import pyqtgraph as pg
import soundfile as sf
from PyQt5.QtWidgets import (
    QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, QWidget,
    QListWidget, QGroupBox, QLabel, QLineEdit, QMessageBox, QApplication
)
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtCore import Qt, QUrl, QTimer, pyqtSignal, QThread
from PyQt5.QtGui import QIcon

from gui.utils import extractWidgets, buttonStyle
from gui.utils import convertMappingsToListForMainDisplay
import config as config
from scipy.io.wavfile import write
import os
from pathlib import Path
import json
import os


class SaveWorker(QThread):
    finished = pyqtSignal()
    error = pyqtSignal(str)
    def __init__(self, app):
        super().__init__()
        self.app = app

    def run(self):
        try:
            metaData = {
                'audioFileName': str(self.app.audioFileNameToSavePath),
                'eegFileName': str(self.app.eegFileNameToSavePath),
                'action': self.app.marker,
                'word': self.app.word,
                'eegStartIndex': self.app.eegStartIndex,
                'eegEndIndex': self.app.eegEndIndex,
                'audioStartIndex': self.app.audioStartIndex,
                'audioEndIndex': self.app.audioEndIndex,
                'channelNames':self.app.channelNames
            }
            with open(str(self.app.metaDataFileNameToSavePath), 'w') as jsonFile:
                json.dump(metaData, jsonFile)
            np.save(self.app.audioFileNameToSavePath, self.app.audioSample)

            sliced_raw = self.app.eegAudioData.eegData.rawData.copy().crop(
                tmin=metaData['eegStartIndex'] /self.app.eegAudioData.eegData.samplingFrequency, 
                tmax=metaData['eegEndIndex'] / self.app.eegAudioData.eegData.samplingFrequency
            )

            sliced_raw.save(metaData['eegFileName'], overwrite=True)
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))


class EEGAudioApp(QMainWindow):
    aboutToClose = pyqtSignal()

    def __init__(self, eegDaudioData):
        super().__init__()
        self.setupDirectories()
        self.eegAudioData = eegDaudioData
        self.mappings = self.eegAudioData.mappingEegEventsWithMarkers
        self.mappingListItems = convertMappingsToListForMainDisplay(self.mappings)

        self.timer = QTimer()
        self.timer.timeout.connect(self.updateAudioPlot)
        self.audioIndex = 0

        self.initUI()

    def setupDirectories(self):
        os.makedirs(config.outputDirAudio, exist_ok=True)
        os.makedirs(config.outputDirEEG, exist_ok=True)
        os.makedirs(config.outputDirMetadata, exist_ok=True)

    def initUI(self):
        self.mainWidget = QWidget()
        self.setCentralWidget(self.mainWidget)
        self.setWindowIcon(QIcon(config.windowIconPath))

        mainLayout = QVBoxLayout()
        topLayout, bottomLayout = self.createMainLayouts()

        mainLayout.addLayout(topLayout)
        mainLayout.addLayout(bottomLayout)

        self.mainWidget.setLayout(mainLayout)

        self.setWindowTitle('EEG and Audio Viewer')
        self.setGeometry(100, 100, 1200, 600)

        self.mediaPlayer = QMediaPlayer()

    def createMainLayouts(self):
        topLayout = self.createTopLayout()
        bottomLayout = self.createBottomLayout()
        return topLayout, bottomLayout

    def createTopLayout(self):
        topLayout = QHBoxLayout()

        self.listGroupBox = self.createListGroupBox()
        self.eegPlotWidget = self.createEegPlotWidget()
        self.audioPlotWidget = self.createAudioPlotWidget()

        topLayout.addWidget(self.listGroupBox)
        topLayout.addWidget(self.eegPlotWidget)
        topLayout.addWidget(self.audioPlotWidget)
        
        return topLayout

    def createListGroupBox(self):
        listGroupBox = QGroupBox("Mappings")
        listLayout = QVBoxLayout()
        
        self.listWidget = QListWidget()
        self.listWidget.addItems(self.mappingListItems)
        self.listWidget.currentItemChanged.connect(self.updateInfoFromListItem)
        
        listLayout.addWidget(self.listWidget)
        listGroupBox.setLayout(listLayout)

        return listGroupBox

    def createEegPlotWidget(self):
        plotWidget = pg.PlotWidget(title="EEG Activity")
        plotWidget.setBackground('w')
        plotWidget.getPlotItem().showGrid(True, True)
        self.plotDataItem = plotWidget.plot(pen='b')
        self.updateEegPlot()
        
        return plotWidget

    def createAudioPlotWidget(self):
        audioPlotWidget = pg.PlotWidget(title="Audio Visualizer")
        audioPlotWidget.setBackground('g')
        audioPlotWidget.getPlotItem().showGrid(True, True)
        self.audioPlotDataItem = audioPlotWidget.plot(pen='red')
        
        return audioPlotWidget

    def createBottomLayout(self):
        bottomLayout = QVBoxLayout()
        
        audioControlLayout = self.createAudioControlLayout()
        infoLayout = self.createInfoLayout()
        navigationLayout = self.createNavigationLayout()
        
        bottomLayout.addLayout(audioControlLayout)
        bottomLayout.addLayout(infoLayout)
        bottomLayout.addStretch()
        bottomLayout.addLayout(navigationLayout)
        
        return bottomLayout

    def createAudioControlLayout(self):
        audioControlLayout = QHBoxLayout()
        
        self.playButton = QPushButton("Play")
        self.playButton.setStyleSheet(buttonStyle)
        self.stopButton = QPushButton("Stop")
        self.stopButton.setStyleSheet(buttonStyle)
        
        self.playButton.clicked.connect(self.playAudio)
        self.stopButton.clicked.connect(self.stopAudio)
        
        audioControlLayout.addWidget(self.playButton)
        audioControlLayout.addWidget(self.stopButton)
        
        return audioControlLayout

    def createInfoLayout(self):
        self.labels = ["Action:", "Word:", "StartTime(EEG):", "EndTime(EEG):", "StartIndex(EEG):", "EndIndex(EEG):", "StartIndex(Audio):", "Duration:", "StartTime(Audio):"]
        self.infoLayout = QVBoxLayout()
        count = 0
        
        for i in range(3):
            hbox1 = QHBoxLayout()
            hbox2 = QHBoxLayout()

            for j in range(3):
                label = QLabel(self.labels[count])
                count += 1
                textBox = QLineEdit()
                hbox1.addWidget(label)
                hbox2.addWidget(textBox)
                
            self.infoLayout.addLayout(hbox1)
            self.infoLayout.addLayout(hbox2)
        
        return self.infoLayout

    def createNavigationLayout(self):
        buttonLayout = QHBoxLayout()
        
        self.prevButton = QPushButton("Previous")
        self.prevButton.setStyleSheet(buttonStyle)
        self.nextButton = QPushButton("Next")
        self.nextButton.setStyleSheet(buttonStyle)
        self.discardButton = QPushButton("Discard")
        self.discardButton.setStyleSheet(buttonStyle)
        self.saveButton = QPushButton("Save")
        self.saveButton.setStyleSheet(buttonStyle)
        
        self.prevButton.clicked.connect(self.prevAction)
        self.nextButton.clicked.connect(self.nextAction)
        self.discardButton.clicked.connect(self.discardAction)
        self.saveButton.clicked.connect(self.saveAction)
        
        buttonLayout.addWidget(self.prevButton)
        buttonLayout.addWidget(self.nextButton)
        buttonLayout.addWidget(self.discardButton)
        buttonLayout.addWidget(self.saveButton)
        
        return buttonLayout

    def closeEvent(self, event):
        self.aboutToClose.emit()
        event.accept()

    def updateEegPlot(self):
        eegData = np.random.normal(size=1000)
        self.plotDataItem.setData(eegData)

    def updateAudioPlot(self):
        if self.audioData is not None:
            chunkSize = 1024
            endIndex = self.audioIndex + chunkSize
            if endIndex >= len(self.audioData):
                endIndex = len(self.audioData)
                self.timer.stop()
            dataChunk = self.audioData[self.audioIndex:endIndex]
            self.audioPlotDataItem.setData(dataChunk)
            self.audioIndex = endIndex

    def playAudio(self):
        self.audioSampleRate = self.eegAudioData.audioData.samplingFrequency
        if not os.path.exists(self.audioFileNameToSavePathWav):
            write(self.audioFileNameToSavePathWav, int(self.audioSampleRate), self.audioSample)
        self.audioData, self.sampleRate = sf.read(self.audioFileNameToSavePathWav, dtype='int16')
        self.audioIndex = 0
        mediaContent = QMediaContent(QUrl.fromLocalFile(str(self.audioFileNameToSavePathWav)))
        self.mediaPlayer.setMedia(mediaContent)
        self.mediaPlayer.play()
        self.timer.start(30)

    def stopAudio(self):
        self.mediaPlayer.stop()
        self.timer.stop()

    def prevAction(self):
        currentRow = self.listWidget.currentRow()
        if currentRow > 0:
            self.listWidget.setCurrentRow(currentRow - 1)
            self.updateInfoFromListItem()

    def nextAction(self):
        currentRow = self.listWidget.currentRow()
        if currentRow < self.listWidget.count() - 1:
            self.listWidget.setCurrentRow(currentRow + 1)
            self.updateInfoFromListItem()

    def discardAction(self):
        currentRow = self.listWidget.currentRow()
        if currentRow < self.listWidget.count() - 1:
            self.listWidget.setCurrentRow(currentRow + 1)
            self.updateInfoFromListItem()

    def saveAction(self):
        
        self.saveMessageBox = self.showWaitingMessage('Saving files')
        self.saveMessageBox.setWindowTitle("Saving")
        self.saveWorker = SaveWorker(self)
        self.saveWorker.finished.connect(self.onSaveFinished)
        self.saveWorker.error.connect(self.onSaveError)
        self.saveWorker.start()

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

    def updateInfoFromListItem(self):
        selectedItemText = self.listWidget.currentItem().text()
        infoParts = selectedItemText.split(",")

        self.marker = infoParts[0]
        self.word = infoParts[1]
        self.eegStartIndex = int(infoParts[4])
        self.eegEndIndex = int(infoParts[5])
        self.duration = int(infoParts[7])
        self.audioStartIndex = int(infoParts[6])
        self.audioEndIndex = self.audioStartIndex + int(
            (self.duration / int(self.eegAudioData.eegData.samplingFrequency)) * self.eegAudioData.audioData.samplingFrequency)

        self.audioSample = self.eegAudioData.audioData.audio[self.audioStartIndex:self.audioEndIndex]
        self.audioSample = self.audioSample.reshape(-1)
        self.eegSample = self.eegAudioData.eegData.rawData[:self.eegStartIndex:self.eegEndIndex]

        self.channelNames = self.eegAudioData.eegData.channelNames
        self.eegFileNameToSavePath = Path(config.outputDirEEG, f'{self.marker}_{self.word}_{self.eegStartIndex}.fif')
        self.audioFileNameToSavePath = Path(config.outputDirAudio, f'{self.marker}_{self.word}_{self.eegStartIndex}.npy')
        self.audioFileNameToSavePathWav = Path(config.outputDirAudio, f'{self.marker}_{self.word}_{self.eegStartIndex}.wav')
        self.metaDataFileNameToSavePath = Path(config.outputDirMetadata, f'{self.marker}_{self.word}.json')
        
        infoParts[2] = str(np.array(float(infoParts[2])).astype('datetime64[s]'))
        infoParts[3] = str(np.array(float(infoParts[3])).astype('datetime64[s]'))
        infoParts[8] = str(np.array(float(infoParts[8])).astype('datetime64[s]'))
        
        
        widgets = extractWidgets(self.infoLayout)
        count = 0
        for widget in widgets:
            if isinstance(widget, QLineEdit):
                widget.setText(infoParts[count])
                count += 1

