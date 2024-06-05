from PyQt5.QtWidgets import QApplication
from src.gui.main_display import MainWindow
import sys

def main():
    App = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(App.exec_())


if __name__ == '__main__':
    main()