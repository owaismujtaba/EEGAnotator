import numpy as np
import pyxdf
import mne
import datetime
import pdb

def find_closet_starting_point_in_eeg(eeg_events, timestamp):
    eeg_timestamps = [item[1] for item in eeg_events]
    diff = abs(eeg_timestamps-timestamp)
    close_index = np.argmin(diff) 
    return close_index

def map_eeg_actions_to_marker_words(start_timestamp_eeg, eeg_events, markers_words_timestamps):
    word_index = 0
    result = []
    for event in eeg_events[start_timestamp_eeg:]:
        action , start_time, end_time, start_index, end_index ,duration = event

        for index in range(word_index, len(markers_words_timestamps)):
            marker, word, time = markers_words_timestamps[index]
            

            if action == marker:
                result.append([marker, word, start_time, end_time,
                               start_index, end_index, duration, time])
                word_index = index
                break

    return result






#**************************************AUDIO RELATED FUNCTIONS**************************************
def bundle_audio_markers_with_timestamps(markers, timestamps):
    """
        Bundles audio markers with corresponding timestamps.

        Parameters:
            - markers (list): List of marker data.
            - timestamps (list): List of timestamps corresponding to the markers.

        Returns:
            - marker_word_timestamp (list): List of lists containing marker action, marker word, and timestamp.

        
    """
    marker_word_timestamp = []
    for index in range(len(markers)):
        marker_values = markers[index][0].split(':')

        if len(marker_values) > 1:
            marker_action = marker_values[0]
            marker_word = marker_values[1]     
        else:
            marker_action = marker_values[0]
            marker_word = ''
        timestamp = timestamps[index]
        marker_word_timestamp.append([marker_action, marker_word, timestamp])

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

    difference_array = np.where(np.diff(trigger_array) > 0)[0] + 1
    
    transition_points_indexes = np.array([0] + difference_array.tolist())

    #pdb.set_trace()
  
    return transition_points_indexes
 

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

        Parameters:
        - trigger_values (numpy.ndarray): An array of trigger values recorded during the EEG session.
        - trigger_points (numpy.ndarray): An array of indexes of trigger values array where the trigger values change.

        Returns:
        - List[str]: A list of strings, each representing an event with its start and end points and duration.
    """
    events_start_end = []

    for i in range(trigger_points.shape[0] - 1):
        
        start = trigger_points[i]
        end = trigger_points[i + 1]
        event = trigger_encodings(trigger_array[start])
        
        #event_string = f"{event} {start} {end}"
        if end-start < 25:
            continue
        events_start_end.append([event, timestamps[start], timestamps[end], start, end, end-start])
        

    return events_start_end 


def calculate_time_gaps(time_array, time_interval):
    
    differences = np.diff(time_array).astype('int')
    indices = np.where(differences > time_interval)[0]

    time_gaps = differences[indices]
    corresponding_items = time_array[1:][indices]
    
    return time_gaps, corresponding_items

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


def convert_eeg_unix_timestamps_to_datetime(timestamps, start):
    """
    Convert Unix timestamps to datetime objects using NumPy vectorized operations.

    Parameters:
        timestamps (array_like): Array of Unix timestamps.
        start (str or datetime-like): The start time to add to the converted datetime objects.

    Returns:
        datetime_objects (np.ndarray): Array of corresponding datetime objects.
    """
    start = start.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]

    datetime_objects = np.datetime64(start, 'ms') + (timestamps * 1000).astype('timedelta64[ms]')

    return datetime_objects

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

