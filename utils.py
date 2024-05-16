from src.audio import AUDIO
from src.eeg import EEG
import numpy as np

def convert_unix_timestamps_to_datetime(timestamps):
    """
    Convert Unix timestamps to datetime objects using NumPy vectorized operations.
    
    Parameters:
        timestamps (array_like): Array of Unix timestamps.
    
    Returns:
        datetime_objects (array): Array of corresponding datetime objects.
    """
    # Convert Unix timestamps to datetime objects
    datetime_objects = np.datetime64('1970-01-01T00:00:00Z') + np.array(timestamps, dtype='timedelta64[s]')
    
    return datetime_objects

class DATA:
    def __init__(self, filepath_xdf, filepath_edf) -> None:
        self.filepath_xdf = filepath_xdf
        self.filepath_edf = filepath_edf
        #self.eeg_streams = EEG(self.filepath_edf)
        #self.eeg_streams.print_info()
        self.audio_streams = AUDIO(self.filepath_xdf) 
