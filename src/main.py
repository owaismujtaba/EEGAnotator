from PyQt5.QtWidgets import QApplication
#from src.gui.main_display1 import MainWindow
from gui.main_display import MainWindow
from classes.eeg import EegData
import pdb
import sys

if __name__ == '__main__':

    edfFilePath = r'C:\DeepRESTORE\\Last\Data\\F10\\PictureNaming\\eeg\\f10.edf'

    #data = EegData(edfFilePath)
    #pdb.set_trace()
    App = QApplication(sys.argv)
    MainWindow = MainWindow()
    MainWindow.show()
    sys.exit(App.exec_())
