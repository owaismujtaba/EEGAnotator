import pdb

from src.eeg import EEG_DATA
from src.audio import AUDIO_DATA

edf_path = 'C:\DeepRESTORE\EEGAnotator\Data\F10\PictureNaming\eeg\\f10.edf'
xdf_path = 'C:\DeepRESTORE\EEGAnotator\Data\F10\PictureNaming\\xdf\\f10.xdf'
eeg = EEG_DATA(filepath_edf=edf_path)
#audio = AUDIO_DATA(xdf_path)



