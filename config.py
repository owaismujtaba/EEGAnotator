import os
from pathlib import Path

CUR_DIR = os.getcwd()
IMAGE_DIR = Path(CUR_DIR, 'src', 'gui')
IMAGE_DIR = Path(IMAGE_DIR, 'Images')

GAP_INTERVAL_AUDIO_MARKER = 1.5
INTERRUPTION_INTERVAL_EEG = 2.0

WINDOW_ICON_PATH = str(Path(IMAGE_DIR, 'icon.bmp'))
BACKGROUND_IMAGE_PATH = str(Path(IMAGE_DIR, 'background.jpg'))

print(BACKGROUND_IMAGE_PATH)