import pyxdf
import pdb
from src.utils import convert_unix_timestamps_to_datetime
from src.utils import load_xdf_file

class AUDIO:
    def __init__(self, filepath_xdf) -> None:
        """
            Initialize an instance of the AUDIO class.

            Parameters:
            - filepath_xdf (str): The filepath to the XDF (Extensible Data Format) file.

            Attributes:
            - filepath (str): The filepath to the XDF file.
            - streams (list): A list containing streams of data loaded from the XDF file.
            - create_time (datetime): The creation time of the XDF file.
            - sampling_frequency (float): The sampling frequency of the audio data.
            - marker_times (list): List of datetime objects representing marker times.
            - markers (list): List of marker data.
            - start_time_marker (datetime): The start time of the first marker.
            - end_time_marker (datetime): The end time of the last marker.
            - n_markers (int): The total number of markers.
            - marker_duration (timedelta): Duration between the first and last marker.
            - audio (list): List containing audio data.
            - audio_times (list): List of datetime objects representing audio sample times.
            - audio_start_time (datetime): The start time of the audio data.
            - audio_end_time (datetime): The end time of the audio data.
            - audio_duration (timedelta): Duration of the audio data.
        """

        self.filepath = filepath_xdf
        self.streams, header = load_xdf_file(filepath_xdf)
        self.create_time = header['info']['datetime'][0]
        
        # Extract information from the marker stream
        self.sampling_frequency = self.streams[1]['info']['effective_srate']
        self.marker_times = convert_unix_timestamps_to_datetime(
            self.streams[0]['time_stamps']
        )
        self.markers = self.streams[0]['time_series']
        self.start_time_marker = self.marker_times[0]
        self.end_time_marker = self.marker_times[-1]
        self.n_markers = len(self.markers)
        self.marker_duration = self.end_time_marker - self.start_time_marker

        # Extract information from the audio stream
        self.audio = self.streams[1]['time_series']
        self.audio_times = self.streams[1]['time_stamps']
        self.audio_times = convert_unix_timestamps_to_datetime(
            self.audio_times
        )
        self.audio_start_time = self.audio_times[0]
        self.audio_end_time = self.audio_times[-1]
        self.audio_duration = self.audio_end_time - self.audio_start_time


    def print_info(self):
        print('***************************Audio File Info***************************')

        print("Filepath:", self.filepath)
        print("Marker :::: Start Time: {}, End Time:{}".format(
            self.start_time_marker, 
            self.end_time_marker)
        )
        print("No. Markers :", self.n_markers)
        print("Marker Duration:", self.marker_duration)

        print("Sampling Frequency:", self.sampling_frequency)
        print("Audio :::: Start Time: {}, End Time:{}".format(
            self.audio_start_time, 
            self.audio_end_time)
        )
        print("Audio Duration:", self.audio_duration)
        print('***************************************************************')
        


