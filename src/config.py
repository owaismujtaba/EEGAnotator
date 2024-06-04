import os
from pathlib import Path

curDir  = os.getcwd()
imageDir  = Path(curDir, 'src', 'gui')
imageDir  = Path(imageDir , 'Images')

gapIntervalAudioMarker  = 1.5
interruptionIntervalEEG  = 2.0

windowIconPath  = str(Path(imageDir , 'icon.bmp'))
backgroundImagePath  = str(Path(imageDir , 'background.jpg'))

outputDir = 'Extracted'
outputDir  = Path(curDir, outputDir )
outputDirMetadata  = Path(outputDir , 'MATADATA')
outputDirEEG  = Path(outputDir , 'EEG')
outputDirAudio  = Path(outputDir , 'AUDIO')