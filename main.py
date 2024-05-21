import config

xdf_path = config.AUDIO_FILE_PATH
edf_path = config.EEG_FILE_PATH

from src.eeg import EEG_DATA

data = EEG_DATA(filepath_edf=r'C:\DeepRESTORE\\EEGAnotator\Data\\F10\\PictureNaming\\eeg\\f10.edf')
#data = DATA(filepath_xdf=xdf_path, filepath_edf=edf_path)
#data.print_info()



