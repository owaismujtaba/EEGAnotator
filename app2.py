from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QComboBox
)
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from PyQt5.QtCore import Qt
import sys
import mne
from src.GUI.utils import get_file_name_from_path
from src.eeg import EEG


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

        # EEG File Browser Layout (Row)
        self.eeg_browser_layout = QHBoxLayout()
        self.eeg_label = QLabel('EEG(.EDF) File:')
        self.eeg_label.setStyleSheet("color: darkbrown; font-weight: bold;background-color: lightgreen; border: 2px solid black; border-radius: 5px")
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
        self.eeg_start_time = QLabel('Start:')
        self.eeg_start_time.setStyleSheet("color: darkbrown; font-weight: bold;background-color: lightgreen; border: 2px solid black; border-radius: 5px")
        self.eeg_duration = QLabel('Duration:')
        self.eeg_duration.setStyleSheet("color: darkbrown; font-weight: bold;background-color: lightgreen; border: 2px solid black; border-radius: 5px")
        self.eeg_n_channels = QLabel('No. of Channels:')
        self.eeg_n_channels.setStyleSheet("color: darkbrown; font-weight: bold;background-color: lightgreen; border: 2px solid black; border-radius: 5px")
        self.eeg_info_layout.addWidget(self.eeg_start_time)
        self.eeg_info_layout.addWidget(self.eeg_duration)
        self.eeg_info_layout.addWidget(self.eeg_n_channels)

        self.eeg_info_layout_1 = QHBoxLayout()
        self.eeg_interrputions = QLabel('Interruptions: ')
        self.eeg_interrputions.setStyleSheet("color: darkbrown; font-weight: bold;background-color: lightgreen; border: 2px solid black; border-radius: 5px")
        self.eeg_n_interruptions = QLabel('No. Interruptions')
        self.eeg_n_interruptions.setStyleSheet("color: darkbrown; font-weight: bold;background-color: lightgreen; border: 2px solid black; border-radius: 5px")
        self.eeg_info_layout_1.addWidget(self.eeg_interrputions)
        self.eeg_info_layout_1.addWidget(self.eeg_n_interruptions)


        # EEG Channel Info Layout (Row)
        self.eeg_channel_info_layout = QHBoxLayout()
        self.eeg_channel_names_box = QComboBox()
        self.eeg_bad_channels = QComboBox()
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

        self.eeg_layout.addLayout(self.eeg_browser_layout)
        self.eeg_layout.addLayout(self.eeg_info_layout_1)
        self.eeg_layout.addLayout(self.eeg_info_layout)
        self.eeg_layout.addLayout(self.eeg_channel_info_layout)

        # Audio Info Layout
        self.audio_layout = QVBoxLayout()

        # Audio File Browser Layout (Row)
        self.audio_browser_layout = QHBoxLayout()
        self.audio_file_name = QLabel('Audio(.XDF) File:')
        self.audio_file_name.setStyleSheet("color: darkbrown; font-weight: bold;background-color: lightgreen; border: 2px solid black; border-radius: 5px")
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
        self.audio_load_btn = QPushButton('Load File')
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
        self.audio_start_time = QLabel('Start:')
        self.audio_start_time.setStyleSheet("color: darkbrown; font-weight: bold;background-color: lightgreen; border: 2px solid black; border-radius: 5px")
        self.audio_duration = QLabel('Duration:')
        self.audio_duration.setStyleSheet("color: darkbrown; font-weight: bold;background-color: lightgreen; border: 2px solid black; border-radius: 5px")
        self.audio_info_layout.addWidget(self.audio_start_time)
        self.audio_info_layout.addWidget(self.audio_duration)

        self.audio_layout.addLayout(self.audio_browser_layout)
        self.audio_layout.addLayout(self.audio_info_layout)

        self.files_info_layout.addLayout(self.eeg_layout)
        self.files_info_layout.addLayout(self.audio_layout)


        #Define functions for button clicks

        self.eeg_browser_file_btn.clicked.connect(self.browse_eeg_file)
        self.eeg_load_file_btn.clicked.connect(self.load_edf_file)
        self.eeg_visualise_btn.clicked.connect(self.visualise_eeg_data)


    def browse_eeg_file(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Open EDF File", "", "EDF Files (*.edf)")
        if file_path:
            self.edf_file_path = file_path
            self.edf_file_name = get_file_name_from_path(file_path)
            self.eeg_browser_file_btn.setText(self.edf_file_name)

    def load_edf_file(self):
        if self.edf_file_path:
            waiting_msg_box = self.show_waiting_message("Loading EEG data. Please wait...")
            self.eeg_data = EEG(self.edf_file_path)
            self.updade_eeg_info()
            waiting_msg_box.accept()
            
    def updade_eeg_info(self):
        self.eeg_label.setText('File Loaded')
        self.eeg_start_time.setText('Start:' + str(self.eeg_data.start_time))
        self.eeg_duration.setText('Duration: ' +str(self.eeg_data.duration))
        self.eeg_n_channels.setText('No. Channels: ' + str(self.eeg_data.n_channels))
        self.eeg_channel_names_box.clear()
        self.eeg_channel_names_box.addItems(self.eeg_data.channel_names)
        self.eeg_bad_channels.clear()
        if self.eeg_data.interruptions_check:
            interruptions = 'True'
            n_interruptions = len(self.eeg_data.interruptions)
        else:
            interruptions = 'False'
            n_interruptions = '0'
        
        self.eeg_interrputions.setText('Interruptions: ' + interruptions)
        self.eeg_n_interruptions.setText('No. of Interruptions: ' + n_interruptions)
        #self.eeg_bad_channels.addItems(self.eeg_data.raw_data.)

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
    
if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
