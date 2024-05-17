import os
from pathlib import Path

CUR_DIR = os.getcwd()

#AUDIO_FILE_PATH = Path(CUR_DIR, r'Data\\Patients\\F10\\PictureNaming\\xdf\\sample.xdf')
#EEG_FILE_PATH  = Path(CUR_DIR, r'Data\\Patients\\F10\\PictureNaming\\eeg\\f10.edf')

EEG_FILE_PATH  = Path(CUR_DIR, 'Data/Patients/F09/JIMÉNEZÁLVAREZ_605b2177-7b18-4d5b-a6df-01fdc6572770.edf')
AUDIO_FILE_PATH = Path(CUR_DIR, 'Data/Patients/F09/sub-AntoniaJimenezAlvarez_ses-VCV_Ses01_task-Default_run-001_eeg.xdf')


INTERRUPTION_INTERVAL_EEG = 1.5
GAP_INTERVAL_AUDIO_MARKER = 3