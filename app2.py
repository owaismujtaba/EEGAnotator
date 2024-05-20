from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout,
    QVBoxLayout, QLabel, QPushButton, QComboBox, QFileDialog, 
    QMessageBox, QSizePolicy, QLineEdit, QFrame
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
        self.setGeometry(500, 300, 800, 300)  
        self.setStyleSheet("background-color: lightgray;")

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QHBoxLayout()
        central_widget.setLayout(self.main_layout)

        right_left_widget_style = "border: 0px solid black; border-radius: 5px; background-color: lightgrey;"
        text_box_style = """
                        color: "#800000";
                        border: 2px solid black;
                        border-radius: 5px;
                        background-color: lightgrey;
                        font-family: Arial, sans-serif;
                        font-weight: bold;
                        font-size: 14px;
                    """        
        label_style = """
                    font-weight: bold; 
                    border: 0px solid black; 
                    border-radius: 5px;
                    font-size: 14px;
                    font-weight: bold
                """
        button_style = """
                QPushButton {
                    background-color: lightcoral;
                    color: black;
                    border-radius: 5px;
                    padding: 5px;
                    border: 1px solid black;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: lightblue;
                }
            """
        combobox_style = """
                    color: darkbrown; 
                    font-weight: bold; 
                    background-color: #ff6666; 
                    border: 2px solid black; 
                    border-radius: 5px
                """


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
        self.left_layout_section_5 = QHBoxLayout()
        self.left_layout_section_5_widget = self.wrap_layout_in_widget(self.left_layout_section_5)
        self.left_layout_section_6 = QHBoxLayout()
        self.left_layout_section_6_widget = self.wrap_layout_in_widget(self.left_layout_section_6)

        # Add section  to left layout widget
        self.left_layout.addWidget(self.left_layout_section_1_widget)
        self.left_layout.addWidget(self.left_layout_section_2_widget)
        self.left_layout.addWidget(self.left_layout_section_3_widget)
        self.left_layout.addWidget(self.left_layout_section_4_widget)
        self.left_layout.addWidget(self.left_layout_section_5_widget)
        self.left_layout.addWidget(self.left_layout_section_6_widget)

        ##############################################################################################
        ###################################### Right Layout Sections####################################

        self.right_layout = QVBoxLayout()
        self.right_layout_widget = self.wrap_layout_in_widget(self.right_layout)
        self.right_layout_widget.setStyleSheet(right_left_widget_style)

        #Right Layout Sections
        self.right_layout_section_1 = QHBoxLayout()
        self.right_layout_section_1_widget = self.wrap_layout_in_widget(self.right_layout_section_1)
        self.right_layout_section_2 = QHBoxLayout()
        self.right_layout_section_2_widget = self.wrap_layout_in_widget(self.right_layout_section_2)
        self.right_layout_section_3 = QHBoxLayout()
        self.right_layout_section_3_widget = self.wrap_layout_in_widget(self.right_layout_section_3)
        self.right_layout_section_4 = QHBoxLayout()
        self.right_layout_section_4_widget = self.wrap_layout_in_widget(self.right_layout_section_4)
        
        # Add section  to right layout widget
        self.right_layout.addWidget(self.right_layout_section_1_widget)
        self.right_layout.addWidget(self.right_layout_section_2_widget)
        self.right_layout.addWidget(self.right_layout_section_3_widget)
        self.right_layout.addWidget(self.right_layout_section_4_widget)


        # Add both left and right layout widgets to the main layout
        self.main_layout.addWidget(self.left_layout_widget)
        self.main_layout.addWidget(self.right_layout_widget)


        ####################Adding Lables, Buttons and ComboBoxes##################

        ###############################left Layout Rows############################
        #***********************************ROW 1***********************************
        header_label = QLabel()
        #<span style="text-decoration: underline; text-decoration-thickness: 3px;">This is an underlined label with increased thickness</span>')

        header_label.setText('<center><b><font color="#8B0000" size="10"><u> EEG (*.edf) FILE INFORMATION<u></font></b></center>')
        self.left_layout_section_1.addWidget(header_label)

        #***********************************ROW 2***********************************
        self.eeg_file_name_label = QLabel('EEG (.edf) File :')
        self.eeg_file_name_label.setStyleSheet(label_style)
        self.eeg_file_name_textbox = QLineEdit('Filename will appear hear when you sucessfully select the xdf file')
        self.eeg_file_name_textbox.setReadOnly(True)
        self.eeg_file_name_textbox.setStyleSheet(text_box_style)
        self.eeg_select_file_button = QPushButton('Select File')
        self.eeg_select_file_button.setStyleSheet(button_style)

        self.left_layout_section_2.addWidget(self.eeg_file_name_label)
        self.left_layout_section_2.addWidget(self.eeg_file_name_textbox)
        self.left_layout_section_2.addWidget(self.eeg_select_file_button)

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

        #***********************************ROW 5**********************************
        self.eeg_n_triggers_label = QLabel('No. Triggers :')
        self.eeg_n_triggers_label.setStyleSheet(label_style)
        self.eeg_n_triggers_text = QLineEdit('')
        self.eeg_n_triggers_text.setStyleSheet(text_box_style)
        self.eeg_n_triggers_text.setReadOnly(True)
        self.eeg_interruption_label = QLabel('Interruptions Flag: ')
        self.eeg_interruption_label.setStyleSheet(label_style)
        self.eeg_interruptions_text = QLineEdit('')
        self.eeg_interruptions_text.setStyleSheet(text_box_style)
        self.eeg_interruptions_text.setReadOnly(True)

        self.left_layout_section_5.addWidget(self.eeg_n_triggers_label)
        self.left_layout_section_5.addWidget(self.eeg_n_triggers_text)
        self.left_layout_section_5.addWidget(self.eeg_interruption_label)
        self.left_layout_section_5.addWidget(self.eeg_interruptions_text)


        #***********************************ROW 6**********************************
        self.eeg_channels_cbox = QComboBox()
        self.eeg_channels_cbox.addItem('Channels')
        self.eeg_channels_cbox.setStyleSheet(combobox_style)
        self.eeg_bad_channels_cbox = QComboBox()
        self.eeg_bad_channels_cbox.addItem('Bad Channels')
        self.eeg_bad_channels_cbox.setStyleSheet(combobox_style)
        self.eeg_events_cbox = QComboBox()
        self.eeg_events_cbox.setStyleSheet(text_box_style)

        self.left_layout_section_6.addWidget(self.eeg_channels_cbox)
        self.left_layout_section_6.addWidget(self.eeg_bad_channels_cbox)
        self.left_layout_section_6.addWidget(self.eeg_events_cbox)






    def wrap_layout_in_widget(self, layout):
        widget = QWidget()
        widget.setLayout(layout)
        return widget

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
