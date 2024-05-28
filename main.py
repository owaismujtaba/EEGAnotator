from PyQt5.QtWidgets import QApplication
from src.gui.main_display import MainWindow
import sys

if __name__ == '__main__':
    App = QApplication(sys.argv)
    MainWindow = MainWindow()
    MainWindow.show()
    sys.exit(App.exec_())
