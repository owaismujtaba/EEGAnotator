import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QFileDialog
from PyQt5.QtWidgets import QComboBox
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


from utils import DATA
from src.eeg import EEG

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('DeepRESTORE')
        self.setGeometry(100, 100, 800, 600)  # Set window size and position

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()  # Main vertical layout
        central_widget.setLayout(main_layout)

        # Horizontal layout for upload options
        upload_layout = QHBoxLayout()
        main_layout.addLayout(upload_layout)

        
        self.create_edf_block()
        self.create_xdf_block()

        upload_layout.addWidget(self.edf_block)
        upload_layout.addWidget(self.xdf_block)

        # Horizontal layout for submit button
        submit_layout = QHBoxLayout()
        main_layout.addLayout(submit_layout)
        
        

    def create_edf_block(self):
        self.edf_block = QWidget()
        self.edf_layout = QVBoxLayout()
        self.edf_block.setLayout(self.edf_layout)
        
        top_layout = QHBoxLayout()
        self.label_eeg = QLabel('EEG')
        top_layout.addWidget(self.label_eeg)

        self.channels_combobox = QComboBox()
        self.channels_combobox.setEditable('True')

        self.edf_layout.addWidget(self.label_eeg)
            
        self.upload_button_edf = QPushButton('Upload EDF File')
        self.upload_button_edf.clicked.connect(self.upload_edf_file)
        self.edf_layout.addWidget(self.upload_button_edf)

        self.vis_edf_file_btn = QPushButton('Visualize EDF File')
        self.vis_edf_file_btn.hide()
        self.vis_edf_file_btn.clicked.connect(self.vis_edf_file)  # Connect submit button to submit method
        self.edf_layout.addWidget(self.vis_edf_file_btn)
       

    def vis_edf_file(self):
        if self.edf_file_path:
            self.eeg_data.raw_data.plot()
    def create_xdf_block(self):
        self.xdf_block = QWidget()
        self.xdf_layout = QVBoxLayout()
        self.xdf_block.setLayout(self.xdf_layout)
        
        self.label_audio = QLabel('AUDIO')
        self.xdf_layout.addWidget(self.label_audio)
        

        self.upload_button_xdf = QPushButton('Upload XDF File')
        self.upload_button_xdf.clicked.connect(self.upload_xdf_file)
        self.xdf_layout.addWidget(self.upload_button_xdf)
        


    
    def submit_xdf_edf(self):
        if self.edf_file_path and self.xdf_file_path:
            print('file paths added')
            print(self.edf_file_path, self.xdf_file_path)
            self.data = DATA(self.xdf_file_path, self.edf_file_path)
            self.data.print_info()
            


    def upload_xdf_file(self):
        options = QFileDialog.Options()
        self.xdf_file_path, _ = QFileDialog.getOpenFileName(
            None,
            "Upload File", 
            "", "All Files (*);;EDF Files (*.xdf)", 
            options=options
        )

    def upload_edf_file(self):
        options = QFileDialog.Options()
        self.edf_file_path, _ = QFileDialog.getOpenFileName(
            None,
            "Upload File", 
            "", "All Files (*);;EDF Files (*.edf)", 
            options=options
        )

        self.eeg_data = EEG(self.edf_file_path)
        self.channels_combobox.addItem(self.eeg_data.channel_names)
        self.vis_edf_file_btn.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
