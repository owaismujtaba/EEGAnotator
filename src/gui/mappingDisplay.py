import sys
import numpy as np
import soundfile as sf
import pyqtgraph as pg
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QListWidget, QGroupBox
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtCore import QUrl, QTimer, pyqtSignal
from src.gui.utils import text_box_style, label_style, button_style, combobox_style



class EEGAudioApp(QMainWindow):
    about_to_close = pyqtSignal()

    def __init__(self, x):
        super().__init__()
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
        self.setGeometry(500, 300, 1200, 300)
        # Layouts
        main_layout = QVBoxLayout()
        top_layout = QHBoxLayout()
        bottom_layout = QHBoxLayout()

        # List Widget for displaying items with title
        list_group_box = QGroupBox("Mappings")
        list_layout = QVBoxLayout()
        self.listWidget = QListWidget()
        self.listWidget.addItems(["Item 1", "Item 2", "Item 3"])  # Add items to the list
        self.listWidget.currentItemChanged.connect(self.on_list_item_changed)
        list_layout.addWidget(self.listWidget)
        list_group_box.setLayout(list_layout)

        # EEG plot setup
        self.plotWidget = pg.PlotWidget(title="EEG Activity")
        self.plotWidget.setBackground('w')  # Set background color to white
        self.plotWidget.getPlotItem().showGrid(True, True)  # Show grid
        self.plotDataItem = self.plotWidget.plot(pen='b')  # Set pen color to blue
        self.update_eeg_plot()

        # Audio plot setup
        self.audioPlotWidget = pg.PlotWidget(title="Audio Visualizer")
        self.audioPlotWidget.setBackground('g')  # Set background color to green
        self.audioPlotWidget.getPlotItem().showGrid(True, True)  # Show grid
        self.audioPlotDataItem = self.audioPlotWidget.plot(pen='y')  # Set pen color to yellow

        top_layout.addWidget(list_group_box)
        top_layout.addWidget(self.plotWidget)
        top_layout.addWidget(self.audioPlotWidget)

        # Audio control buttons
        audio_control_layout = QHBoxLayout()
        self.play_button = QPushButton("Play")
        self.play_button.setStyleSheet(button_style)
        self.stop_button = QPushButton("Stop")
        self.stop_button.setStyleSheet(button_style)
        self.play_button.clicked.connect(self.play_audio)
        self.stop_button.clicked.connect(self.stop_audio)
        audio_control_layout.addWidget(self.play_button)
        audio_control_layout.addWidget(self.stop_button)

        # Navigation buttons
        button_layout = QHBoxLayout()
        self.prev_button = QPushButton("Previous")
        self.prev_button.setStyleSheet(button_style)
        self.next_button = QPushButton("Next")
        self.next_button.setStyleSheet(button_style)
        self.discard_button = QPushButton("Discard")
        self.discard_button.setStyleSheet(button_style)
        self.save_button = QPushButton("Save")
        self.save_button.setStyleSheet(button_style)
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

    def on_list_item_changed(self, current, previous):
        print(f"Selected: {current.text()}")


