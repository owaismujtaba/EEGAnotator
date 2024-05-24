
import numpy as np
import pdb
from src.utils import find_closest_starting_point_in_eeg


class DATA:
    def __init__(self, edf_data_obj, xdf_data_object ) -> None:
        """
            Initialize an instance of the DATA class.

            Parameters:
            - filepath_xdf (str): The filepath to the XDF (Extensible Data Format) file.
            - filepath_edf (str): 
            
            The filepath to the EDF (European Data Format) file.

            Attributes:
            - filepath_xdf (str): The filepath to the XDF file.
            - filepath_edf (str): The filepath to the EDF file.
            - eeg_streams (object): EEG data streams object initialized with the EDF file.
            - audio_streams (object): Audio data streams object initialized with the XDF file.

            Helper Classes:
            - EEG: Helper class for handling EEG data.
            - AUDIO: Helper class for handling audio data.
        """
        self.EEG_DATA = edf_data_obj
        self.AUDIO_DATA = xdf_data_object
        self.CLOSEST_POINT_BTW_EEG_EVENTS_AUDIO = find_closest_starting_point_in_eeg

        pdb.set_trace()

    
    def map_eeg_actions_to_marker_words(self, start_timestamp_eeg, eeg_events, markers_words_timestamps):
        """
            Maps EEG actions to corresponding marker words and timestamps.

            Args:
                - start_timestamp_eeg (int): The starting index for processing EEG events.
                - eeg_events (list of tuples): A list of EEG events where each event is represented as a tuple:
                    (action, start_time, end_time, start_index, end_index, duration).
                - markers_words_timestamps (list of tuples): A list of markers with corresponding words and timestamps,
                    where each item is represented as a tuple: (marker, word, time).

                Returns:
                - result (list of lists): A list of mapped actions to markers with their corresponding details,
                    where each item is represented as a list:
                    [marker, word, start_time, end_time, start_index, end_index, duration, time].

        """

        word_index = 0
        result = []

        for event in eeg_events[start_timestamp_eeg:]:
            action, start_time, end_time, start_index, end_index, duration = event

            for index in range(word_index, len(markers_words_timestamps)):
                marker, word, time = markers_words_timestamps[index]

                if action == marker:
                    result.append([marker, word, start_time, end_time, start_index, end_index, duration, time])
                    word_index = index + 1
                    break
        

        columns = ['marker', 'word', 'start_time_eeg', 'end_time_eeg', 'start_index_eeg', 'end_index_eeg', 'duration_eeg', 'time_xdf']
        data = pd.DataFrame(result, columns=columns)
        data.to_csv('mappings.csv')
        return result


