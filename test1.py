import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QFileDialog
from src.GUI.utils import upload_file, load_edf
import config
import mne

def create_edf_block():
    edf_block = QWidget()
    edf_layout = QVBoxLayout()
    edf_block.setLayout(edf_layout)
    
    label = QLabel('EEG')
    edf_layout.addWidget(label)
    
    upload_button = QPushButton('Upload EDF File')
    upload_button.clicked.connect(lambda: upload_and_load_edf(edf_layout))
    edf_layout.addWidget(upload_button)
    
    return edf_block

def create_xdf_block():
    xdf_block = QWidget()
    xdf_layout = QVBoxLayout()
    xdf_block.setLayout(xdf_layout)
    
    label = QLabel('AUDIO')
    xdf_layout.addWidget(label)
    
    upload_button = QPushButton('Upload XDF File')
    upload_button.clicked.connect(upload_file)  # Assuming upload_file handles XDF files too
    xdf_layout.addWidget(upload_button)
    
    submit_button = QPushButton('Submit')
    # Here you can add functionality for the Submit button if needed
    xdf_layout.addWidget(submit_button)
    
    return xdf_block

def upload_and_load_edf(layout):
    file_path, _ = QFileDialog.getOpenFileName(None, "Select EDF file", "", "EDF files (*.edf)")
    if file_path:
        raw_eeg = load_edf(file_path)
        fig = raw_eeg.plot(block=False)
        layout.addWidget(fig)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle('DeepRESTORE')
        self.setGeometry(100, 100, 800, 600)  # Set window size and position
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QHBoxLayout()
        central_widget.setLayout(layout)
        
        edf_block = create_edf_block()
        xdf_block = create_xdf_block()
        
        layout.addWidget(edf_block)
        layout.addWidget(xdf_block)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
