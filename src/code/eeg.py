import config as config
import numpy as np
from code.utils import load_edf_file
from code.utils import normalize_eeg_triggers
from code.utils import eeg_events_mapping
from code.utils import correct_eeg_triggers
from code.utils import eeg_transition_trigger_points
from code.utils import convert_eeg_unix_timestamps_to_datetime


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

class EEG_DATA:
    """
    A class to represent EEG (Electroencephalogram) data.
    """

    def __init__(self, filepath_edf):
        """
        Initialize the EEG object.

        Args:
            - filepath_edf (str): The file path to the .edf EEG data file.

        Attributes:
            - FILEPATH (str): The filepath to the .edf EEG data file.
            - RAW_DATA (obj): The loaded raw EEG data.
            - N_CHANNELS (int): The number of channels in the EEG data.
            - BAD_CHANNELS (list): List of bad channels.
            - CHANNEL_NAMES (list): Names of all channels.
            - SAMPLING_FREQUENCY (float): Sampling frequency of the EEG data.
            - DURATION (float): Duration of EEG recording.
            - START_TIME (datetime): Start time of EEG recording.
            - TIME_STAMPS (numpy.ndarray): Array of Unix timestamps.
            - TIME_STAMPS_REAL (numpy.ndarray): Array of datetime objects.
            - TRIGGERS (numpy.ndarray): Trigger channel data.
            - INTERRUPTIONS_CHECK (bool): Flag indicating if interruptions in the EEG data were checked.
            - INTERRUPTIONS (obj): Object storing information about interruptions in the EEG data.
            - EVENTS (numpy.ndarray): Events based on trigger changes.
        """
        
        self.FILEPATH = filepath_edf 
        self.RAW_DATA = None

        self.N_CHANNELS = None
        self.BAD_CHANNELS = None
        self.CHANNEL_NAMES = None
        self.SAMPLING_FREQUENCY = None
        
        self.DURATION = None
        self.START_TIME = None
        self.TIME_STAMPS = None
        self.END_TIME = None
        self.TIME_STAMPS_REAL = None

        self.TRIGGERS = None
        self.INTERRUPTIONS_CHECK = False
        self.INTERRUPTIONS = None
        self.EVENTS = None

        self.TRIGGER_TRANSITION_POINTS_INDEX = None
        self.TRIGGER_NORMALIZED = None
        self.TRIGGERS_CORRECTED =None

        self.load_eeg_data()
        self.preprocess_eeg_data()

    
    def load_eeg_data(self):
        """
        Load EEG data from the .edf file.
        """
        self.RAW_DATA = load_edf_file(self.FILEPATH)
        self.N_CHANNELS = self.RAW_DATA.info['nchan']
        self.BAD_CHANNELS = self.RAW_DATA.info['bads']
        self.START_TIME = self.RAW_DATA.info['meas_date']
        self.CHANNEL_NAMES = self.RAW_DATA.ch_names
        self.SAMPLING_FREQUENCY = self.RAW_DATA.info['sfreq']
        self.TRIGGERS = self.RAW_DATA['TRIG'][0][0]
        self.DURATION = self.RAW_DATA.n_times / self.SAMPLING_FREQUENCY
        self.TIME_STAMPS = self.RAW_DATA.times + self.RAW_DATA.info['meas_date'].timestamp()
        

    def preprocess_eeg_data(self):
        """
        Preprocess EEG data.
        """
        self.TIME_STAMPS_REAL = convert_eeg_unix_timestamps_to_datetime(self.TIME_STAMPS, self.START_TIME)
        self.END_TIME = self.TIME_STAMPS_REAL[-1]
        self.TRIGGER_NORMALIZED = normalize_eeg_triggers(self.TRIGGERS)
        self.TRIGGERS_CORRECTED = correct_eeg_triggers(self.TRIGGER_NORMALIZED)
        self.TRIGGER_TRANSITION_POINTS_INDEX = eeg_transition_trigger_points(self.TRIGGERS_CORRECTED)
        self.EVENTS = eeg_events_mapping(
            self.TRIGGERS_CORRECTED, 
            self.TRIGGER_TRANSITION_POINTS_INDEX,
            self.TIME_STAMPS    
        )
        
        self.INTERRUPTIONS, self.INTERRUPTIONS_CHECK = check_interruptions(
            self.RAW_DATA,
            self.SAMPLING_FREQUENCY
        )
        
    def print_info(self):
        """
        Print information about the EEG data.
        """
        print("File Path:", self.FILEPATH)
        print("Start Time:", self.START_TIME)
        print("Number of Channels:", self.N_CHANNELS)
        print("Bad Channels:", self.BAD_CHANNELS)
        print("Channel Names:", self.CHANNEL_NAMES)
        print("Sampling Frequency:", self.SAMPLING_FREQUENCY)
        print("Trigger Data:", self.TRIGGERS)
        print("Duration:", self.DURATION)
        print("Events:", self.EVENTS)
        print("Interruptions Check:", self.INTERRUPTIONS_CHECK)
        print("Interruptions:", self.INTERRUPTIONS)