
import numpy as np
def find_closest_starting_point_in_eeg(eeg_events, timestamp):
    """
    Finds the closest starting point in EEG events to a given timestamp.

    This function takes a list of EEG events and a timestamp and finds the EEG event with the closest 
    starting time to the given timestamp. Each EEG event is represented as a tuple: (action, start_time, 
    end_time, start_index, end_index, duration).

    Args:
        eeg_events (list of tuples): A list of EEG events.
        timestamp (float): The timestamp to find the closest starting point to.

    Returns:
        close_index (int): The index of the EEG event with the closest starting time to the given timestamp.

    Example:
    >>> eeg_events = [('Action1', 0.0, 2.0, 0, 10, 2), ('Action2', 2.5, 4.5, 12, 22, 2)]
    >>> timestamp = 2.7
    >>> find_closest_starting_point_in_eeg(eeg_events, timestamp)
    1
    """

    timestamp = timestamp + 7200 # adjusting the difference in time
    eeg_timestamps = [item[1] for item in eeg_events]
    diff = abs(np.array(eeg_timestamps) - timestamp)
    close_index = np.argmin(diff)
    return close_index


class EEG_AUDIO_DATA:
    def __init__(self, eeg_data_obj, audio_data_object) -> None:
        self.eeg = eeg_data_obj
        self.audio = audio_data_object
        self.audio_marker_start_time = self.audio.MARKERS_TIME_STAMPS[0]
        
        self.NearestEEGStartPointToAudio = find_closest_starting_point_in_eeg(
            self.eeg.EVENTS, self.audio_marker_start_time
        )

        self.MappingEEGEventsWithMarkers = self.map_eeg_actions_to_marker_words(
            self.NearestEEGStartPointToAudio, self.eeg.EVENTS, self.audio.MARKERS_WORDS_TIMESTAMPS_AUDIO_STARTINDEX
        )



    def map_eeg_actions_to_marker_words(self, start_timestamp_eeg, eeg_events, markers_words_timestamps):
        """
            Maps EEG actions to corresponding marker words and timestamps.
            
            Key Point : Assuming we have all the markers in the xdf file. No missings.
            
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
                marker, word, time, audio_index = markers_words_timestamps[index]

                if action == marker:
                    result.append([marker, word, start_time, end_time, start_index, end_index,audio_index, duration, time])
                    word_index = index + 1
                    break
        

        
        return result
    

    