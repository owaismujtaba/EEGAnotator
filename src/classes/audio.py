from classes.utils import convertAudioUnixTimestampsToDatetime, loadXdfFile, calculateTimeGaps, bundleAudioMarkersWithTimestamps
import config as config



class AudioData:
    """
    A class to represent XDF (AUDIO and MARKER) data.
    """
    def __init__(self, filePathXdf) -> None:
        """
        Initialize an instance of the AudioData class.

        Parameters:
            - filePathXdf (str): The filepath to the XDF (Extensible Data Format) file.

         Attributes:
            - FilePath (str): The filepath to the XDF file.
            - Streams (list): A list containing streams of data loaded from the XDF file.
            - SamplingFrequency (float): The sampling frequency of the audio data.
            - Markers (list): List of marker data.
            - NMarkers (int): The total number of markers.
            - MarkersTimeStamps (list): List of Unix timestamps for marker data.
            - MarkersTimeStampsReal (list): List of datetime objects for marker data.
            - MarkersStartTime (datetime): The start time of the first marker.
            - MarkersEndTime (datetime): The end time of the last marker.
            - MarkersDuration (timedelta): Duration between the first and last marker.
            - Audio (list): List containing audio data.
            - AudioTimeStamps (list): List of Unix timestamps for audio sample times.
            - AudioTimeStampsReal (list): List of datetime objects for audio sample times.
            - AudioStartTime (datetime): The start time of the audio data.
            - AudioEndTime (datetime): The end time of the audio data.
            - AudioDuration (timedelta): Duration of the audio data.
            - MarkersWordsTimestampsAudioStartIndex (list): List of tuples containing marker, word, marker timestamps, and corresponding audio sample start index.
            - MarkerTimeGaps (list): List of time gaps between marker data.
            - NGapsMarkers (int): The total number of time gaps between marker data.
        """

        self.filePath = filePathXdf
        self.streams = None
        self.samplingFrequency = None

        self.markers = None
        self.nMarkers = None
        self.markersTimeStamps = None
        self.markersTimeStampsReal = None
        self.markersStartTime = None
        self.markersEndTime = None
        self.markersDuration = None

        self.audio = None
        self.audioTimeStamps = None
        self.audioTimeStampsReal = None
        self.audioStartTime = None
        self.audioEndTime = None
        self.audioDuration = None

        self.markerTimeGaps = None
        self.nGapsMarkers = None

        self.loadAudioData()
        self.preprocessAudioData()

    def loadAudioData(self):
        """
        Load audio data from XDF file and initialize relevant attributes.
        """
        print('***************************Loading Audio data***************************')

        self.streams, header = loadXdfFile(self.filePath)
        self.samplingFrequency = self.streams[1]['info']['effective_srate']
        self.markers = self.streams[0]['time_series']
        self.markersTimeStamps = self.streams[0]['time_stamps']
        self.markersStartTime = self.markersTimeStamps[0]
        self.markersEndTime = self.markersTimeStamps[-1]

        self.audio = self.streams[1]['time_series']
        self.audioTimeStamps = self.streams[1]['time_stamps']
        self.audioStartTime = self.audioTimeStamps[0]
        self.audioEndTime = self.audioTimeStamps[-1]

        self.nMarkers = len(self.markers)

    def preprocessAudioData(self):
        """
        Preprocess audio data by converting timestamps and calculating time gaps between markers.
        """
        print('***************************Preprocessing Audio data***************************')

        self.markersTimeStampsReal = convertAudioUnixTimestampsToDatetime(self.markersTimeStamps)
        self.markersStartTime = self.markersTimeStampsReal[0]
        self.markersEndTime = self.markersTimeStampsReal[-1]
        self.markersDuration = self.markersEndTime - self.markersStartTime

        self.audioTimeStampsReal = convertAudioUnixTimestampsToDatetime(self.audioTimeStamps)
        self.audioStartTime = self.audioTimeStampsReal[0]
        self.audioEndTime = self.audioTimeStampsReal[-1]
        self.audioDuration = self.audioEndTime - self.audioStartTime
        self.markersWordsTimestampsAudioStartIndex = bundleAudioMarkersWithTimestamps(self.markers, self.markersTimeStamps, self.audioTimeStamps)

        self.markerTimeGaps, self.markerTimeGapsItems = calculateTimeGaps(
                                            self.markersTimeStamps,
                                            config.gapIntervalAudioMarker
                                        )

        self.nGapsMarkers = len(self.markerTimeGaps)

    def printInfo(self):
        """
        Print detailed information about the audio file and its attributes.
        """
        print('***************************Audio File Info***************************')

        print("Filepath:", self.filePath)
        print("Sampling Frequency:", self.samplingFrequency)

        print("Marker Start Time:", self.markersStartTime)
        print("Marker End Time:", self.markersEndTime)
        print("No. of Markers:", self.nMarkers)
        print("Marker Duration:", self.markersDuration)

        print("Audio Start Time:", self.audioStartTime)
        print("Audio End Time:", self.audioEndTime)
        print("Audio Duration:", self.audioDuration)

        print("Marker Time Gaps:", self.markerTimeGaps)
        print("No. of Marker Time Gaps:", self.nGapsMarkers)

        print('***************************************************************')
