import mne
import config
import pdb
import numpy as np
from datetime import  timedelta
from src.utils import load_edf_file

def check_interruptions(raw_data, sfreq):
    print('Checking for Interruptions')
    times = raw_data.times
    interruptions_check = True
    
    time_diff = np.diff(times)
    interruptions_indices = np.where(time_diff > (1 / sfreq) * config.INTERRUPTION_INTERVAL)[0]

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
    def __init__(self, filepath_edf) -> None:
        """
            Initialize an instance of the EEG class.

            Parameters:
            - filepath_edf (str): The filepath to the EDF (European Data Format) file.

            Attributes:
            - filepath (str): The filepath to the EDF file.
            - raw_data (object): Loaded EDF raw data object.
            - n_channels (int): Number of EEG channels.
            - channel_names (list): Names of EEG channels.
            - sampling_frequency (float): Sampling frequency of the EEG data.
            - triggers (array): Array containing trigger data.
            - interruptions_check (bool): Flag indicating if interruptions are present.
            - interruptions (object): Object containing information about interruptions.
            - start_time (datetime): Start time of the EEG recording.
            - duration (float): Duration of the EEG recording in seconds.
            - end_time (datetime): End time of the EEG recording.

            Helper Functions:
            - check_interruptions(): Helper function to check for interruptions in EEG data.
        """
        self.filepath = filepath_edf 
        self.raw_data = load_edf_file(filepath_edf)
        self.n_channels = self.raw_data.info['nchan']
        self.channel_names = self.raw_data.ch_names
        self.sampling_frequency = self.raw_data.info['sfreq']
        self.triggers = self.raw_data['TRIG'][0][0] # Assuming 'TRIG' is the trigger channel
        self.interruptions_check = False
        self.interruptions = None
        self.start_time = self.raw_data.info['meas_date']
        self.duration = self.raw_data.n_times / self.sampling_frequency
        self.end_time = self.start_time + timedelta(seconds=self.duration)

        # Check for interruptions in the EEG data
        self.interruptions, self.interruptions_check = check_interruptions(
            self.raw_data,
            self.sampling_frequency
        )


    def print_info(self):
        print('***************************EEG File Info***************************')

        print("Filepath:", self.filepath)
        print("Start Time: {}, End Time:{}".format(
            self.start_time, 
            self.end_time)
        )
        print("Number of Channels:", self.n_channels)
        print("Sampling Frequency:", self.sampling_frequency)
        print("Number of data points:", self.raw_data.n_times)
        print("No. of Triggers:", len(self.triggers))
        print("Duration (seconds):", self.duration)
        print("Interruptions Check:", self.interruptions_check)
        print("Interruptions:", self.interruptions)
        print('***************************************************************')
        print("Channel Names:", self.channel_names)
        print('***************************************************************')

        #pdb.set_trace()

    
        
    