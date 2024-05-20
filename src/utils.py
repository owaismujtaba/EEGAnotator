import numpy as np
import pyxdf
import mne
import numpy as np

def find_start_block_saying_time_stamp(events):
    for i, item in enumerate(events):
        if item[0] == 'START_BLOCK_SAYING':
            return i, item[1], item[2]
    return None


def trigger_encodings(code):
    """
        Converts trigger codes into their corresponding marker names based on a predefined dictionary.
        Parameters:
            code (int): Trigger code to be converted.
        Returns:
            str: Corresponding marker name if code is found in the dictionary, otherwise 'UNKNOWN_CODE'.
    """

    # Dictionary mapping trigger codes to marker names
    marker_names = {
        255: 'START_READ_WORD',
        224: 'END_READ_WORD',
        192: 'START_SAY_WORD',
        160: 'END_SAY_WORD',
        128: 'START_BLOCK_SAYING',
        96: 'START_BLOCK_THINKING',
        64: 'EXPERIMENT_RESTART',
        32: 'EXPERIMENT_REST',
        16: 'EXPERIMENT_START',
        8: 'EXPERIMENT_END'
    }

    marker_name = marker_names.get(code)
    if marker_name:
        return marker_name
    else:
        return 'UNKNOWN_CODE'


def find_trigger_changes(trigger_array):
    """
        Finds the start and end indices of each trigger along with their respective codes in an array.        Parameters:
            trigger_array (numpy.ndarray): Array containing trigger codes.
        Returns:
            list: List of tuples, each containing the marker name, start index, and end index of a trigger range.
    """

    changes = np.where(np.diff(trigger_array) != 0)[0] + 1

    start_indices = [0] + changes.tolist()
    end_indices = changes.tolist() + [len(trigger_array)]

    trigger_ranges = [(trigger_encodings(trigger_array[start_indices[i]]), start_indices[i], end_indices[i]) for i in range(len(start_indices))]

    return trigger_ranges


def normalize_triggers(trigger_values):
    """
        Normalizes a trigger value using the formula:
        normalized_value = (trigger_value - trigger_min) / (trigger_max - trigger_min)
        Parameters:
            trigger_values (numpy.ndarray): Array containing trigger values to be normalized.
        Returns:
            numpy.ndarray: Array of normalized trigger values rounded to the nearest integer.
    """
    
    trigger_min = np.min(trigger_values)
    trigger_max = np.max(trigger_values)
    
    normalized_array = (trigger_values - trigger_min) / (trigger_max - trigger_min) * 255
    
    rounded_array = np.round(normalized_array).astype(int)
    
    return rounded_array

    





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
    #pdb.set_trace()
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
    print(filepath)
    streams = mne.io.read_raw_edf(filepath)
    print('*******************************Completed*******************************')

    return streams

