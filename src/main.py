from PyQt5.QtWidgets import QApplication
from gui.main_display import MainWindow
from classes.eeg import EegData
import sys

if __name__ == '__main__':
    App = QApplication(sys.argv)
    MainWindow = MainWindow()
    MainWindow.show()
    sys.exit(App.exec_())
