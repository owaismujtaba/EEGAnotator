import pdb
from src.utils import convert_audio_unix_timestamps_to_datetime
from src.utils import load_xdf_file, calculate_time_gaps
from src.utils import bundle_audio_markers_with_timestamps
from src.utils import find_closest_starting_point_in_eeg
from src.utils import map_eeg_actions_to_marker_words
import config

class AUDIO_DATA:
    def __init__(self, filepath_xdf) -> None:
        """
        Initialize an instance of the AUDIO_DATA class.

            Parameters:
                - filepath_xdf (str): The filepath to the XDF (Extensible Data Format) file.

            Attributes:
                - FILEPATH (str): The filepath to the XDF file.
                - STREAMS (list): A list containing streams of data loaded from the XDF file.
                - SAMPLING_FREQUENCY (float): The sampling frequency of the audio data.
                - MARKERS (list): List of marker data.
                - MARKERS_TIME_STAMPS (list): List of Unix timestamps for marker data.
                - MARKERS_START_TIME (datetime): The start time of the first marker.
                - MARKERS_END_TIME (datetime): The end time of the last marker.
                - MARKERS_DURATION (timedelta): Duration between the first and last marker.
                - AUDIO (list): List containing audio data.
                - AUDIO_TIME_STAMPS (list): List of Unix timestamps for audio sample times.
                - AUDIO_START_TIME (datetime): The start time of the audio data.
                - AUDIO_END_TIME (datetime): The end time of the audio data.
                - AUDIO_DURATION (timedelta): Duration of the audio data.
                - MARKER_TIME_GAPS (list): List of time gaps between marker data.
                - N_GAPS_MARKERS (int): The total number of time gaps between marker data.
        """

        self.FILEPATH = filepath_xdf
        self.STREAMS = None
        self.SAMPLING_FREQUENCY = None

        self.MARKERS = None
        self.MARKERS_TIME_STAMPS = None
        self.MARKERS_START_TIME = None
        self.MARKERS_END_TIME = None
        self.MARKERS_DURATION = None

        self.AUDIO = None
        self.AUDIO_TIME_STAMPS = None
        self.AUDIO_START_TIME = None
        self.AUDIO_END_TIME = None
        self.AUDIO_DURATION = None

        self.MARKER_TIME_GAPS = None
        self.N_GAPS_MARKERS = None

        self.load_audio_data()
        self.preprocess_audio_data()

    def load_audio_data(self):
        """
        Load audio data from XDF file and initialize relevant attributes.
        """
        print('***************************Loading Audio data***************************')

        self.STREAMS, header = load_xdf_file(self.FILEPATH)
        self.SAMPLING_FREQUENCY = self.STREAMS[1]['info']['effective_srate']
        self.MARKERS = self.STREAMS[0]['time_series']
        self.MARKERS_TIME_STAMPS = self.STREAMS[0]['time_stamps']
        self.MARKERS_START_TIME = self.MARKERS_TIME_STAMPS[0]
        self.MARKERS_END_TIME = self.MARKERS_TIME_STAMPS[-1]
        self.MARKERS_DURATION = self.MARKERS_END_TIME - self.MARKERS_START_TIME

        self.AUDIO = self.STREAMS[1]['time_series']
        self.AUDIO_TIME_STAMPS = self.STREAMS[1]['time_stamps']
        self.AUDIO_START_TIME = self.AUDIO_TIME_STAMPS[0]
        self.AUDIO_END_TIME = self.AUDIO_TIME_STAMPS[-1]
        self.AUDIO_DURATION = self.AUDIO_END_TIME - self.AUDIO_START_TIME

        self.N_MARKERS = len(self.MARKERS)

    def preprocess_audio_data(self):
        """
        Preprocess audio data by converting timestamps and calculating time gaps between markers.
        """
        self.MARKERS_TIME_STAMPS = convert_audio_unix_timestamps_to_datetime(self.MARKERS_TIME_STAMPS)
        self.MARKERS_START_TIME = self.MARKERS_TIME_STAMPS[0]
        self.MARKERS_END_TIME = self.MARKERS_TIME_STAMPS[-1]
        self.AUDIO_TIME_STAMPS = convert_audio_unix_timestamps_to_datetime(self.AUDIO_TIME_STAMPS)
        self.AUDIO_START_TIME = self.AUDIO_TIME_STAMPS[0]
        self.AUDIO_END_TIME = self.AUDIO_TIME_STAMPS[-1]
        self.MARKERS_WORDS_TIME_STAMPS = bundle_audio_markers_with_timestamps(self.MARKERS, self.MARKERS_TIME_STAMPS)
        self.MARKER_TIME_GAPS, self.MARKER_TIME_GAPS_ITEMS = calculate_time_gaps(
            self.MARKERS_TIME_STAMPS,
            config.GAP_INTERVAL_AUDIO_MARKER
        )

        self.N_GAPS_MARKERS = len(self.MARKER_TIME_GAPS)




    def print_info(self):
        """
        Print detailed information about the audio file and its attributes.
        """
        print('***************************Audio File Info***************************')

        print("Filepath:", self.FILEPATH)
        print("Sampling Frequency:", self.SAMPLING_FREQUENCY)

        print("Marker Start Time:", self.MARKERS_START_TIME)
        print("Marker End Time:", self.MARKERS_END_TIME)
        print("No. of Markers:", self.N_MARKERS)
        print("Marker Duration:", self.MARKERS_DURATION)

        print("Audio Start Time:", self.AUDIO_START_TIME)
        print("Audio End Time:", self.AUDIO_END_TIME)
        print("Audio Duration:", self.AUDIO_DURATION)

        print("Marker Time Gaps:", self.MARKER_TIME_GAPS)
        print("No. of Marker Time Gaps:", self.N_GAPS_MARKERS)

        print('***************************************************************')


