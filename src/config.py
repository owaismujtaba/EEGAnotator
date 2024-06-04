import os
from pathlib import Path

curDir  = os.getcwd()
imageDir  = Path(curDir, 'src', 'gui')
imageDir  = Path(imageDir , 'Images')

gapIntervalAudioMarker  = 1.5
interruptionIntervalEEG  = 2.0

windowIconPath  = str(Path(imageDir , 'icon.bmp'))
backgroundImagePath  = str(Path(imageDir , 'background.jpg'))

audioPlayDir = str(Path(curDir, 'AudioFilesForPlaying'))
bidsDir = str(Path(curDir, 'BIDS'))