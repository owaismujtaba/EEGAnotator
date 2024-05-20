
from PyQt5.QtCore import Qt, QThread, pyqtSignal
def get_file_name_from_path(file_path):
    filename = file_path.split('/')[-1]
    return filename
      


