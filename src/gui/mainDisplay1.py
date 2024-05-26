from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout,
    QVBoxLayout, QLabel, QPushButton, QComboBox, QFileDialog, 
    QMessageBox,  QLineEdit,  QListWidget
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QIcon, QPalette, QBrush, QPixmap

from src.gui.utils import get_file_name_from_path, convert_eeg_events_to_list
from src.code.eeg import EEG_DATA
from src.code.audio import AUDIO_DATA
from src.gui.mappingDisplay1 import EEGAudioApp
from src.utils import EEG_AUDIO_DATA
from src.gui.utils import text_box_style, label_style, button_style, combobox_style
import config


class LoadEEGThread(QThread):
    finished = pyqtSignal(object)
    error = pyqtSignal(str)

    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path

    def run(self):
        try:
            eeg_data = EEG_DATA(self.file_path)
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
            audio_data = AUDIO_DATA(self.file_path)
            self.finished.emit(audio_data)
        except Exception as e:
            self.error.emit(str(e))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.EEG_DATA = None
        self.AUDIO_DATA = None
        self.mappingDisplay = None
        self.setWindowTitle('EEG_AUDIO_Anotator')
        self.setGeometry(500, 300, 1200, 300)
        self.setWindowIcon(QIcon(config.WINDOW_ICON_PATH))  
        self.setStyleSheet("background-color: #f0f0f0;")

        self.background_label = QLabel(self)
        self.background_label.setGeometry(0, 0, self.width(), self.height())
        pixmap = QPixmap(config.BACKGROUND_IMAGE_PATH)
        self.background_label.setPixmap(pixmap)
        self.background_label.setScaledContents(True)
        self.background_label.setAlignment(Qt.AlignCenter)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QHBoxLayout()
        central_widget.setLayout(self.main_layout)

        right_left_widget_style = "border: 2px solid #ccc; border-radius: 5px; background-color: #f0f0f0;"


        ##############################################################################################
        ######################################Left Layout Sections####################################

        self.left_layout = QVBoxLayout()
        self.left_layout_widget = self.wrap_layout_in_widget(self.left_layout)
        self.left_layout_widget.setStyleSheet(right_left_widget_style)

        
        # Left Layout Sections
        self.left_layout_section_1 = QHBoxLayout()
        self.left_layout_section_1_widget = self.wrap_layout_in_widget(self.left_layout_section_1)
        self.left_layout_section_2 = QHBoxLayout()
        self.left_layout_section_2_widget = self.wrap_layout_in_widget(self.left_layout_section_2)
        self.left_layout_section_3 = QHBoxLayout()
        self.left_layout_section_3_widget = self.wrap_layout_in_widget(self.left_layout_section_3)
        self.left_layout_section_4 = QHBoxLayout()
        self.left_layout_section_4_widget = self.wrap_layout_in_widget(self.left_layout_section_4)
        self.left_layout_section_4_2= QHBoxLayout()
        self.left_layout_section_4_2_widget = self.wrap_layout_in_widget(self.left_layout_section_4_2)
        self.left_layout_section_5 = QHBoxLayout()
        self.left_layout_section_5_widget = self.wrap_layout_in_widget(self.left_layout_section_5)
        self.left_layout_section_6 = QHBoxLayout()
        self.left_layout_section_6_widget = self.wrap_layout_in_widget(self.left_layout_section_6)
        self.left_layout_section_7 = QVBoxLayout()
        self.left_layout_section_7_widget = self.wrap_layout_in_widget(self.left_layout_section_7)
        self.left_layout_section_8 = QVBoxLayout()
        self.left_layout_section_8_widget = self.wrap_layout_in_widget(self.left_layout_section_8)



        # Add section  to left layout widget
        self.left_layout.addWidget(self.left_layout_section_1_widget)
        self.left_layout.addWidget(self.left_layout_section_2_widget)
        self.left_layout.addWidget(self.left_layout_section_3_widget)
        self.left_layout.addWidget(self.left_layout_section_4_widget)
        self.left_layout.addWidget(self.left_layout_section_4_2_widget)
        self.left_layout.addWidget(self.left_layout_section_5_widget)
        self.left_layout.addWidget(self.left_layout_section_6_widget)
        self.left_layout.addWidget(self.left_layout_section_7_widget)
        self.left_layout.addWidget(self.left_layout_section_8_widget)
        
        ####################Adding Labels, Buttons, and ComboBoxes##################

        ###############################left Layout Rows############################
        #***********************************ROW 1***********************************
        header_label = QLabel()
        header_label.setText('<center><b><font color="#8B0000" size="5"><u> EEG (*.edf) FILE INFORMATION<u></font></b></center>')
        self.left_layout_section_1.addWidget(header_label)

        #***********************************ROW 2***********************************
        self.eeg_file_name_label = QLabel('EEG (.edf) File :')
        self.eeg_file_name_label.setStyleSheet(label_style)
        self.eeg_file_name_textbox = QLineEdit('Filename will appear here when you successfully select the .edf file')
        self.eeg_file_name_textbox.setReadOnly(True)
        self.eeg_file_name_textbox.setStyleSheet(text_box_style)
        self.eeg_select_file_button = QPushButton('Select File')
        self.eeg_select_file_button.setStyleSheet(button_style)
        self.eeg_load_file_button = QPushButton('Load File')
        self.eeg_load_file_button.setStyleSheet(button_style)

        self.left_layout_section_2.addWidget(self.eeg_file_name_label)
        self.left_layout_section_2.addWidget(self.eeg_file_name_textbox)
        self.left_layout_section_2.addWidget(self.eeg_select_file_button)
        self.left_layout_section_2.addWidget(self.eeg_load_file_button)

        #***********************************ROW 3***********************************
        self.eeg_sampling_freq_label = QLabel('Sampling Frequency :')
        self.eeg_sampling_freq_label.setStyleSheet(label_style)
        self.eeg_sampling_freq_text = QLineEdit('')
        self.eeg_sampling_freq_text.setStyleSheet(text_box_style)
        self.eeg_sampling_freq_text.setReadOnly(True)
        self.eeg_duration_label = QLabel('Duration: ')
        self.eeg_duration_label.setStyleSheet(label_style)
        self.eeg_duration_text = QLineEdit('')
        self.eeg_duration_text.setStyleSheet(text_box_style)
        self.eeg_duration_text.setReadOnly(True)

        self.left_layout_section_3.addWidget(self.eeg_sampling_freq_label)
        self.left_layout_section_3.addWidget(self.eeg_sampling_freq_text)
        self.left_layout_section_3.addWidget(self.eeg_duration_label)
        self.left_layout_section_3.addWidget(self.eeg_duration_text)

        #***********************************ROW 4**********************************
        self.eeg_n_channels_label = QLabel('No. Channels :')        
        self.eeg_n_channels_label.setStyleSheet(label_style)
        self.eeg_n_channels_text = QLineEdit('')
        self.eeg_n_channels_text.setStyleSheet(text_box_style)
        self.eeg_n_channels_text.setReadOnly(True)
        self.eeg_n_bad_channels_label = QLabel('No. bad channels')
        self.eeg_n_bad_channels_label.setStyleSheet(label_style)
        self.eeg_n_bad_channels_text = QLineEdit('')
        self.eeg_n_bad_channels_text.setStyleSheet(text_box_style)
        self.eeg_n_bad_channels_text.setReadOnly(True)

        self.left_layout_section_4.addWidget(self.eeg_n_channels_label)
        self.left_layout_section_4.addWidget(self.eeg_n_channels_text)
        self.left_layout_section_4.addWidget(self.eeg_n_bad_channels_label)
        self.left_layout_section_4.addWidget(self.eeg_n_bad_channels_text)

        #***********************************ROW 4_2***********************************
        self.eeg_start_time_label = QLabel('Start Time :')
        self.eeg_start_time_label.setStyleSheet(label_style)
        self.eeg_start_time_text = QLineEdit('')
        self.eeg_start_time_text.setStyleSheet(text_box_style)
        self.eeg_start_time_text.setReadOnly(True)
        self.eeg_end_time_label = QLabel('End Time :')
        self.eeg_end_time_label.setStyleSheet(label_style)
        self.eeg_end_time_text = QLineEdit('')
        self.eeg_end_time_text.setStyleSheet(text_box_style)
        self.eeg_end_time_text.setReadOnly(True)

        self.left_layout_section_4_2.addWidget(self.eeg_start_time_label)
        self.left_layout_section_4_2.addWidget(self.eeg_start_time_text)
        self.left_layout_section_4_2.addWidget(self.eeg_end_time_label)
        self.left_layout_section_4_2.addWidget(self.eeg_end_time_text)
        

        #***********************************ROW 5**********************************        
        self.eeg_n_triggers_label = QLabel('No. Triggers :')
        self.eeg_n_triggers_label.setStyleSheet(label_style)
        self.eeg_n_triggers_text = QLineEdit('')
        self.eeg_n_triggers_text.setStyleSheet(text_box_style)
        self.eeg_n_triggers_text.setReadOnly(True)
        self.eeg_n_events_label = QLabel('No. Events:')
        self.eeg_n_events_label.setStyleSheet(label_style)
        self.eeg_n_events_text = QLineEdit('')
        self.eeg_n_events_text.setStyleSheet(text_box_style)
        self.eeg_n_events_text.setReadOnly(True)

        self.left_layout_section_5.addWidget(self.eeg_n_triggers_label)
        self.left_layout_section_5.addWidget(self.eeg_n_triggers_text)
        self.left_layout_section_5.addWidget(self.eeg_n_events_label)
        self.left_layout_section_5.addWidget(self.eeg_n_events_text)


        #***********************************ROW 6**********************************
        self.eeg_event_labels_label = QLabel('Event Labels :')
        self.eeg_event_labels_label.setStyleSheet(label_style)
        self.eeg_event_labels_text = QLineEdit('')
        self.eeg_event_labels_text.setStyleSheet(text_box_style)
        self.eeg_event_labels_text.setReadOnly(True)
        self.eeg_event_duration_label = QLabel('Events Duration :')
        self.eeg_event_duration_label.setStyleSheet(label_style)
        self.eeg_event_duration_text = QLineEdit('')
        self.eeg_event_duration_text.setStyleSheet(text_box_style)
        self.eeg_event_duration_text.setReadOnly(True)

        self.left_layout_section_6.addWidget(self.eeg_event_labels_label)
        self.left_layout_section_6.addWidget(self.eeg_event_labels_text)
        self.left_layout_section_6.addWidget(self.eeg_event_duration_label)
        self.left_layout_section_6.addWidget(self.eeg_event_duration_text)


        #***********************************ROW 7**********************************
        self.eeg_triggers_list_label = QLabel('Triggers:')
        self.eeg_triggers_list_label.setStyleSheet(label_style)
        self.eeg_triggers_list_widget = QListWidget()
        self.eeg_triggers_list_widget.setStyleSheet("background-color: #fff;")
        self.eeg_triggers_list_widget.setMaximumHeight(100)

        self.left_layout_section_7.addWidget(self.eeg_triggers_list_label)
        self.left_layout_section_7.addWidget(self.eeg_triggers_list_widget)

        #***********************************ROW 8**********************************
        self.start_mapping_display_button = QPushButton('Open Mapping Display Window')
        self.start_mapping_display_button.setStyleSheet(button_style)
        self.left_layout_section_8.addWidget(self.start_mapping_display_button)


        # Set up connections for EEG buttons
        self.eeg_select_file_button.clicked.connect(self.select_eeg_file)
        self.eeg_load_file_button.clicked.connect(self.load_eeg_file)
        self.start_mapping_display_button.clicked.connect(self.open_mapping_display)


        ##############################################################################################
        ######################################Right Layout Sections###################################

        self.right_layout = QVBoxLayout()
        self.right_layout_widget = self.wrap_layout_in_widget(self.right_layout)
        self.right_layout_widget.setStyleSheet(right_left_widget_style)

        # Right Layout Sections
        self.right_layout_section_1 = QHBoxLayout()
        self.right_layout_section_1_widget = self.wrap_layout_in_widget(self.right_layout_section_1)
        self.right_layout_section_2 = QHBoxLayout()
        self.right_layout_section_2_widget = self.wrap_layout_in_widget(self.right_layout_section_2)
        self.right_layout_section_3 = QHBoxLayout()
        self.right_layout_section_3_widget = self.wrap_layout_in_widget(self.right_layout_section_3)
        self.right_layout_section_4 = QHBoxLayout()
        self.right_layout_section_4_widget = self.wrap_layout_in_widget(self.right_layout_section_4)
        self.right_layout_section_5 = QHBoxLayout()
        self.right_layout_section_5_widget = self.wrap_layout_in_widget(self.right_layout_section_5)
        self.right_layout_section_6 = QHBoxLayout()
        self.right_layout_section_6_widget = self.wrap_layout_in_widget(self.right_layout_section_6)

        # Add sections to right layout widget
        self.right_layout.addWidget(self.right_layout_section_1_widget)
        self.right_layout.addWidget(self.right_layout_section_2_widget)
        self.right_layout.addWidget(self.right_layout_section_3_widget)
        self.right_layout.addWidget(self.right_layout_section_4_widget)
        self.right_layout.addWidget(self.right_layout_section_5_widget)
        self.right_layout.addWidget(self.right_layout_section_6_widget)

        # Adding Labels, Buttons, and ComboBoxes
        ###############################Right Layout Rows############################
        #***********************************ROW 1***********************************
        header_label = QLabel()
        header_label.setText('<center><b><font color="#8B0000" size="5"><u> AUDIO (*.wav) FILE INFORMATION<u></font></b></center>')
        self.right_layout_section_1.addWidget(header_label)

        #***********************************ROW 2***********************************
        self.audio_file_name_label = QLabel('Audio (.wav) File :')
        self.audio_file_name_label.setStyleSheet(label_style)
        self.audio_file_name_textbox = QLineEdit('Filename will appear here when you successfully select the .wav file')
        self.audio_file_name_textbox.setReadOnly(True)
        self.audio_file_name_textbox.setStyleSheet(text_box_style)
        self.audio_select_file_button = QPushButton('Select File')
        self.audio_select_file_button.setStyleSheet(button_style)
        self.audio_load_file_button = QPushButton('Load File')
        self.audio_load_file_button.setStyleSheet(button_style)

        self.right_layout_section_2.addWidget(self.audio_file_name_label)
        self.right_layout_section_2.addWidget(self.audio_file_name_textbox)
        self.right_layout_section_2.addWidget(self.audio_select_file_button)
        self.right_layout_section_2.addWidget(self.audio_load_file_button)


        #***********************************ROW 3***********************************
        self.audio_sampling_freq_label = QLabel('Sampling Frequency :')
        self.audio_sampling_freq_label.setStyleSheet(label_style)
        self.audio_sampling_freq_text = QLineEdit('')
        self.audio_sampling_freq_text.setReadOnly(True)
        self.audio_sampling_freq_text.setStyleSheet(text_box_style)
        self.audio_duration_label = QLabel('Duration :')
        self.audio_duration_label.setStyleSheet(label_style)
        self.audio_duration_text = QLineEdit('')
        self.audio_duration_text.setReadOnly(True)
        self.audio_duration_text.setStyleSheet(text_box_style)

        self.right_layout_section_3.addWidget(self.audio_sampling_freq_label)
        self.right_layout_section_3.addWidget(self.audio_sampling_freq_text)
        self.right_layout_section_3.addWidget(self.audio_duration_label)
        self.right_layout_section_3.addWidget(self.audio_duration_text)

        #***********************************ROW 4***********************************
        self.audio_n_markers_label = QLabel('No. of Markers :')
        self.audio_n_markers_label.setStyleSheet(label_style)
        self.audio_n_markers_text = QLineEdit('')
        self.audio_n_markers_text.setReadOnly(True)
        self.audio_n_markers_text.setStyleSheet(text_box_style)
        self.audio_markers_start_label = QLabel('Markers Start Times :')
        self.audio_markers_start_label.setStyleSheet(label_style)
        self.audio_markers_start_text = QLineEdit('')
        self.audio_markers_start_text.setReadOnly(True)
        self.audio_markers_start_text.setStyleSheet(text_box_style)

        self.right_layout_section_4.addWidget(self.audio_n_markers_label)
        self.right_layout_section_4.addWidget(self.audio_n_markers_text)
        self.right_layout_section_4.addWidget(self.audio_markers_start_label)
        self.right_layout_section_4.addWidget(self.audio_markers_start_text)

        #***********************************ROW 5***********************************
        self.audio_markers_end_label = QLabel('Markers End Times :')
        self.audio_markers_end_label.setStyleSheet(label_style)
        self.audio_markers_end_text = QLineEdit('')
        self.audio_markers_end_text.setReadOnly(True)
        self.audio_markers_end_text.setStyleSheet(text_box_style)
        self.audio_markers_duration_label = QLabel('Markers Duration :')
        self.audio_markers_duration_label.setStyleSheet(label_style)
        self.audio_markers_duration_text = QLineEdit('')
        self.audio_markers_duration_text.setReadOnly(True)
        self.audio_markers_duration_text.setStyleSheet(text_box_style)

        self.right_layout_section_5.addWidget(self.audio_markers_end_label)
        self.right_layout_section_5.addWidget(self.audio_markers_end_text)
        self.right_layout_section_5.addWidget(self.audio_markers_duration_label)
        self.right_layout_section_5.addWidget(self.audio_markers_duration_text)

        #***********************************ROW 6***********************************
        self.audio_start_time_label = QLabel('Start Time :')
        self.audio_start_time_label.setStyleSheet(label_style)
        self.audio_start_time_text = QLineEdit('')
        self.audio_start_time_text.setReadOnly(True)
        self.audio_start_time_text.setStyleSheet(text_box_style)
        self.audio_end_time_label = QLabel('End Time :')
        self.audio_end_time_label.setStyleSheet(label_style)
        self.audio_end_time_text = QLineEdit('')
        self.audio_end_time_text.setReadOnly(True)
        self.audio_end_time_text.setStyleSheet(text_box_style)
        self.audio_duration_full_label = QLabel('Duration :')
        self.audio_duration_full_label.setStyleSheet(label_style)
        self.audio_duration_full_text = QLineEdit('')
        self.audio_duration_full_text.setReadOnly(True)
        self.audio_duration_full_text.setStyleSheet(text_box_style)

        self.right_layout_section_6.addWidget(self.audio_start_time_label)
        self.right_layout_section_6.addWidget(self.audio_start_time_text)
        self.right_layout_section_6.addWidget(self.audio_end_time_label)
        self.right_layout_section_6.addWidget(self.audio_end_time_text)
        self.right_layout_section_6.addWidget(self.audio_duration_full_label)
        self.right_layout_section_6.addWidget(self.audio_duration_full_text)
        
        # Set up connections for Audio buttons
        self.audio_select_file_button.clicked.connect(self.select_audio_file)
        self.audio_load_file_button.clicked.connect(self.load_audio_file)

        # Add left and right layout widgets to the main layout
        self.main_layout.addWidget(self.left_layout_widget)
        self.main_layout.addWidget(self.right_layout_widget)


    def wrap_layout_in_widget(self, layout):
        widget = QWidget()
        widget.setLayout(layout)
        return widget

    def select_eeg_file(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Select EEG File", "", "EDF Files (*.edf);;All Files (*)", options=options)
        if file_path:
            self.eeg_file_name_textbox.setText(get_file_name_from_path(file_path))

    def select_audio_file(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Audio File", "", "WAV Files (*.wav);;All Files (*)", options=options)
        if file_path:
            self.audio_file_name_textbox.setText(get_file_name_from_path(file_path))

    def load_eeg_file(self):
        file_path = self.eeg_file_name_textbox.text()
        if not file_path:
            QMessageBox.warning(self, 'Warning', 'Please select an EEG file first.')
            return

        self.eeg_thread = LoadEEGThread(file_path)
        self.eeg_thread.finished.connect(self.on_eeg_loaded)
        self.eeg_thread.error.connect(self.on_eeg_load_error)
        self.eeg_thread.start()

    def on_eeg_loaded(self, eeg_data):
        self.EEG_DATA = eeg_data

        self.eeg_sampling_freq_text.setText(str(eeg_data.sampling_frequency))
        self.eeg_duration_text.setText(str(eeg_data.duration))
        self.eeg_n_channels_text.setText(str(eeg_data.n_channels))
        self.eeg_n_bad_channels_text.setText(str(len(eeg_data.bad_channels)))
        self.eeg_start_time_text.setText(eeg_data.start_time)
        self.eeg_end_time_text.setText(eeg_data.end_time)
        self.eeg_n_triggers_text.setText(str(eeg_data.n_triggers))
        self.eeg_n_events_text.setText(str(eeg_data.n_events))
        self.eeg_event_labels_text.setText(', '.join(eeg_data.event_labels))
        self.eeg_event_duration_text.setText(str(eeg_data.event_duration))

        triggers_list = convert_eeg_events_to_list(eeg_data.triggers)
        self.eeg_triggers_list_widget.clear()
        self.eeg_triggers_list_widget.addItems(triggers_list)

    def on_eeg_load_error(self, error_message):
        QMessageBox.critical(self, 'Error', f'Failed to load EEG file: {error_message}')

    def load_audio_file(self):
        file_path = self.audio_file_name_textbox.text()
        if not file_path:
            QMessageBox.warning(self, 'Warning', 'Please select an audio file first.')
            return

        self.audio_thread = LoadAudioThread(file_path)
        self.audio_thread.finished.connect(self.on_audio_loaded)
        self.audio_thread.error.connect(self.on_audio_load_error)
        self.audio_thread.start()

    def on_audio_loaded(self, audio_data):
        self.AUDIO_DATA = audio_data

        self.audio_sampling_freq_text.setText(str(audio_data.sampling_frequency))
        self.audio_duration_text.setText(str(audio_data.duration))
        self.audio_n_markers_text.setText(str(audio_data.n_markers))
        self.audio_markers_start_text.setText(', '.join(map(str, audio_data.markers_start)))
        self.audio_markers_end_text.setText(', '.join(map(str, audio_data.markers_end)))
        self.audio_markers_duration_text.setText(str(audio_data.markers_duration))
        self.audio_start_time_text.setText(audio_data.start_time)
        self.audio_end_time_text.setText(audio_data.end_time)
        self.audio_duration_full_text.setText(str(audio_data.duration))

    def on_audio_load_error(self, error_message):
        QMessageBox.critical(self, 'Error', f'Failed to load audio file: {error_message}')

    def open_mapping_display(self):
        if self.EEG_DATA is None or self.AUDIO_DATA is None:
            QMessageBox.warning(self, 'Warning', 'Please load both EEG and audio files before opening the mapping display.')
            return

        eeg_audio_data = EEG_AUDIO_DATA(self.EEG_DATA, self.AUDIO_DATA)
        self.mappingDisplay = EEGAudioApp(eeg_audio_data)
        self.mappingDisplay.show()


