import pyxdf
import pdb
from utils import convert_unix_timestamps_to_datetime


def load_xdf_file(filepath):
    print('Loading .xdf file')
    streams, _ = pyxdf.load_xdf(filepath)

    return streams

class AUDIO:
    def __init__(self, filepath_xdf) -> None:
        self.filepath = filepath_xdf
        pdb.set_trace()
        self.streams, header = load_xdf_file(filepath_xdf)
        self.start_time = header['info']['datetime'][0]
        self.sampling_frequency = self.streams[1]['info']['effective_srate']
        self.marker_times = convert_unix_timestamps_to_datetime(
            self.streams[0]['time_stamps']
        )
        self.markers = self.streams[0]['time_series']
        self.n_markers = len(self.markers)
        self.audio = self.streams[1]['time_stamps']
        self.audio_times = self.streams[1]['time_series']
        self.audio_times = convert_unix_timestamps_to_datetime(
            self.audio_times
        )
        self.end_time = self.marker_times[-1]
        self.duration = self.end_time - self.start_time

    def print_info(self):
        print('***************************Audio File Info***************************')

        print("Filepath:", self.filepath)
        print("Start Time: {}, End Time:{}".format(
            self.start_time, 
            self.end_time)
        )
        print("Sampling Frequency:", self.sampling_frequency)
        print("Duration:", self.duration)
        print('***************************************************************')


