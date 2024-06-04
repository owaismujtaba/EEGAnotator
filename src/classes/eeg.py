import config as config
import numpy as np

from classes.utils import loadEdfFile, normalizeEegTriggers, eegEventsMapping, correctEegTriggers, eegTransitionTriggerPoints, convertEegUnixTimestampsToDatetime

def checkInterruptions(rawData, sfreq):
    print('Checking for Interruptions')
    times = rawData.times
    interruptionsCheck = True
    timeDiff = np.diff(times)
    interruptionsIndices = np.where(timeDiff > (1 / sfreq) * config.interruptionIntervalEEG)[0]

    if len(interruptionsIndices) == 0:
        print("No interruptions detected.")
        interruptionsCheck = False
        timeGaps = None
    else:
        print("Interruptions detected:")
        timeGaps = [(times[i], times[i+1]) for i in interruptionsIndices]
        for gap in timeGaps:
            print("Gap between {:.2f}s and {:.2f}s".format(gap[0], gap[1]))
    
    return timeGaps, interruptionsCheck

class EegData:
    """
    A class to represent EEG (Electroencephalogram) data.
    """

    def __init__(self, filepathEdf):
        """
        Initialize the EEG object.

        Args:
            - filepathEdf (str): The file path to the .edf EEG data file.

        Attributes:
            - filePath (str): The filepath to the .edf EEG data file.
            - rawData (obj): The loaded raw EEG data.
            - nChannels (int): The number of channels in the EEG data.
            - badChannels (list): List of bad channels.
            - channelNames (list): Names of all channels.
            - samplingFrequency (float): Sampling frequency of the EEG data.
            - duration (float): Duration of EEG recording.
            - startTime (datetime): Start time of EEG recording.
            - timeStamps (numpy.ndarray): Array of Unix timestamps.
            - timeStampsReal (numpy.ndarray): Array of datetime objects.
            - triggers (numpy.ndarray): Trigger channel data.
            - interruptionsCheck (bool): Flag indicating if interruptions in the EEG data were checked.
            - interruptions (obj): Object storing information about interruptions in the EEG data.
            - events (numpy.ndarray): Events based on trigger changes.
        """
        
        self.filePath = filepathEdf 
        self.rawData = None

        self.nChannels = None
        self.badChannels = None
        self.channelNames = None
        self.samplingFrequency = None
        
        self.duration = None
        self.startTime = None
        self.timeStamps = None
        self.endTime = None
        self.timeStampsReal = None

        self.triggers = None
        self.interruptionsCheck = False
        self.interruptions = None
        self.events = None

        self.triggerTransitionPointsIndex = None
        self.triggerNormalized = None
        self.triggersCorrected = None

        self.loadEegData()
        self.preprocessEegData()

    
    def loadEegData(self):
        """
        Load EEG data from the .edf file.
        """
        self.rawData = loadEdfFile(self.filePath)
        self.nChannels = self.rawData.info['nchan']
        self.badChannels = list(self.rawData.info['bads'])
        self.startTime = self.rawData.info['meas_date']
        self.channelNames = self.rawData.ch_names
        self.samplingFrequency = self.rawData.info['sfreq']
        self.triggers = self.rawData['TRIG'][0][0]
        self.duration = self.rawData.n_times / self.samplingFrequency
        self.timeStamps = self.rawData.times + self.rawData.info['meas_date'].timestamp()
        self.goodChannels = [item for item in self.channelNames if item not in self.badChannels]

    def preprocessEegData(self):
        """
        Preprocess EEG data.
        """
        self.timeStampsReal = convertEegUnixTimestampsToDatetime(self.timeStamps, self.startTime)
        self.endTime = self.timeStampsReal[-1]
        self.triggerNormalized = normalizeEegTriggers(self.triggers)
        self.triggersCorrected = correctEegTriggers(self.triggerNormalized)
        self.triggerTransitionPointsIndex = eegTransitionTriggerPoints(self.triggersCorrected)
        self.events = eegEventsMapping(
            self.triggersCorrected, 
            self.triggerTransitionPointsIndex,
            self.timeStamps    
        )
        
        self.interruptions, self.interruptionsCheck = checkInterruptions(
            self.rawData,
            self.samplingFrequency
        )
        
    def printInfo(self):
        """
        Print information about the EEG data.
        """
        print("File Path:", self.filePath)
        print("Start Time:", self.startTime)
        print("Number of Channels:", self.nChannels)
        print("Bad Channels:", self.badChannels)
        print("Channel Names:", self.channelNames)
        print("Sampling Frequency:", self.samplingFrequency)
        print("Trigger Data:", self.triggers)
        print("Duration:", self.duration)
        print("Events:", self.events)
        print("Interruptions Check:", self.interruptionsCheck)
        print("Interruptions:", self.interruptions)
