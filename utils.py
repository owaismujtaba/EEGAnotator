from src.audio import AUDIO
from src.eeg import EEG
import numpy as np
import pdb

def load_xdf_edf_data(xdf_file, edf_file):
    data = DATA(xdf_file, edf_file)
    return data

class DATA:
    def __init__(self, filepath_xdf, filepath_edf) -> None:
        """
            Initialize an instance of the DATA class.

            Parameters:
            - filepath_xdf (str): The filepath to the XDF (Extensible Data Format) file.
            - filepath_edf (str): The filepath to the EDF (European Data Format) file.

            Attributes:
            - filepath_xdf (str): The filepath to the XDF file.
            - filepath_edf (str): The filepath to the EDF file.
            - eeg_streams (object): EEG data streams object initialized with the EDF file.
            - audio_streams (object): Audio data streams object initialized with the XDF file.

            Helper Classes:
            - EEG: Helper class for handling EEG data.
            - AUDIO: Helper class for handling audio data.
        """
        self.filepath_xdf = filepath_xdf
        self.filepath_edf = filepath_edf

        # Initialize EEG data streams and print info
        self.eeg_streams = EEG(self.filepath_edf)

        # Initialize audio data streams and print info
        self.audio_streams = AUDIO(self.filepath_xdf)

        #self.remove_gaps_by_markers_in_audio()
        
    def print_info(self):
        self.eeg_streams.print_info()
        self.audio_streams.print_info()

    def remove_gaps_by_markers_in_audio(self):
        pass