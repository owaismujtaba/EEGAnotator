import os
from pathlib import Path

CUR_DIR = os.getcwd()

AUDIO_FILE_PATH = Path(CUR_DIR, r'Data\\Patients\\F10\\PictureNaming\\xdf\\sample.xdf')
EEG_FILE_PATH  = Path(CUR_DIR, r'Data\\Patients\\F10\\PictureNaming\\eeg\\f10.edf')


INTERRUPTION_INTERVAL = 1.5