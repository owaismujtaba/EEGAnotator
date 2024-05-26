from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout,
    QVBoxLayout, QLabel, QPushButton, QComboBox, QFileDialog, 
    QMessageBox,  QLineEdit,  QListWidget
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal

from src.gui.utils import get_file_name_from_path, convert_eeg_events_to_list
from src.code.eeg import EEG_DATA
from src.code.audio import AUDIO_DATA
from src.gui.mappingDisplay1 import EEGAudioApp
from src.utils import EEG_AUDIO_DATA
from src.gui.utils import text_box_style, label_style, button_style, combobox_style

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
        self.mappingDisplay = EEGAudioApp(self.EEG_DATA)
        self.setWindowTitle('DeepRESTORE')
        self.setGeometry(500, 300, 1200, 300)  
        self.setStyleSheet("background-color: #f0f0f0;")

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
        self.eeg_file_name_textbox = QLineEdit('Filename will appear hear when you successfully select the xdf file')
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
        self.eeg_bad_channels_cbox = QComboBox()
        self.eeg_bad_channels_cbox.addItem('Bad Channels')
        self.eeg_bad_channels_cbox.setStyleSheet(combobox_style)
        self.eeg_events_cbox = QComboBox()
        self.eeg_events_cbox.addItem('Event Name:       Start Time:   End Time:  Start Index:     End Index:   Duration')
        self.eeg_events_cbox.setStyleSheet(combobox_style)

        self.left_layout_section_6.addWidget(self.eeg_bad_channels_cbox)
        self.left_layout_section_6.addWidget(self.eeg_events_cbox)


        #***********************************ROW 7**********************************
        self.channels_list_layout = QHBoxLayout()
        self.channels_list_layout_widget = self.wrap_layout_in_widget(self.channels_list_layout)
        self.channels_button_layout = QVBoxLayout()
        self.channels_button_layout_widget = self.wrap_layout_in_widget(self.channels_button_layout)

        self.eeg_channels_available_list = QListWidget()
        self.eeg_channels_selected_list = QListWidget()

        self.eeg_channel_add_btn = QPushButton('Add >>')
        self.eeg_channel_remove_btn = QPushButton('<< Remove')
        self.eeg_channel_add_all_btn = QPushButton('Add All >>')
        self.eeg_channel_remove_all_btn = QPushButton('<< Remove All')

        self.channels_button_layout.addWidget(self.eeg_channel_add_btn)
        self.channels_button_layout.addWidget(self.eeg_channel_remove_btn)
        self.channels_button_layout.addWidget(self.eeg_channel_add_all_btn)
        self.channels_button_layout.addWidget(self.eeg_channel_remove_all_btn)
        self.channels_button_layout.addStretch()

        self.channels_button_widget = QWidget()
        self.channels_button_widget.setLayout(self.channels_button_layout)

        self.channels_list_layout.addWidget(self.eeg_channels_available_list)
        self.channels_list_layout.addWidget(self.channels_button_widget)
        self.channels_list_layout.addWidget(self.eeg_channels_selected_list)

        self.left_layout_section_7.addWidget(self.channels_list_layout_widget)
        
        #***********************************ROW 8**********************************
        self.visualize_eeg_btn = QPushButton('Visualize selected channels')
        self.visualize_eeg_btn.setStyleSheet(button_style)

        self.left_layout_section_8.addWidget(self.visualize_eeg_btn)
        

        ##############################################################################################
        ###################################### Right Layout Sections####################################

        self.right_layout = QVBoxLayout()
        self.right_layout_widget = self.wrap_layout_in_widget(self.right_layout)
        self.right_layout_widget.setStyleSheet(right_left_widget_style)

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
        self.right_layout_section_7 = QHBoxLayout()
        self.right_layout_section_7_widget = self.wrap_layout_in_widget(self.right_layout_section_7)
        self.right_layout_section_8 = QVBoxLayout()
        self.right_layout_section_8_widget = self.wrap_layout_in_widget(self.right_layout_section_8)




        self.right_layout.addWidget(self.right_layout_section_1_widget)
        self.right_layout.addWidget(self.right_layout_section_2_widget)
        self.right_layout.addWidget(self.right_layout_section_3_widget)
        self.right_layout.addWidget(self.right_layout_section_4_widget)
        self.right_layout.addWidget(self.right_layout_section_5_widget)
        self.right_layout.addWidget(self.right_layout_section_6_widget)
        self.right_layout.addWidget(self.right_layout_section_7_widget)
        self.right_layout.addWidget(self.right_layout_section_8_widget)




        ####################Adding Labels, Buttons, and ComboBoxes##################
        ###############################left Layout Rows############################
        
        #***********************************ROW 1***********************************
        header_label = QLabel()
        header_label.setText('<center><b><font color="#8B0000" size="5"><u> AUDIO (*.xdf) FILE INFORMATION<u></font></b></center>')
        self.right_layout_section_1.addWidget(header_label)

        #***********************************ROW 2***********************************
        self.audio_file_name_label = QLabel('AUDIO (.edf) File :')
        self.audio_file_name_label.setStyleSheet(label_style)
        self.audio_file_name_textbox = QLineEdit('Filename will appear hear when you successfully select the xdf file')
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
        self.audio_sampling_freq_text.setStyleSheet(text_box_style)
        self.audio_sampling_freq_text.setReadOnly(True)
        self.audio_duration_label = QLabel('Duration: ')
        self.audio_duration_label.setStyleSheet(label_style)
        self.audio_duration_text = QLineEdit('')
        self.audio_duration_text.setStyleSheet(text_box_style)
        self.audio_duration_text.setReadOnly(True)

        self.right_layout_section_3.addWidget(self.audio_sampling_freq_label)
        self.right_layout_section_3.addWidget(self.audio_sampling_freq_text)
        self.right_layout_section_3.addWidget(self.audio_duration_label)
        self.right_layout_section_3.addWidget(self.audio_duration_text)
        

        #***********************************ROW 4***********************************
        self.audio_n_markers_label = QLabel('No. Markers :')
        self.audio_n_markers_label.setStyleSheet(label_style)
        self.audio_n_markers_text = QLineEdit('')
        self.audio_n_markers_text.setStyleSheet(text_box_style)
        self.audio_n_markers_text.setReadOnly(True)
        self.audio_markers_start_label = QLabel('Markers Start Time :')
        self.audio_markers_start_label.setStyleSheet(label_style)
        self.audio_markers_start_text = QLineEdit('')
        self.audio_markers_start_text.setStyleSheet(text_box_style)
        self.audio_markers_start_text.setReadOnly(True)

        self.right_layout_section_4.addWidget(self.audio_n_markers_label)
        self.right_layout_section_4.addWidget(self.audio_n_markers_text)
        self.right_layout_section_4.addWidget(self.audio_markers_start_label)
        self.right_layout_section_4.addWidget(self.audio_markers_start_text)

        

        #***********************************ROW 5***********************************
        self.audio_markers_end_label = QLabel('Markers End Time :')
        self.audio_markers_end_label.setStyleSheet(label_style)
        self.audio_markers_end_text = QLineEdit('')
        self.audio_markers_end_text.setStyleSheet(text_box_style)
        self.audio_markers_end_text.setReadOnly(True)
        self.audio_markers_duration_label = QLabel('Markers Duration :')
        self.audio_markers_duration_label.setStyleSheet(label_style)
        self.audio_markers_duration_text = QLineEdit('')
        self.audio_markers_duration_text.setStyleSheet(text_box_style)
        self.audio_markers_duration_text.setReadOnly(True)

        self.right_layout_section_5.addWidget(self.audio_markers_end_label)
        self.right_layout_section_5.addWidget(self.audio_markers_end_text)
        self.right_layout_section_5.addWidget(self.audio_markers_duration_label)
        self.right_layout_section_5.addWidget(self.audio_markers_duration_text)


        #***********************************ROW 6***********************************
        self.audio_start_time_label = QLabel('Audio Start Time :')
        self.audio_start_time_label.setStyleSheet(label_style)
        self.audio_start_time_text = QLineEdit('')
        self.audio_start_time_text.setStyleSheet(text_box_style)
        self.audio_start_time_text.setReadOnly(True)
        self.audio_end_time_label = QLabel('Audio End Time :')
        self.audio_end_time_label.setStyleSheet(label_style)
        self.audio_end_time_text = QLineEdit('')
        self.audio_end_time_text.setStyleSheet(text_box_style)
        self.audio_end_time_text.setReadOnly(True)

        self.right_layout_section_6.addWidget(self.audio_start_time_label)
        self.right_layout_section_6.addWidget(self.audio_start_time_text)
        self.right_layout_section_6.addWidget(self.audio_end_time_label)
        self.right_layout_section_6.addWidget(self.audio_end_time_text)


        #***********************************ROW 7***********************************
        self.audio_duration_full_label = QLabel('Audio Duration :')
        self.audio_duration_full_label.setStyleSheet(label_style)
        self.audio_duration_full_text = QLineEdit('')
        self.audio_duration_full_text.setStyleSheet(text_box_style)
        self.audio_duration_full_text.setReadOnly(True)
        
        self.right_layout_section_7.addWidget(self.audio_duration_full_label)
        self.right_layout_section_7.addWidget(self.audio_duration_full_text)

        #***********************************ROW 8**********************************
        self.map_audio_and_eeg_button = QPushButton('Start Mapping')
        self.map_audio_and_eeg_button.setStyleSheet(button_style)
        

        self.right_layout_section_8.addWidget(self.map_audio_and_eeg_button)
        



        ################Adding right and left layouts to main layout###############
        ###########################################################################
        self.main_layout.addWidget(self.left_layout_widget)
        self.main_layout.addWidget(self.right_layout_widget)



        ################Function connections for buttons###############
        ###########################################################################


        self.eeg_select_file_button.clicked.connect(self.browse_eeg_file)
        self.eeg_load_file_button.clicked.connect(self.load_edf_file)
        self.eeg_channel_add_btn.clicked.connect(self.add_item)
        self.eeg_channel_remove_btn.clicked.connect(self.remove_item)
        self.eeg_channel_remove_all_btn.clicked.connect(self.remove_all_items)
        self.eeg_channel_add_all_btn.clicked.connect(self.add_all_items)

        self.audio_select_file_button.clicked.connect(self.browse_xdf_file)
        self.audio_load_file_button.clicked.connect(self.load_xdf_file)

        self.visualize_eeg_btn.clicked.connect(self.visualize_eeg_channels)
        self.map_audio_and_eeg_button.clicked.connect(self.display_mapping_page)


    def display_mapping_page(self):
        #if self.EEG_DATA:
            #eeg_audio_data = EEG_AUDIO_DATA(self.EEG_DATA, self.AUDIO_DATA)
            self.hide()
            self.mapping_page_viewer = EEGAudioApp(self.EEG_DATA)
            self.mapping_page_viewer.about_to_close.connect(self.show_main_window)        
            self.mapping_page_viewer.show()
        #else:
            #pass

    def show_main_window(self):
        self.show()




    def visualize_eeg_channels(self):
        selected_channels = [self.eeg_channels_selected_list.item(i).text() for i in range(self.eeg_channels_selected_list.count())]
        plot_data = self.EEG_DATA.RAW_DATA.copy()
        eeg_data_selected_channels = plot_data.pick_channels(selected_channels)
        eeg_data_selected_channels.plot(duration=60,show_options=True)
        
    def add_all_items(self):
            while self.eeg_channels_available_list.count() > 0:
                item = self.eeg_channels_available_list.takeItem(0)
                self.eeg_channels_selected_list.addItem(item.text())


    def remove_all_items(self):
        while self.eeg_channels_selected_list.count() > 0:
            item = self.eeg_channels_selected_list.takeItem(0)
            self.eeg_channels_available_list.addItem(item.text())

    def add_item(self):
        selected_items = self.eeg_channels_available_list.selectedItems()
        for item in selected_items:
            self.eeg_channels_selected_list.addItem(item.text())
            self.eeg_channels_available_list.takeItem(self.eeg_channels_available_list.row(item))

    def remove_item(self):
        selected_items = self.eeg_channels_selected_list.selectedItems()
        for item in selected_items:
            self.eeg_channels_available_list.addItem(item.text())
            self.eeg_channels_selected_list.takeItem(self.eeg_channels_selected_list.row(item))

    def browse_eeg_file(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Open EDF File", "", "EDF Files (*.edf)")
        if file_path:
            self.edf_file_path = file_path
            self.edf_file_name = get_file_name_from_path(file_path)
            self.eeg_file_name_textbox.setText(self.edf_file_name)
           
    def browse_xdf_file(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Open XDF File", "", "XDF Files (*.xdf)")
        if file_path:
            self.xdf_file_path = file_path
            self.xdf_file_name = get_file_name_from_path(file_path)
            self.audio_file_name_textbox.setText(self.xdf_file_name)
    
    def load_xdf_file(self):
        if self.xdf_file_path:
            self.waiting_msg_box = self.show_waiting_message("Loading XDF data. Please wait...")
            self.load_thread_eeg = LoadAudioThread(self.xdf_file_path)
            self.load_thread_eeg.finished.connect(self.on_load_finished_audio)
            self.load_thread_eeg.error.connect(self.on_load_error)
            self.load_thread_eeg.start()

    def load_edf_file(self):
        if self.edf_file_path:
            self.waiting_msg_box = self.show_waiting_message("Loading EEG data. Please wait...")
            self.load_thread_eeg = LoadEEGThread(self.edf_file_path)
            self.load_thread_eeg.finished.connect(self.on_load_finished_eeg)
            self.load_thread_eeg.error.connect(self.on_load_error)
            self.load_thread_eeg.start()
    
    def on_load_finished_eeg(self, eeg_data):
        self.EEG_DATA = eeg_data
        self.update_eeg_info()
        self.waiting_msg_box.accept()

    def update_eeg_info(self):
        self.eeg_sampling_freq_text.setText(str(self.EEG_DATA.SAMPLING_FREQUENCY))
        self.eeg_duration_text.setText(str(self.EEG_DATA.DURATION))
        self.eeg_n_triggers_text.setText(str(len(self.EEG_DATA.TRIGGERS)))
        self.eeg_n_bad_channels_text.setText(str(len(self.EEG_DATA.BAD_CHANNELS)))
        self.eeg_n_channels_text.setText(str(self.EEG_DATA.N_CHANNELS))
        self.eeg_interruptions_text.setText(str(self.EEG_DATA.INTERRUPTIONS_CHECK))
        self.eeg_channels_available_list.addItems(self.EEG_DATA.CHANNEL_NAMES)
        self.eeg_bad_channels_cbox.addItems(self.EEG_DATA.BAD_CHANNELS)
        self.eeg_start_time_text.setText(str(self.EEG_DATA.START_TIME))
        self.eeg_end_time_text.setText(str(self.EEG_DATA.END_TIME))


        events = convert_eeg_events_to_list(self.EEG_DATA.EVENTS)
        self.eeg_events_cbox.addItems(events)

    def update_audio_info(self):
        self.audio_sampling_freq_text.setText(str(self.AUDIO_DATA.SAMPLING_FREQUENCY))
        self.audio_duration_text.setText(str(self.AUDIO_DATA.AUDIO_DURATION))

        self.audio_n_markers_text.setText(str(len(self.AUDIO_DATA.MARKERS)))
        self.audio_markers_start_text.setText(str(self.AUDIO_DATA.MARKERS_START_TIME))
        self.audio_markers_end_text.setText(str(self.AUDIO_DATA.MARKERS_END_TIME))
        self.audio_markers_duration_text.setText(str(self.AUDIO_DATA.MARKERS_DURATION))

        self.audio_start_time_text.setText(str(self.AUDIO_DATA.AUDIO_START_TIME))
        self.audio_end_time_text.setText(str(self.AUDIO_DATA.AUDIO_END_TIME))
        self.audio_markers_duration_text.setText(str(self.AUDIO_DATA.AUDIO_DURATION))
        self.audio_duration_full_text.setText(str(self.AUDIO_DATA.AUDIO_DURATION))

    def on_load_finished_audio(self, audio_data):
        self.AUDIO_DATA = audio_data
        self.update_audio_info()
        self.waiting_msg_box.accept()

    def on_load_error(self, error_message):
        self.waiting_msg_box.accept()
        QMessageBox.critical(self, "Error", f"Failed to load EEG data: {error_message}")

    def show_waiting_message(self, message):
        waiting_msg_box = QMessageBox()
        waiting_msg_box.setText(message)
        waiting_msg_box.setStandardButtons(QMessageBox.NoButton)
        waiting_msg_box.setWindowFlags(Qt.Window | Qt.CustomizeWindowHint | Qt.WindowTitleHint)
        waiting_msg_box.setWindowTitle('Processing')
        waiting_msg_box.show()
        QApplication.processEvents()
        return waiting_msg_box
    
    def wrap_layout_in_widget(self, layout):
        widget = QWidget()
        widget.setLayout(layout)
        return widget