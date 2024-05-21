import numpy as np
import pyxdf
import mne
import pdb




def trigger_encodings(code):
    """
        Converts trigger codes into their corresponding marker names based on a predefined dictionary.
        If the exact code is not found, the closest code is used.
        
        Parameters:
            code (int): Trigger code to be converted.
        
        Returns:
            str: Corresponding marker name if code is found in the dictionary, otherwise the closest code's marker name.
    """

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
    
    closest_code = min(marker_names.keys(), key=lambda k: abs(k - code))
    closest_marker_name = marker_names[closest_code]
    
    return closest_marker_name

def eeg_events_mapping(trigger_values, trigger_points):
    """
        Maps EEG trigger values to their corresponding start and end points.

        Parameters:
        - trigger_values (numpy.ndarray): An array of trigger values recorded during the EEG session.
        - trigger_points (numpy.ndarray): An array of indexes of trigger values array where the trigger values change .

        Returns:
        - List[str]: A list of strings, each representing an event with its start and end points.
    """
    events_start_end = []

    for i in range(trigger_points.shape[0] - 1):
        event = trigger_encodings(trigger_values[i])
        start = trigger_points[i]
        end = trigger_points[i + 1]
        event_string = f"{event} {start} {end}"
        if end-start < 25:
            continue
        events_start_end.append(event_string)
        

    return events_start_end 


def eeg_transition_trigger_points(trigger_array):
    transition_points_indexes = np.where(np.diff(trigger_array) != 0)[0] + 1
    transition_points_indexes = np.array([0] + transition_points_indexes.tolist())
  
    return transition_points_indexes
 
def correct_eeg_triggers(triggers):
    """
        Corrects a list of EEG triggers by mapping them to the nearest valid code
        from a predefined set of correct codes.

        Parameters:
        triggers (list of int): A list of integer trigger codes to be corrected.

        Returns:
        list of int: A list of corrected trigger codes, where each input trigger
                    is either directly mapped if it exists in the correct codings,
                    or mapped to the nearest valid code if it does not.
    """

    correct_codings = {
        255: 255, 224: 224, 192: 192, 160: 160,
        128: 128, 96: 96, 64: 64, 32: 32, 16: 16, 8: 8
    }

    valid_codes = sorted(correct_codings.keys())

    max_trigger = max(valid_codes)
    nearest_code_map = {}

    for i in range(max_trigger + 1):
        nearest_code = min(valid_codes, key=lambda x: abs(x - i))
        nearest_code_map[i] = correct_codings[nearest_code]

    corrected_triggers = []
    for trigger in triggers:
        if trigger in nearest_code_map:
            corrected_triggers.append(nearest_code_map[trigger])
        else:
            corrected_triggers.append(nearest_code_map[max_trigger])
    
    return corrected_triggers

def normalize_eeg_triggers(trigger_values):
    """
        Normalizes a trigger value using the formula:
        normalized_value = (trigger_value - trigger_min) / (trigger_max - trigger_min)
        Parameters:
            trigger_values (numpy.ndarray): Array containing trigger values to be normalized.
        Returns:
            numpy.ndarray: Array of normalized trigger values rounded to the nearest integer.
    """
    trigger_values = trigger_values*-1
    trigger_min = np.min(trigger_values)
    trigger_max = np.max(trigger_values)
    
    normalized_triggers = (trigger_values - trigger_min) / (trigger_max - trigger_min) * 255
    normalized_triggers = np.round(normalized_triggers).astype(int)
    
    return normalized_triggers

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

