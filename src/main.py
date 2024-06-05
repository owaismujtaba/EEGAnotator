from PyQt5.QtWidgets import QApplication
import sys

def main():
    App = QApplication(sys.argv)
    MainWindow = MainWindow()
    MainWindow.show()
    sys.exit(App.exec_())


if __name__ == '__main__':
    main()