import os
from pathlib import Path

CurDir  = os.getcwd()
ImageDir  = Path(CurDir, 'src', 'gui')
ImageDir  = Path(ImageDir , 'Images')

GapIntervalAudioMarker  = 1.5
InterruptionIntervalEEG  = 2.0

WindowIconPath  = str(Path(ImageDir , 'icon.bmp'))
BackgroundImagePath  = str(Path(ImageDir , 'background.jpg'))

OutputDir = 'Extracted'
OutputDir  = Path(CurDir, OutputDir )
OutputDirMetadata  = Path(OutputDir , 'MATADATA')
OutputDirEEG  = Path(OutputDir , 'EEG')
OutputDirAudio  = Path(OutputDir , 'AUDIO')