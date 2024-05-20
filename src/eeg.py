import mne
import config
import pdb
import numpy as np
from datetime import  timedelta
from src.utils import load_edf_file
from src.utils import convert_unix_timestamps_to_datetime
from src.utils import normalize_triggers, find_trigger_changes
from src.utils import find_start_block_saying_time_stamp

def check_interruptions(raw_data, sfreq):
    print('Checking for Interruptions')
    times = raw_data.times
    interruptions_check = True
    
    time_diff = np.diff(times)
    interruptions_indices = np.where(time_diff > (1 / sfreq) * config.INTERRUPTION_INTERVAL_EEG)[0]

    if len(interruptions_indices) == 0:
        print("No interruptions detected.")
        interruptions_check = False
        time_gaps = None
    else:
        print("Interruptions detected:")
        time_gaps = [(times[i], times[i+1]) for i in interruptions_indices]
        for gap in time_gaps:
            print("Gap between {:.2f}s and {:.2f}s".format(gap[0], gap[1]))
    
    return time_gaps, interruptions_check



class EEG:
    """
    A class to represent EEG (Electroencephalogram) data.
    """

    def __init__(self, filepath_edf):
        """
            Initialize the EEG object.

            Args:
                - filepath_edf (str): The file path to the .edf EEG data file.
                - raw_data (obj): The loaded raw EEG data.
                - n_channels (int): The number of channels in the EEG data.
                - bad_channels (list): List of bad channels.
                - channel_names (list): Names of all channels.
                - sampling_frequency (float): Sampling frequency of the EEG data.
                - triggers (numpy.ndarray): Trigger channel data.
                - interruptions_check (bool): Flag indicating if interruptions in the EEG data were checked.
                - interruptions (obj): Object storing information about interruptions in the EEG data.
                - start_time (datetime): Start time of EEG recording.
                - duration (float): Duration of EEG recording.
                - end_time (datetime): End time of EEG recording.
                - triggers_types (numpy.ndarray): Types of triggers.
                - events (numpy.ndarray): Events based on trigger changes.
                - times (numpy.ndarray): Timestamps converted to datetime format.
        """
        self.filepath = filepath_edf 
        self.EXPERIMENT_START = None
        self.raw_data = load_edf_file(filepath_edf)
        self.n_channels = self.raw_data.info['nchan']
        self.bad_channels = self.raw_data.info['bads']
        self.channel_names = self.raw_data.ch_names
        self.sampling_frequency = self.raw_data.info['sfreq']
        self.triggers = self.raw_data['TRIG'][0][0]
        self.interruptions_check = False
        self.interruptions = None
        self.start_time = self.raw_data.info['meas_date']
        self.duration = self.raw_data.n_times / self.sampling_frequency
        self.end_time = self.start_time + timedelta(seconds=self.duration)

        self.triggers = normalize_triggers(self.triggers)
        self.triggers_types = np.unique(self.triggers)
        self.events = find_trigger_changes(self.triggers)
        self.interruptions, self.interruptions_check = check_interruptions(
            self.raw_data,
            self.sampling_frequency
        )

        self.times = convert_unix_timestamps_to_datetime(self.raw_data.times)

        self.find_start_block_saying_time_stamp()

    def find_start_block_saying_time_stamp(self):
        for i, item in enumerate(self.events):
            if item[0] == 'START_BLOCK_SAYING':
                self.EXPERIMENT_START = item[1]
                break
        
    def print_info(self):
        """
        Print information about the EEG data.
        """
        print("File Path:", self.filepath)
        print("Number of Channels:", self.n_channels)
        print("Bad Channels:", self.bad_channels)
        print("Channel Names:", self.channel_names)
        print("Sampling Frequency:", self.sampling_frequency)
        print("Trigger Data:", self.triggers)
        print("Start Time:", self.start_time)
        print("Duration:", self.duration)
        print("End Time:", self.end_time)
        print("Trigger Types:", self.triggers_types)
        print("Events:", self.events)
        print("Interruptions Check:", self.interruptions_check)
        print("Interruptions:", self.interruptions)
        print("Timestamps:", self.times)