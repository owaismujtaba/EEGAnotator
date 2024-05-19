import numpy as np
import pyxdf
import mne
import numpy as np
import config
import pdb


def check_audio_markers(markers):
    """
        This function checks if the sequences of audio markers follow the correct order.
        Each marker is expected to be a tuple where the first element is a string in the format 'Action:Word'.
        The correct sequence for each word should be:
        StartReading -> EndReading -> StartSaying -> EndSaying
        
        Parameters:
            markers (list of Lists): A list of audio markers.

        Returns:
            tuple: A boolean indicating if all sequences are complete, and a list of lists with indices of incomplete sequences.
    """

    print('Checking Audio Markers')
    current_state = 'START'  
    incomplete_indices = [] 
    temp_wrong_indices = []  

    prev_word = None  
    word = None  

    for i, marker in enumerate(markers):
        event = marker[0].split(':')
        if len(event) != 2:
            continue  

        action, word = event
        prev_word = prev_word if prev_word is not None else word

        if word != prev_word and current_state != 'START':
            incomplete_indices.append(temp_wrong_indices.copy())
            temp_wrong_indices.clear()
            current_state = 'START'

        temp_wrong_indices.append(i)  

        # State transitions based on the action and current state
        if current_state == 'START' and action == 'StartReading':
            current_state = 'StartReading'
        elif current_state == 'StartReading' and action == 'EndReading':
            current_state = 'EndReading'
        elif current_state == 'EndReading' and action == 'StartSaying':
            current_state = 'StartSaying'
        elif current_state == 'StartSaying' and action == 'EndSaying':
            current_state = 'START'
            temp_wrong_indices.clear()  
        else:
            incomplete_indices.append(temp_wrong_indices.copy())
            temp_wrong_indices.clear()
            current_state = 'START'

        prev_word = word  

    result = len(incomplete_indices) == 0  

    return result, incomplete_indices


def calculate_time_gaps(time_array, time_interval):

    differences = np.diff(time_array).astype('int')
    indices = np.where(differences > time_interval)[0]

    time_gaps = differences[indices]
    corresponding_items = time_array[1:][indices]
    pdb.set_trace()
    return time_gaps, corresponding_items




def convert_unix_timestamps_to_datetime(timestamps):
    """
    Convert Unix timestamps to datetime objects using NumPy vectorized operations.
    
    Parameters:
        timestamps (array_like): Array of Unix timestamps.
    
    Returns:
        datetime_objects (array): Array of corresponding datetime objects.
    """
    # Convert Unix timestamps to datetime objects
    datetime_objects =  np.datetime64(0, 's') + timestamps.astype('timedelta64[s]')

    
    return datetime_objects

def load_xdf_file(filepath):
    """
        Load data from an XDF (Extensible Data Format) file.

        Parameters:
        - filepath (str): The filepath to the XDF file.

        Returns:
        - streams (list): A list containing streams of data loaded from the XDF file using pyxdf library.
        - header (dict): A dictionary containing header information of the XDF file.

        Dependencies:
        - pyxdf: Python library for reading XDF files.
    """
    print('*********************************************************************************')
    print('***************************Loading .xdf file***************************')
    
    # Use pyxdf library to load data from the XDF file
    streams, header = pyxdf.load_xdf(filepath)
    print('*******************************Completed*******************************')

    return streams, header


def load_edf_file(filepath):
    """
        Load data from an EDF (European Data Format) file.

        Parameters:
        - filepath (str): The filepath to the EDF file.

        Returns:
        - streams (object): Raw EEG data object loaded from the EDF file using mne library.

        Dependencies:
        - mne: Python library for EEG data analysis.
    """
    print('*********************************************************************************')
    print('***************************Loading .edf file***************************')
    
    # Use mne library to read the raw EEG data from the EDF file
    streams = mne.io.read_raw_edf(filepath)
    print('*******************************Completed*******************************')

    return streams

