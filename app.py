from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QComboBox, QFileDialog, QMessageBox, QSizePolicy
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import sys
import mne
from src.GUI.utils import get_file_name_from_path
from src.eeg import EEG
from src.audio import AUDIO

class LoadEEGThread(QThread):
    finished = pyqtSignal(object)
    error = pyqtSignal(str)

    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path

    def run(self):
        try:
            eeg_data = EEG(self.file_path)
            self.finished.emit(eeg_data)
        except Exception as e:
            self.error.emit(str(e))

class LoadAudioThread(QThread):
    finished = pyqtSignal(object)
    error = pyqtSignal(str)

    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path

    def run(self):
        try:
            audio_data = AUDIO(self.file_path)
            self.finished.emit(audio_data)
        except Exception as e:
            self.error.emit(str(e))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('DeepRESTORE')
        self.setGeometry(500, 300, 800, 300)  # Set window size and position

        # Set background color of the main window
        self.setStyleSheet("background-color: lightgray;")

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.files_info_layout = QHBoxLayout()  # Main horizontal layout
        central_widget.setLayout(self.files_info_layout)

        # EEG Info Layout
        self.eeg_layout = QVBoxLayout()
        self.eeg_widget = self.wrap_layout_in_widget(self.eeg_layout)
        self.eeg_widget.setStyleSheet("border: 2px solid black;")

        # EEG File Browser Layout (Row)
        self.eeg_browser_layout = QHBoxLayout()
        self.eeg_browser_widget = self.wrap_layout_in_widget(self.eeg_browser_layout)
        self.eeg_browser_widget.setStyleSheet("border: 1px solid black;")
        self.eeg_label = QLabel('EEG(.EDF) File:')
        self.eeg_label.setStyleSheet("color: darkbrown; font-weight: bold;background-color: lightgreen; border: 2px solid black; border-radius: 5px")
        self.eeg_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)  # Set size policy
        self.eeg_browser_file_btn = QPushButton('Select File')
        self.eeg_browser_file_btn.setStyleSheet("""
            QPushButton {
                background-color: lightcoral;
                color: black;
                border-radius: 5px;
                padding: 5px;
                border: 2px solid black;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: lightblue;
            }
        """)
        self.eeg_load_file_btn = QPushButton('Load')
        self.eeg_load_file_btn.setStyleSheet("""
            QPushButton {
                background-color: lightcoral;
                color: black;
                border-radius: 5px;
                padding: 5px;
                border: 2px solid black;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: lightblue;
            }
        """)
        self.eeg_browser_layout.addWidget(self.eeg_label)
        self.eeg_browser_layout.addWidget(self.eeg_browser_file_btn)
        self.eeg_browser_layout.addWidget(self.eeg_load_file_btn)

        # EEG Info Layout (Row)
        self.eeg_info_layout = QHBoxLayout()
        self.eeg_info_widget = self.wrap_layout_in_widget(self.eeg_info_layout)
        self.eeg_info_widget.setStyleSheet("border: 1px solid black;")
        self.eeg_start_time = QLabel('Start:')
        self.eeg_start_time.setStyleSheet("color: darkbrown; font-weight: bold;background-color: lightgreen; border: 2px solid black; border-radius: 5px")
        self.eeg_start_time.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)  # Set size policy
        self.eeg_duration = QLabel('Duration:')
        self.eeg_duration.setStyleSheet("color: darkbrown; font-weight: bold;background-color: lightgreen; border: 2px solid black; border-radius: 5px")
        self.eeg_duration.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)  # Set size policy
        self.eeg_n_channels = QLabel('No. of Channels:')
        self.eeg_n_channels.setStyleSheet("color: darkbrown; font-weight: bold;background-color: lightgreen; border: 2px solid black; border-radius: 5px")
        self.eeg_n_channels.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)  # Set size policy
        self.eeg_info_layout.addWidget(self.eeg_start_time)
        self.eeg_info_layout.addWidget(self.eeg_duration)
        self.eeg_info_layout.addWidget(self.eeg_n_channels)

        

        self.eeg_info_layout_1 = QHBoxLayout()
        self.eeg_info_widget_1 = self.wrap_layout_in_widget(self.eeg_info_layout_1)
        self.eeg_info_widget_1.setStyleSheet("border: 1px solid black;")
        self.eeg_interrputions = QLabel('Interruptions: ')
        self.eeg_interrputions.setStyleSheet("color: darkbrown; font-weight: bold;background-color: lightgreen; border: 2px solid black; border-radius: 5px")
        self.eeg_interrputions.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)  # Set size policy
        self.eeg_n_interruptions = QLabel('No. Interruptions')
        self.eeg_n_interruptions.setStyleSheet("color: darkbrown; font-weight: bold;background-color: lightgreen; border: 2px solid black; border-radius: 5px")
        self.eeg_n_interruptions.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)  # Set size policy
        self.eeg_info_layout_1.addWidget(self.eeg_interrputions)
        self.eeg_info_layout_1.addWidget(self.eeg_n_interruptions)

        #Events 
        self.events_info_layout = QHBoxLayout()
        self.events_info_widget = self.wrap_layout_in_widget(self.events_info_layout)
        self.events_info_widget.setStyleSheet("border: 1px solid black;")
        self.events =QComboBox()
        self.events = QComboBox()
        self.events.addItem('Events')
        self.events.setStyleSheet("color: darkbrown; font-weight: bold;background-color: #ff6666; border: 2px solid black; border-radius: 5px")
        self.events.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)  # Set size policy
        self.n_triggers = QComboBox()
        self.n_triggers.addItem('No. Triggers')
        self.n_triggers.setStyleSheet("color: darkbrown; font-weight: bold;background-color: #ff6666; border: 2px solid black; border-radius: 5px")
        self.n_triggers.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.events_info_layout.addWidget(self.events)
        self.events_info_layout.addWidget(self.n_triggers)

        # EEG Channel Info Layout (Row)
        self.eeg_channel_info_layout = QHBoxLayout()
        self.eeg_channel_info_widget = self.wrap_layout_in_widget(self.eeg_channel_info_layout)
        self.eeg_channel_info_widget.setStyleSheet("border: 1px solid black;")
        self.eeg_channel_names_box = QComboBox()
        self.eeg_channel_names_box.addItem('Channels')
        self.eeg_bad_channels = QComboBox()
        self.eeg_bad_channels.addItem('Bad Channels')
        self.eeg_visualise_btn = QPushButton('Visualize')
        self.eeg_visualise_btn.setStyleSheet("""
            QPushButton {
                background-color: lightcoral;
                color: black;
                border-radius: 5px;
                padding: 5px;
                border: 2px solid black;
                font-weight: bold;                             
            }
            QPushButton:hover {
                background-color: lightblue;
            }
        """)
        self.eeg_channel_info_layout.addWidget(self.eeg_channel_names_box)
        self.eeg_channel_info_layout.addWidget(self.eeg_bad_channels)
        self.eeg_channel_info_layout.addWidget(self.eeg_visualise_btn)

        self.eeg_layout.addWidget(self.eeg_browser_widget)
        self.eeg_layout.addWidget(self.eeg_info_widget_1)
        self.eeg_layout.addWidget(self.eeg_info_widget)
        self.eeg_layout.addWidget(self.events_info_widget)
        self.eeg_layout.addWidget(self.eeg_channel_info_widget)
        
        

        # Audio Info Layout
        self.audio_layout = QVBoxLayout()
        self.audio_widget = self.wrap_layout_in_widget(self.audio_layout)
        self.audio_widget.setStyleSheet("border: 2px solid black;")

        # Audio File Browser Layout (Row)
        self.audio_browser_layout = QHBoxLayout()
        self.audio_browser_widget = self.wrap_layout_in_widget(self.audio_browser_layout)
        self.audio_browser_widget.setStyleSheet("border: 1px solid black;")
        self.audio_file_name = QLabel('Audio(.XDF) File:')
        self.audio_file_name.setStyleSheet("color: darkbrown; font-weight: bold;background-color: lightgreen; border: 2px solid black; border-radius: 5px")
        self.audio_file_name.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)  # Set size policy
        self.audio_browser_btn = QPushButton('Select File')
        self.audio_browser_btn.setStyleSheet("""
            QPushButton {
                background-color: lightcoral;
                color: black;
                border-radius: 5px;
                padding: 5px;
                border: 2px solid black;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: lightblue;
            }
        """)
        self.audio_load_btn = QPushButton('Load')
        self.audio_load_btn.setStyleSheet("""
            QPushButton {
                background-color: lightcoral;
                color: black;
                border-radius: 5px;
                padding: 5px;
                border: 2px solid black;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: lightblue;
            }
        """)
        self.audio_browser_layout.addWidget(self.audio_file_name)
        self.audio_browser_layout.addWidget(self.audio_browser_btn)
        self.audio_browser_layout.addWidget(self.audio_load_btn)

        # Audio Info Layout (Row)
        self.audio_info_layout = QHBoxLayout()
        self.audio_info_widget = self.wrap_layout_in_widget(self.audio_info_layout)
        self.audio_info_widget.setStyleSheet("border: 1px solid black;")
        self.audio_start_time = QLabel('Start:')
        self.audio_start_time.setStyleSheet("color: darkbrown; font-weight: bold;background-color: lightgreen; border: 2px solid black; border-radius: 5px")
        self.audio_start_time.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)  # Set size policy
        self.audio_duration = QLabel('Duration:')
        self.audio_duration.setStyleSheet("color: darkbrown; font-weight: bold;background-color: lightgreen; border: 2px solid black; border-radius: 5px")
        self.audio_duration.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)  # Set size policy
        self.audio_info_layout.addWidget(self.audio_start_time)
        self.audio_info_layout.addWidget(self.audio_duration)

        self.audio_layout.addWidget(self.audio_browser_widget)
        self.audio_layout.addWidget(self.audio_info_widget)

        self.files_info_layout.addWidget(self.eeg_widget)
        self.files_info_layout.addWidget(self.audio_widget)

        # Define functions for button clicks
        self.eeg_browser_file_btn.clicked.connect(self.browse_eeg_file)
        self.eeg_load_file_btn.clicked.connect(self.load_edf_file)
        self.eeg_visualise_btn.clicked.connect(self.visualise_eeg_data)

        self.audio_browser_btn.clicked.connect(self.browse_audio_file)
        self.audio_load_btn.clicked.connect(self.load_xdf_file)

    def browse_audio_file(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Open XDF File", "", "XDF Files (*.xdf)")
        if file_path:
            self.xdf_file_path = file_path
            self.xdf_file_name = get_file_name_from_path(file_path)
            self.audio_browser_btn.setText(self.xdf_file_name)

    def load_xdf_file(self):
        if self.xdf_file_path:
            self.waiting_msg_box = self.show_waiting_message("Loading XEG data. Please wait...")
            self.load_thread_audio = LoadAudioThread(self.xdf_file_path)
            self.load_thread_audio.finished.connect(self.on_load_finished_audio)
            self.load_thread_audio.error.connect(self.on_load_error)
            self.load_thread_audio.start()

    def browse_eeg_file(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Open EDF File", "", "EDF Files (*.edf)")
        if file_path:
            self.edf_file_path = file_path
            self.edf_file_name = get_file_name_from_path(file_path)
            self.eeg_browser_file_btn.setText(self.edf_file_name)

    def load_edf_file(self):
        if self.edf_file_path:
            self.waiting_msg_box = self.show_waiting_message("Loading EEG data. Please wait...")
            self.load_thread_eeg = LoadEEGThread(self.edf_file_path)
            self.load_thread_eeg.finished.connect(self.on_load_finished_eeg)
            self.load_thread_eeg.error.connect(self.on_load_error)
            self.load_thread_eeg.start()

    def update_audio_info(self):
        self.audio_start_time.setText(str(self.audio_data.start_time_marker))
        self.audio_duration.setText(str(self.audio_data.end_time_marker))
        pass

    def on_load_finished_audio(self, audio_data):
        self.audio_data = audio_data
        self.update_audio_info()
        self.waiting_msg_box.accept()

    def on_load_finished_eeg(self, eeg_data):
        self.eeg_data = eeg_data
        self.update_eeg_info()
        self.waiting_msg_box.accept()

    def on_load_error(self, error_message):
        self.waiting_msg_box.accept()
        QMessageBox.critical(self, "Error", f"Failed to load EEG data: {error_message}")

    def update_eeg_info(self):
        self.eeg_label.setText('File Loaded')
        self.eeg_start_time.setText('Start: ' + str(self.eeg_data.start_time))
        self.eeg_duration.setText('Duration: ' + str(self.eeg_data.duration))
        self.eeg_n_channels.setText('No. Channels: ' + str(self.eeg_data.n_channels))
        self.eeg_channel_names_box.clear()
        self.eeg_channel_names_box.addItems(self.eeg_data.channel_names)
        self.eeg_bad_channels.clear()
        self.eeg_bad_channels.addItems(self.eeg_data.bad_channels)
        if self.eeg_data.interruptions_check:
            interruptions = 'True'
            n_interruptions = len(self.eeg_data.interruptions)
        else:
            interruptions = 'False'
            n_interruptions = '0'

        self.eeg_interrputions.setText('Interruptions: ' + interruptions)
        self.eeg_n_interruptions.setText('No. of Interruptions: ' + n_interruptions)

        self.events.clear()
        events = [str(tpl) for tpl in self.eeg_data.events]
        self.events.addItems(events)
        
        self.n_triggers.clear()
        triggers =  [str(tpl) for tpl in self.eeg_data.triggers_types]
        #triggers = ' '.join(['' + str(trig) for trig in self.eeg_data.triggers_types])
        self.n_triggers.addItems(triggers)

    def visualise_eeg_data(self):
        if self.eeg_data:
            self.eeg_data.raw_data.plot()

    def show_waiting_message(self, message):
        waiting_msg_box = QMessageBox()
        waiting_msg_box.setText(message)
        waiting_msg_box.setStandardButtons(QMessageBox.NoButton)
        waiting_msg_box.setWindowFlags(Qt.Window | Qt.CustomizeWindowHint | Qt.WindowTitleHint)
        waiting_msg_box.show()
        QApplication.processEvents()
        return waiting_msg_box

    def wrap_layout_in_widget(self, layout):
        widget = QWidget()
        widget.setLayout(layout)
        return widget

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
