import numpy as np


def findClosestStartingPointInEeg(eegEvents, timestamp):
    """
    Finds the closest starting point in EEG events to a given timestamp.

    This function takes a list of EEG events and a timestamp and finds the EEG event with the closest 
    starting time to the given timestamp. Each EEG event is represented as a tuple: (action, start_time, 
    end_time, start_index, end_index, duration).

    Args:
        eegEvents (list of tuples): A list of EEG events.
        timestamp (float): The timestamp to find the closest starting point to.

    Returns:
        closeIndex (int): The index of the EEG event with the closest starting time to the given timestamp.

    Example:
    >>> eegEvents = [('Action1', 0.0, 2.0, 0, 10, 2), ('Action2', 2.5, 4.5, 12, 22, 2)]
    >>> timestamp = 2.7
    >>> findClosestStartingPointInEeg(eegEvents, timestamp)
    1
    """

    timestamp += 7200  # adjusting the difference in time
    eegTimestamps = [item[1] for item in eegEvents]
    diff = abs(np.array(eegTimestamps) - timestamp)
    closeIndex = np.argmin(diff)
    return closeIndex


class EegAudioData:
    def __init__(self, eegDataObj, audioDataObject) -> None:
        self.eegData = eegDataObj
        self.audioData = audioDataObject
        self.audioMarkerStartTime = self.audioData.markersTimeStamps[0]
        
        self.nearestEegStartPointToAudio = findClosestStartingPointInEeg(
            self.eegData.events, self.audioMarkerStartTime
        )

        self.mappingEegEventsWithMarkers = self.mapEegActionsToMarkerWords(
            self.nearestEegStartPointToAudio, self.eegData.events, self.audioData.markersWordsTimestampsAudioStartIndex
        )



    def mapEegActionsToMarkerWords(self, startTimestampEeg, eegEvents, markersWordsTimestamps):
        """
            Maps EEG actions to corresponding marker words and timestamps.
            
            Key Point : Assuming we have all the markers in the xdf file. No missings.
            
            Args:
                - startTimestampEeg (int): The starting index for processing EEG events.
                - eegEvents (list of tuples): A list of EEG events where each event is represented as a tuple:
                    (action, start_time, end_time, start_index, end_index, duration).
                - markersWordsTimestamps (list of tuples): A list of markers with corresponding words and timestamps,
                    where each item is represented as a tuple: (marker, word, time).

                Returns:
                - result (list of lists): A list of mapped actions to markers with their corresponding details,
                    where each item is represented as a list:
                    [marker, word, start_time, end_time, start_index, end_index, duration, time].

        """
        print('Performing the mappings')
        wordIndex = 0
        result = []

        for event in eegEvents[startTimestampEeg:]:
            action, startTime, endTime, startIndex, endIndex, duration = event

            for index in range(wordIndex, len(markersWordsTimestamps)):
                marker, word, time, audioIndex = markersWordsTimestamps[index]

                if action == marker:
                    result.append([marker, word, startTime, endTime, startIndex, endIndex, audioIndex, duration, time])
                    wordIndex = index + 1
                    break
        

        
        return result
