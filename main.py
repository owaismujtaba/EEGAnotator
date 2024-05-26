import pdb

from src.eeg import EEG_DATA
from src.audio import AUDIO_DATA

from utils import DATA

edf_path = '/home/owais/GitHub/21-05-2024/EEGAnotator/F10/PictureNaming/eeg/sample.edf'
xdf_path = '/home/owais/GitHub/21-05-2024/EEGAnotator/F10/PictureNaming/xdf/sample.xdf'

eeg = EEG_DATA(filepath_edf=edf_path)
audio = AUDIO_DATA(filepath_xdf=xdf_path)


data = DATA(eeg, audio)

