from PyQt5.QtWidgets import QApplication
from gui.main_display import MainWindow
import sys

def main():
    App = QApplication(sys.argv)
    MainWindow = MainWindow()
    MainWindow.show()
    sys.exit(App.exec_())

if __name__ == '__main__':
    App = QApplication(sys.argv)
    MainWindow = MainWindow()
    MainWindow.show()
    sys.exit(App.exec_())
