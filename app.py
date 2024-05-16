import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QFileDialog, QProgressDialog, QComboBox, QHBoxLayout, QLabel
from PyQt5.QtCore import Qt
import pyqtgraph as pg

from utils import load_xdf_edf_data

class EEGPlotter(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EEG Plotter")
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()
        
        # Create a horizontal layout for the file uploader buttons and dropdown menu
        self.row_layout = QHBoxLayout()

        # Upload EDF file button
        self.upload_edf_button = QPushButton("Upload EDF File")
        self.upload_edf_button.clicked.connect(self.upload_edf_file)
        self.row_layout.addWidget(self.upload_edf_button)

        # Upload XDF file button
        self.upload_xdf_button = QPushButton("Upload XDF File")
        self.upload_xdf_button.clicked.connect(self.upload_xdf_file)
        self.row_layout.addWidget(self.upload_xdf_button)

        # Submit button
        self.submit_button = QPushButton("Submit")
        self.submit_button.clicked.connect(self.submit_files)
        self.row_layout.addWidget(self.submit_button)

        label_channels = QLabel("Channels:")
        label_channels.setAlignment(Qt.AlignRight)  # Align the text to the left
        self.row_layout.addWidget(label_channels)

        self.channel_dropdown = QComboBox()  # Dropdown box for channel names
        self.channel_dropdown.currentIndexChanged.connect(self.update_plot)  # Call update_plot on index change
        self.row_layout.addWidget(self.channel_dropdown)

        self.layout.addLayout(self.row_layout)

        # Create a horizontal layout for the file uploader buttons and dropdown menu
     

        self.channel_dropdown = QComboBox()  # Dropdown box for channel names
        self.channel_dropdown.currentIndexChanged.connect(self.update_plot)  # Call update_plot on index change
        self.row_layout.addWidget(self.channel_dropdown)

        self.layout.addLayout(self.row_layout)

        self.plot_widget = pg.PlotWidget()
        self.layout.addWidget(self.plot_widget)

    

        self.central_widget.setLayout(self.layout)
        self.progress_dialog = None
        self.edf_file = None
        self.xdf_file = None

        # Apply stylesheets
        self.apply_styles()

    def apply_styles(self):
        # Apply stylesheets to the dropdown menu and its items
        self.channel_dropdown.setStyleSheet("QComboBox { background-color: green; color: red; min-width: 100px; font-size: 10px; padding: 2px; }"
                                             "QComboBox::drop-down { subcontrol-origin: padding; subcontrol-position: top right; }"
                                             "QComboBox::down-arrow { image: url(arrow_down.png); }"
                                             "QComboBox::down-arrow:on { top: 1px; }"
                                             "QComboBox QAbstractItemView { background-color: green; color: red; selection-background-color: green; }")

    def upload_edf_file(self):
        file_dialog = QFileDialog()
        filename, _ = file_dialog.getOpenFileName(self, "Open EDF File", "", "EDF Files (*.edf)")
        if filename:
            self.edf_file = filename
            self.upload_edf_button.setText(self.get_filename(filename))
            

    def upload_xdf_file(self):
        file_dialog = QFileDialog()
        filename, _ = file_dialog.getOpenFileName(self, "Open XDF File", "", "XDF Files (*.xdf)")
        if filename:
            self.xdf_file = filename
            self.upload_xdf_button.setText(self.get_filename(filename))
            

    

    def submit_files(self):
        # Do something with the selected files
        print("EDF File:", self.xdf_file)
        print("XDF File:", self.edf_file)
        self.progress_dialog = QProgressDialog("Loading EEG and Audio Data...", "Cancel", 0, 0, self)
        self.progress_dialog.setWindowModality(Qt.WindowModal)
        self.progress_dialog.show()
        data = load_xdf_edf_data(self.xdf_file, self.edf_file)
        data.print_info()
        channels = data.eeg_streams.channel_names
        self.populate_channel_dropdown(channels)

    
        self.progress_dialog.close()

    def get_filename(self, filepath):
        return filepath.split("/")[-1]  # Extract filename from filepath

    def populate_channel_dropdown(self, channels):
        if self.file_data:
            self.channel_dropdown.clear()  # Clear existing items
            self.channel_dropdown.addItems(channels)  # Add channel names

    def update_plot(self):
        # Placeholder for updating the plot based on selected channel
        pass

def main():
    app = QApplication(sys.argv)
    window = EEGPlotter()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
