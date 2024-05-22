import pdb
from src.utils import convert_unix_timestamps_to_datetime
from src.utils import load_xdf_file, calculate_time_gaps
import config

class AUDIO_DATA:
    def __init__(self, filepath_xdf) -> None:
        """
            Initialize an instance of the AUDIO class.

            Parameters:
            - filepath_xdf (str): The filepath to the XDF (Extensible Data Format) file.

            Attributes:
            - FILEPATH (str): The filepath to the XDF file.
            - STREAMS (list): A list containing streams of data loaded from the XDF file.
            - CREATE_TIME (datetime): The creation time of the XDF file.
            - SAMPLING_FREQUENCY (float): The sampling frequency of the audio data.
            - MARKER_TIMES (list): List of datetime objects representing marker times.
            - MARKERS (list): List of marker data.
            - START_TIME_MARKER (datetime): The start time of the first marker.
            - END_TIME_MARKER (datetime): The end time of the last marker.
            - N_MARKERS (int): The total number of markers.
            - MARKER_DURATION (timedelta): Duration between the first and last marker.
            - AUDIO (list): List containing audio data.
            - AUDIO_TIMES (list): List of datetime objects representing audio sample times.
            - AUDIO_START_TIME (datetime): The start time of the audio data.
            - AUDIO_END_TIME (datetime): The end time of the audio data.
            - AUDIO_DURATION (timedelta): Duration of the audio data.
        """

        self.FILEPATH = filepath_xdf
        self.STREAMS = None
        self.SAMPLING_FREQUENCY = None
        self.MARKER_TIMES = None
        self.N_MARKERS = None
        self.MARKERS = None
        self.START_TIME_MARKER = None
        self.END_TIME_MARKER = None
        self.MARKER_TIMES_ORIGINAL = None
        self.MARKER_TIMES_ORIGINAL = None
        self.AUDIO = None
        self.MARKER_DURATION = None
        self.AUDIO_START_TIME = None
        self.AUDIO_END_TIME = None
        self.MARKER_TIMES_ORIGINAL = None
        self.MARKER_TIMES_REAL = None
        self.MARKER_TIME_GAPS = None
        
        
        

        
        
        
        self.MARKER_TIME_GAPS, self.MARKER_TIME_GAPS_ITEMS = calculate_time_gaps(
            self.MARKER_TIMES, 
            config.GAP_INTERVAL_AUDIO_MARKER
        )
        
        self.N_GAPS = len(self.MARKER_TIME_GAPS)

        self.load_audio_data()
        self.preprocess_audio_data()

    def load_audio_data(self):
        print('***************************Loading Audio data***************************')

        self.STREAMS, header = load_xdf_file(self.FILEPATH)
        self.SAMPLING_FREQUENCY = self.STREAMS[1]['info']['effective_srate']
        self.MARKERS = self.STREAMS[0]['time_series']
        self.START_TIME_MARKER = self.MARKER_TIMES[0]
        self.END_TIME_MARKER = self.MARKER_TIMES[-1]
        self.MARKER_TIMES_ORIGINAL = self.STREAMS[0]['time_stamps']
        
        self.AUDIO = self.STREAMS[1]['time_series']
        self.MARKER_DURATION = self.END_TIME_MARKER - self.START_TIME_MARKER
        self.AUDIO_START_TIME = self.AUDIO_TIMES[0]
        self.AUDIO_END_TIME = self.AUDIO_TIMES[-1]
        self.AUDIO_DURATION = self.AUDIO_END_TIME - self.AUDIO_START_TIME
        self.AUDIO_TIMES_ORIGINAL = self.STREAMS[1]['time_stamps']
        
    def preprocess_audio_data(self):
        self.MARKER_TIMES_REAL = convert_unix_timestamps_to_datetime(
                                            self.STREAMS[0]['time_stamps']
                                        )

        self.AUDIO_TIMES_REAL = convert_unix_timestamps_to_datetime(
                                                self.AUDIO_TIMES_ORIGINAL
                                        )
        
        self.MARKER_TIME_GAPS, self.MARKER_TIME_GAPS_ITEMS = calculate_time_gaps(
                                            self.MARKER_TIMES, 
                                            config.GAP_INTERVAL_AUDIO_MARKER
                                        )

    def print_info(self):
        print('***************************Audio File Info***************************')

        print("Filepath:", self.FILEPATH)
        print("Marker :::: Start Time: {}, End Time:{}".format(
            self.START_TIME_MARKER, 
            self.END_TIME_MARKER)
        )
        print("No. Markers :", self.N_MARKERS)
        print("Marker Duration:", self.MARKER_DURATION)

        print("Sampling Frequency:", self.SAMPLING_FREQUENCY)
        print("Audio :::: Start Time: {}, End Time:{}".format(
            self.AUDIO_START_TIME, 
            self.AUDIO_END_TIME)
        )
        print("Audio Duration:", self.AUDIO_DURATION)
        print('***************************************************************')
