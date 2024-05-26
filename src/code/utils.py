import numpy as np
import pyxdf
import mne
import pdb
import pandas as pd


#**************************************AUDIO RELATED FUNCTIONS**************************************

def bundle_audio_markers_with_timestamps(markers, marker_timestamps, audio_timestamps):
    """
    Bundles audio markers with corresponding timestamps.

    Parameters:
        - markers (list): List of marker data.
        - marker_timestamps (list): List of timestamps corresponding to the markers.
        - audio_timestamps (np.ndarray): Array of timestamps corresponding to the audio data.

    Returns:
        - marker_word_timestamp (list): List of lists containing marker action, marker word, timestamp, and audio start index.
    """
    print('***************************Started Bundling markers and audio timestamps***************************')

    marker_word_timestamp = []

    # Pre-calculate the closest audio start indices for each marker timestamp
    audio_indices = np.searchsorted(audio_timestamps, marker_timestamps)
    audio_indices = np.clip(audio_indices, 1, len(audio_timestamps) - 1)
    left_distances = abs(audio_timestamps[audio_indices - 1] - marker_timestamps)
    right_distances = abs(audio_timestamps[audio_indices] - marker_timestamps)
    closest_indices = np.where(left_distances <= right_distances, audio_indices - 1, audio_indices)

    for index in range(len(markers)):
        marker_values = markers[index][0].split(':')

        marker_action = marker_values[0]
        marker_word = marker_values[1] if len(marker_values) > 1 else '.'
        timestamp = marker_timestamps[index]
        audio_start_index = closest_indices[index]

        marker_word_timestamp.append([marker_action, marker_word, timestamp, audio_start_index])

    return marker_word_timestamp


    return marker_word_timestamp

def convert_audio_unix_timestamps_to_datetime(timestamps, start=None):
    """
    Convert Unix timestamps to datetime objects using NumPy vectorized operations.

    Parameters:
        timestamps (array_like): Array of Unix timestamps.
        start (str or datetime-like, optional): The start time to add to the converted datetime objects.
            If None, the default start time is '1970-01-01T00:00:00.000'.

    Returns:
        datetime_objects (np.ndarray): Array of corresponding datetime objects.
    """
    if start is None:
        start = '1970-01-01T00:00:00.000'
    else:
        start = np.datetime64(start) + np.timedelta64(2, 'h')  # Add two hours of delay

    datetime_objects = np.datetime64(start, 'ms') + + np.timedelta64(2, 'h')+ (timestamps * 1000).astype('timedelta64[ms]')

    return datetime_objects

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


#**************************************EEG RELATED FUNCTIONS**************************************

def eeg_transition_trigger_points(trigger_array):
    """
    Identifies the transition points in an EEG trigger array.

    This function takes a 1D numpy array of EEG trigger values and identifies the indexes where
    transitions occur. A transition is defined as a change from a lower value to a higher value 
    between consecutive elements in the trigger array. The function returns an array of indexes 
    indicating the positions of these transition points.

    Parameters:
    trigger_array (np.ndarray): A 1D numpy array containing the trigger values from EEG data.

    Returns:
    np.ndarray: An array of indexes where transitions occur in the trigger array. The first 
                element of the returned array is always 0 to indicate the start of the array.
                
    Example:
    >>> trigger_array = np.array([0, 0, 1, 1, 0, 0, 1, 1, 0])
    >>> eeg_transition_trigger_points(trigger_array)
    array([0, 2, 6])
    """
    
    difference_array = np.where(np.diff(trigger_array) > 0)[0] + 1
    transition_points_indexes = np.array([0] + difference_array.tolist())
  
    return transition_points_indexes

def trigger_encodings(code):
    """
    Converts trigger codes into their corresponding marker names based on a predefined dictionary.
    If the exact code is not found, the closest code is used.

    This function maps an integer trigger code to a human-readable marker name using a predefined 
    dictionary of codes and their corresponding marker names. If the exact code is not found in the 
    dictionary, the function finds and returns the marker name of the closest available code.

    Parameters:
    code (int): Trigger code to be converted.

    Returns:
    str: Corresponding marker name if the code is found in the dictionary. If the exact code is 
         not found, the marker name of the closest code is returned.

    Example:
    >>> trigger_encodings(200)
    'StartSaying'

    >>> trigger_encodings(10)
    'ExperimentEnded'
    """
    
    marker_names = {
        255: 'StartReading',
        224: 'EndReading',
        192: 'StartSaying',
        160: 'EndSaying',
        128: 'StartBlockSaying',
        96: 'StartBlockThinking',
        64: 'EXPERIMENT_RESTART',
        32: 'ExperimentResting',
        16: 'ExperimentStarted',
        8: 'ExperimentEnded'
    }

    marker_name = marker_names.get(code)
    
    if marker_name:
        return marker_name
    
    closest_code = min(marker_names.keys(), key=lambda k: abs(k - code))
    closest_marker_name = marker_names[closest_code]
    
    return closest_marker_name

def eeg_events_mapping(trigger_array, trigger_points, timestamps):
    """
    Maps EEG trigger values to their corresponding start and end points.

    This function takes an array of trigger values, an array of trigger points (indexes where trigger 
    values change), and an array of timestamps. It identifies events based on the trigger values and 
    maps them to their start and end points. Each event is represented by its corresponding marker 
    name, start timestamp, end timestamp, start index, end index, and duration.

    Parameters:
    trigger_array (np.ndarray): An array of trigger values recorded during the EEG session.
    trigger_points (np.ndarray): An array of indexes in the trigger values array where the trigger values change.
    timestamps (np.ndarray): An array of timestamps corresponding to the trigger values.

    Returns:
    List[List]: A list of lists, each representing an event with the following information:
        - Marker name (str)
        - Start timestamp (float)
        - End timestamp (float)
        - Start index (int)
        - End index (int)
        - Duration (int)
    
    Example:
    >>> trigger_array = np.array([0, 0, 1, 1, 0, 0, 2, 2, 0])
    >>> trigger_points = np.array([0, 2, 6])
    >>> timestamps = np.array([0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0])
    >>> eeg_events_mapping(trigger_array, trigger_points, timestamps)
    [['StartReading', 0.0, 1.0, 0, 2, 2],
     ['EndReading', 2.0, 3.0, 6, 8, 2]]
    """
    
    events_start_end = []

    for i in range(trigger_points.shape[0] - 1):
        
        start = trigger_points[i]
        end = trigger_points[i + 1]
        event = trigger_encodings(trigger_array[start])
        
        if end - start < 25:
            continue
        events_start_end.append([event, timestamps[start], timestamps[end], start, end, end - start])
        
    return events_start_end

def calculate_time_gaps(time_array, time_interval):
    """
    Identifies significant time gaps in an array of timestamps.

    This function takes an array of timestamps and a time interval. It calculates the differences 
    between consecutive timestamps and identifies those differences that are greater than the given 
    time interval. The function returns the time gaps and the corresponding timestamps where these 
    gaps occur.

    Parameters:
    time_array (np.ndarray): An array of timestamps.
    time_interval (int): The threshold time interval to identify significant gaps.

    Returns:
    Tuple[np.ndarray, np.ndarray]: 
        - An array of time gaps that are greater than the specified time interval.
        - An array of timestamps corresponding to the identified time gaps.

    Example:
    >>> time_array = np.array([0, 1, 2, 5, 6, 10])
    >>> time_interval = 2
    >>> calculate_time_gaps(time_array, time_interval)
    (array([3, 4]), array([5, 10]))
    """
    
    differences = np.diff(time_array).astype('int')
    indices = np.where(differences > time_interval)[0]

    time_gaps = differences[indices]
    corresponding_items = time_array[1:][indices]
    
    return time_gaps, corresponding_items

def correct_eeg_triggers(triggers):
    """
    Corrects a list of EEG triggers by mapping them to the nearest valid code
    from a predefined set of correct codes.

    This function takes a list of integer EEG trigger codes and corrects them by mapping 
    each trigger to the nearest valid code from a predefined set of valid codes. If a trigger 
    code is not in the predefined set, it is mapped to the closest valid code.

    Parameters:
    triggers (list of int): A list of integer trigger codes to be corrected.

    Returns:
    list of int: A list of corrected trigger codes. Each input trigger is either directly 
                 mapped if it exists in the valid codes, or mapped to the nearest valid code 
                 if it does not.

    Example:
    >>> triggers = [5, 20, 100, 130]
    >>> correct_eeg_triggers(triggers)
    [8, 16, 96, 128]
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
    Normalizes EEG trigger values to a range from 0 to 255.

    This function normalizes an array of EEG trigger values using the formula:
    normalized_value = (trigger_value - trigger_min) / (trigger_max - trigger_min) * 255.
    The trigger values are first inverted (multiplied by -1) before normalization. The resulting 
    normalized values are rounded to the nearest integer.

    Parameters:
    trigger_values (np.ndarray): Array containing trigger values to be normalized.

    Returns:
    np.ndarray: Array of normalized trigger values rounded to the nearest integer.

    Example:
    >>> trigger_values = np.array([10, 20, 30, 40, 50])
    >>> normalize_eeg_triggers(trigger_values)
    array([255, 204, 153, 102,  51])
    """
    
    trigger_values = trigger_values * -1
    trigger_min = np.min(trigger_values)
    trigger_max = np.max(trigger_values)
    
    normalized_triggers = (trigger_values - trigger_min) / (trigger_max - trigger_min) * 255
    normalized_triggers = np.round(normalized_triggers).astype(int)
    
    return normalized_triggers

def convert_eeg_unix_timestamps_to_datetime(timestamps, start):
    """
    Convert Unix timestamps to datetime objects using NumPy vectorized operations.

    This function takes an array of Unix timestamps and converts them into corresponding 
    datetime objects. The conversion is done using NumPy vectorized operations for efficiency. 
    A start time is provided as a reference point for the conversion.

    Parameters:
    timestamps (array_like): Array of Unix timestamps.
    start (str or datetime-like): The start time to add to the converted datetime objects.

    Returns:
    datetime_objects (np.ndarray): Array of corresponding datetime objects.

    Example:
    >>> timestamps = np.array([1621914057, 1621914058, 1621914059])
    >>> start_time = np.datetime64('2022-05-25T00:00:00')
    >>> convert_eeg_unix_timestamps_to_datetime(timestamps, start_time)
    array(['2022-05-25T00:00:57.000', '2022-05-25T00:00:58.000',
           '2022-05-25T00:00:59.000'], dtype='datetime64[ms]')
    """

    start = start.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]
    datetime_objects = np.datetime64(start, 'ms') + (timestamps * 1000).astype('timedelta64[ms]')

    return datetime_objects

def load_edf_file(filepath):
    """
    Load data from an EDF (European Data Format) file.

    This function loads raw EEG data from an EDF file using the MNE library, a Python library 
    for EEG data analysis.

    Parameters:
    - filepath (str): The filepath to the EDF file.

    Returns:
    - streams (object): Raw EEG data object loaded from the EDF file using the MNE library.

    Dependencies:
    - mne: Python library for EEG data analysis.

    Example:
    >>> filepath = "path/to/your/file.edf"
    >>> eeg_data = load_edf_file(filepath)
    """
    print('*********************************************************************************')
    print('***************************Loading .edf file***************************')
    
    # Use mne library to read the raw EEG data from the EDF file
    print(filepath)
    streams = mne.io.read_raw_edf(filepath)
    print('*******************************Completed*******************************')

    return streams
