import sys
import numpy as np
import soundfile as sf
import pyqtgraph as pg
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, QWidget
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtCore import QUrl, QTimer, pyqtSignal

class EEGAudioApp(QMainWindow):
    about_to_close = pyqtSignal()

    def __init__(self, EEG_AUDIO_DATA):
        super().__init__()

        self.EEG_AUDIO_DATA = EEG_AUDIO_DATA
        self.initUI()
        
        # Audio visualizer variables
        self.audio_data = None
        self.sample_rate = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_audio_plot)
        self.audio_index = 0

    def initUI(self):
        # Main widget
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        
        # Layouts
        main_layout = QVBoxLayout()
        top_layout = QHBoxLayout()
        bottom_layout = QHBoxLayout()

        # EEG plot setup
        self.plotWidget = pg.PlotWidget(title="EEG Activity")
        self.plotWidget.setBackground('w')  # Set background color to white
        self.plotDataItem = self.plotWidget.plot()
        self.update_eeg_plot()

        # Audio plot setup
        self.audioPlotWidget = pg.PlotWidget(title="Audio Visualizer")
        self.audioPlotWidget.setBackground('g')  # Set background color to green
        self.audioPlotDataItem = self.audioPlotWidget.plot()
        
        top_layout.addWidget(self.plotWidget)
        top_layout.addWidget(self.audioPlotWidget)

        # Audio control buttons
        audio_control_layout = QHBoxLayout()
        self.play_button = QPushButton("Play")
        self.stop_button = QPushButton("Stop")
        self.play_button.clicked.connect(self.play_audio)
        self.stop_button.clicked.connect(self.stop_audio)
        audio_control_layout.addWidget(self.play_button)
        audio_control_layout.addWidget(self.stop_button)

        # Navigation buttons
        button_layout = QHBoxLayout()
        self.prev_button = QPushButton("Previous")
        self.next_button = QPushButton("Next")
        self.discard_button = QPushButton("Discard")
        self.save_button = QPushButton("Save")
        self.prev_button.clicked.connect(self.prev_action)
        self.next_button.clicked.connect(self.next_action)
        self.discard_button.clicked.connect(self.discard_action)
        self.save_button.clicked.connect(self.save_action)
        button_layout.addWidget(self.prev_button)
        button_layout.addWidget(self.next_button)
        button_layout.addWidget(self.discard_button)
        button_layout.addWidget(self.save_button)

        bottom_layout.addLayout(audio_control_layout)
        bottom_layout.addStretch()
        bottom_layout.addLayout(button_layout)

        main_layout.addLayout(top_layout)
        main_layout.addLayout(bottom_layout)

        self.main_widget.setLayout(main_layout)

        # Window settings
        self.setWindowTitle('EEG and Audio Viewer')
        self.setGeometry(100, 100, 800, 600)

        # Initialize media player
        self.mediaPlayer = QMediaPlayer()

    def closeEvent(self, event):
        self.about_to_close.emit()  # Emit the custom signal
        event.accept()

    def update_eeg_plot(self):
        # Generate random EEG data for demonstration
        eeg_data = np.random.normal(size=1000)
        self.plotDataItem.setData(eeg_data)

    def update_audio_plot(self):
        if self.audio_data is not None:
            chunk_size = 1024
            end_index = self.audio_index + chunk_size
            if end_index >= len(self.audio_data):
                end_index = len(self.audio_data)
                self.timer.stop()
            data_chunk = self.audio_data[self.audio_index:end_index]
            self.audioPlotDataItem.setData(data_chunk)
            self.audio_index = end_index

    def play_audio(self):
        self.audio_data, self.sample_rate = sf.read("/home/owais/GitHub/21-05-2024/EEGAnotator/audio_file.wav", dtype='int16')
        self.audio_index = 0
        media_content = QMediaContent(QUrl.fromLocalFile("/home/owais/GitHub/21-05-2024/EEGAnotator/audio_file.wav"))
        self.mediaPlayer.setMedia(media_content)
        self.mediaPlayer.play()
        self.timer.start(30)

    def stop_audio(self):
        self.mediaPlayer.stop()
        self.timer.stop()

    def prev_action(self):
        print("Previous button clicked")

    def next_action(self):
        print("Next button clicked")

    def discard_action(self):
        print("Discard button clicked")

    def save_action(self):
        print("Save button clicked")

