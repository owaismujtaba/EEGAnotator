import numpy as np
import pyqtgraph as pg
import soundfile as sf
from PyQt5.QtWidgets import (
    QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, QWidget,
    QListWidget, QGroupBox, QLabel, QLineEdit
)
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtCore import QUrl, QTimer, pyqtSignal
from PyQt5.QtGui import QIcon

from src.gui.utils import extract_widgets, button_style
from src.gui.utils import convert_mappings_to_list_for_mainDisplay
import config
from scipy.io.wavfile import write
import os
from pathlib import Path
import json


class EEGAudioApp(QMainWindow):
    about_to_close = pyqtSignal()

    def __init__(self, eeg_daudio_data):
        super().__init__()
        self.setup_directories()
        self.EEG_AUDIO_DATA = eeg_daudio_data
        self.MAPPINGS = self.EEG_AUDIO_DATA.MappingEEGEventsWithMarkers
        self.mapping_list_items = convert_mappings_to_list_for_mainDisplay(self.MAPPINGS)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_audio_plot)
        self.audio_index = 0

        self.initUI()

    def setup_directories(self):
        os.makedirs(config.OUTPUT_DIR_AUDIO, exist_ok=True)
        os.makedirs(config.OUTPUT_DIR_EEG, exist_ok=True)
        os.makedirs(config.OUTPUT_DIR_METADATA, exist_ok=True)

    def initUI(self):
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.setWindowIcon(QIcon(config.WINDOW_ICON_PATH))

        main_layout = QVBoxLayout()
        top_layout, bottom_layout = self.create_main_layouts()

        main_layout.addLayout(top_layout)
        main_layout.addLayout(bottom_layout)

        self.main_widget.setLayout(main_layout)

        self.setWindowTitle('EEG and Audio Viewer')
        self.setGeometry(100, 100, 1200, 600)

        self.mediaPlayer = QMediaPlayer()

    def create_main_layouts(self):
        top_layout = self.create_top_layout()
        bottom_layout = self.create_bottom_layout()
        return top_layout, bottom_layout

    def create_top_layout(self):
        top_layout = QHBoxLayout()

        self.list_group_box = self.create_list_group_box()
        self.eeg_plot_widget = self.create_eeg_plot_widget()
        self.audio_plot_widget = self.create_audio_plot_widget()

        top_layout.addWidget(self.list_group_box)
        top_layout.addWidget(self.eeg_plot_widget)
        top_layout.addWidget(self.audio_plot_widget)
        
        return top_layout

    def create_list_group_box(self):
        list_group_box = QGroupBox("Mappings")
        list_layout = QVBoxLayout()
        
        self.listWidget = QListWidget()
        self.listWidget.addItems(self.mapping_list_items)
        self.listWidget.currentItemChanged.connect(self.update_info_from_list_item)
        
        list_layout.addWidget(self.listWidget)
        list_group_box.setLayout(list_layout)

        return list_group_box

    def create_eeg_plot_widget(self):
        plot_widget = pg.PlotWidget(title="EEG Activity")
        plot_widget.setBackground('w')
        plot_widget.getPlotItem().showGrid(True, True)
        self.plotDataItem = plot_widget.plot(pen='b')
        self.update_eeg_plot()
        
        return plot_widget

    def create_audio_plot_widget(self):
        audio_plot_widget = pg.PlotWidget(title="Audio Visualizer")
        audio_plot_widget.setBackground('g')
        audio_plot_widget.getPlotItem().showGrid(True, True)
        self.audioPlotDataItem = audio_plot_widget.plot(pen='y')
        
        return audio_plot_widget

    def create_bottom_layout(self):
        bottom_layout = QVBoxLayout()
        
        audio_control_layout = self.create_audio_control_layout()
        info_layout = self.create_info_layout()
        navigation_layout = self.create_navigation_layout()
        
        bottom_layout.addLayout(audio_control_layout)
        bottom_layout.addLayout(info_layout)
        bottom_layout.addStretch()
        bottom_layout.addLayout(navigation_layout)
        
        return bottom_layout

    def create_audio_control_layout(self):
        audio_control_layout = QHBoxLayout()
        
        self.play_button = QPushButton("Play")
        self.play_button.setStyleSheet(button_style)
        self.stop_button = QPushButton("Stop")
        self.stop_button.setStyleSheet(button_style)
        
        self.play_button.clicked.connect(self.play_audio)
        self.stop_button.clicked.connect(self.stop_audio)
        
        audio_control_layout.addWidget(self.play_button)
        audio_control_layout.addWidget(self.stop_button)
        
        return audio_control_layout

    def create_info_layout(self):
        self.labels = ["Action:", "Word:", "Start Time(EEG):", "End Time(EEG):", "Start Index(EEG):", "End Index(EEG):", "Start Index(Audio):", "Duration:", "Start Time(Audio):"]
        self.info_layout = QVBoxLayout()
        count = 0
        
        for i in range(3):
            hbox1 = QHBoxLayout()
            hbox2 = QHBoxLayout()

            for j in range(3):
                label = QLabel(self.labels[count])
                count += 1
                text_box = QLineEdit()
                hbox1.addWidget(label)
                hbox2.addWidget(text_box)
                
            self.info_layout.addLayout(hbox1)
            self.info_layout.addLayout(hbox2)
        
        return self.info_layout

    def create_navigation_layout(self):
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
        
        return button_layout

    def closeEvent(self, event):
        self.about_to_close.emit()
        event.accept()

    def update_eeg_plot(self):
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
        self.audio_sample_rate = self.EEG_AUDIO_DATA.audio.SAMPLING_FREQUENCY
        write(self.audio_file_name_to_save_path, int(self.audio_sample_rate), self.audio_sample)
        self.audio_data, self.sample_rate = sf.read(self.audio_file_name_to_save_path, dtype='int16')
        self.audio_index = 0
        media_content = QMediaContent(QUrl.fromLocalFile(str(self.audio_file_name_to_save_path)))
        self.mediaPlayer.setMedia(media_content)
        self.mediaPlayer.play()
        self.timer.start(30)

    def stop_audio(self):
        self.mediaPlayer.stop()
        self.timer.stop()

    def prev_action(self):
        current_row = self.listWidget.currentRow()
        if current_row > 0:
            self.listWidget.setCurrentRow(current_row - 1)
            self.update_info_from_list_item()

    def next_action(self):
        current_row = self.listWidget.currentRow()
        if current_row < self.listWidget.count() - 1:
            self.listWidget.setCurrentRow(current_row + 1)
            self.update_info_from_list_item()

    def discard_action(self):
        current_row = self.listWidget.currentRow()
        if current_row < self.listWidget.count() - 1:
            self.listWidget.setCurrentRow(current_row + 1)
            self.update_info_from_list_item()

    def save_action(self):
        meta_data = {'audio_file_name': str(self.audio_file_name_to_save_path), 'eeg_file_name':str(self.eeg_file_name_to_save_path),
                     'Action':self.marker, 'word': self.word, 'eeg_start_index':self.eeg_start_index,
                        'eeg_end_index': self.eeg_end_index, 'audio_start_index': self.audio_start_index,
                        'audio_end_index':self.audio_end_index 
                    }
        with open(self.meta_data_file_name_to_save_path, 'w') as json_file:
            json.dump(meta_data, json_file)
        self.audio_sample.save(self.audio_file_name_to_save_path)
        #self.

    def update_info_from_list_item(self):
        selected_item_text = self.listWidget.currentItem().text()
        info_parts = selected_item_text.split(",")

        self.marker = info_parts[0]
        self.word = info_parts[1]
        self.eeg_start_index = int(info_parts[4])
        self.eeg_end_index = int(info_parts[5])
        self.duration = int(info_parts[7])
        self.audio_start_index = int(info_parts[6])
        self.audio_end_index = self.audio_start_index + int(
            (self.duration / int(self.EEG_AUDIO_DATA.eeg.SAMPLING_FREQUENCY)) * self.EEG_AUDIO_DATA.audio.SAMPLING_FREQUENCY)

        self.audio_sample = self.EEG_AUDIO_DATA.audio.AUDIO[self.audio_start_index:self.audio_end_index]
        self.audio_sample = self.audio_sample.reshape(-1)
        self.eeg_sample = self.EEG_AUDIO_DATA.eeg.RAW_DATA[:self.eeg_start_index:self.eeg_end_index]

        self.channel_names = self.EEG_AUDIO_DATA.eeg.CHANNEL_NAMES
        self.eeg_file_name_to_save_path = Path(config.OUTPUT_DIR_EEG, f'eeg_{self.marker}_{self.word}_{self.eeg_start_index}.npy')
        self.audio_file_name_to_save_path = Path(config.OUTPUT_DIR_AUDIO, f'audio_{self.marker}_{self.word}_{self.eeg_start_index}.npy')
        self.meta_data_file_name_to_save_path = Path(config.OUTPUT_DIR_METADATA, f'meta_{self.marker}_{self.word}.json')

        print(
            self.marker,
            self.word,
            self.eeg_start_index,
            self.eeg_end_index,
            self.duration,
            self.audio_start_index,
            self.audio_end_index,
            self.eeg_file_name_to_save_path,
            self.audio_file_name_to_save_path
        )
        import pdb
        
        
        widgets = extract_widgets(self.info_layout)
        count = 0
        for widget in widgets:
            if isinstance(widget, QLineEdit):
                widget.setText(info_parts[count])
                count += 1
