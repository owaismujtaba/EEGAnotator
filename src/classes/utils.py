import numpy as np
import pyxdf
import mne

#**************************************AUDIO RELATED FUNCTIONS**************************************
def bundleAudioMarkersWithTimestamps(markers, markerTimestamps, audioTimestamps):
    """
    Bundles audio markers with corresponding timestamps.

    Parameters:
        - markers (list): List of marker data.
        - markerTimestamps (list): List of timestamps corresponding to the markers.
        - audioTimestamps (np.ndarray): Array of timestamps corresponding to the audio data.

    Returns:
        - markerWordTimestamp (list): List of lists containing marker action, marker word, timestamp, and audio start index.
    """
    print('***************************Started bundling markers and audio timestamps***************************')

    markerWordTimestamp = []

    # Pre-calculate the closest audio start indices for each marker timestamp
    audioIndices = np.searchsorted(audioTimestamps, markerTimestamps)
    audioIndices = np.clip(audioIndices, 1, len(audioTimestamps) - 1)
    leftDistances = abs(audioTimestamps[audioIndices - 1] - markerTimestamps)
    rightDistances = abs(audioTimestamps[audioIndices] - markerTimestamps)
    closestIndices = np.where(leftDistances <= rightDistances, audioIndices - 1, audioIndices)

    for index in range(len(markers)):
        markerValues = markers[index][0].split(':')

        markerAction = markerValues[0]
        markerWord = markerValues[1] if len(markerValues) > 1 else '.'
        timestamp = markerTimestamps[index]
        audioStartIndex = closestIndices[index]

        markerWordTimestamp.append([markerAction, markerWord, timestamp, audioStartIndex])

    return markerWordTimestamp

def convertAudioUnixTimestampsToDatetime(timestamps, start=None):
    """
    Convert Unix timestamps to datetime objects using NumPy vectorized operations.

    Parameters:
        timestamps (array_like): Array of Unix timestamps.
        start (str or datetime-like, optional): The start time to add to the converted datetime objects.
            If None, the default start time is '1970-01-01T00:00:00.000'.

    Returns:
        datetimeObjects (np.ndarray): Array of corresponding datetime objects.
    """
    if start is None:
        start = '1970-01-01T00:00:00.000'
    else:
        start = np.datetime64(start) + np.timedelta64(2, 'h')  # Add two hours of delay

    datetimeObjects = np.datetime64(start, 'ms') + np.timedelta64(2, 'h') + (timestamps * 1000).astype('timedelta64[ms]')

    return datetimeObjects

def checkAudioMarkers(markers):
    """
        This function checks if the sequences of audio markers follow the correct order.
        Each marker is expected to be a tuple where the first element is a string in the format 'Action:Word'.
        The correct sequence for each word should be:
        StartReading -> EndReading -> StartSaying -> EndSaying
        
        Parameters:
            markers (list of Lists): A list of audio markers.

        Returns:
            tuple: A boolean indicating if all sequences are complete, and a list of lists with indices of incomplete sequences.
    """

    print('Checking audio markers')
    currentState = 'START'  
    incompleteIndices = [] 
    tempWrongIndices = []  

    prevWord = None  
    word = None  

    for i, marker in enumerate(markers):
        event = marker[0].split(':')
        if len(event) != 2:
            continue  

        action, word = event
        prevWord = prevWord if prevWord is not None else word

        if word != prevWord and currentState != 'START':
            incompleteIndices.append(tempWrongIndices.copy())
            tempWrongIndices.clear()
            currentState = 'START'

        tempWrongIndices.append(i)  

        # State transitions based on the action and currentState
        if currentState == 'START' and action == 'StartReading':
            currentState = 'StartReading'
        elif currentState == 'StartReading' and action == 'EndReading':
            currentState = 'EndReading'
        elif currentState == 'EndReading' and action == 'StartSaying':
            currentState = 'StartSaying'
        elif currentState == 'StartSaying' and action == 'EndSaying':
            currentState = 'START'
            tempWrongIndices.clear()  
        else:
            incompleteIndices.append(tempWrongIndices.copy())
            tempWrongIndices.clear()
            currentState = 'START'

        prevWord = word  

    result = len(incompleteIndices) == 0  

    return result, incompleteIndices

def loadXdfFile(filepath):
    """
        Load data from an XDF (Extensible Data Format) file.

        Parameters:
        - filepath (str): The filepath to the XDF file.

        Returns:
        - streams (list): A list containing streams of data loaded from the XDF file using pyxdf library.
        - header (dict): A dictionary containing header information of the XDF file.

        Dependencies:
        - pyxdf: Python library for reading XDF files.
    """
    print('*********************************************************************************')
    print('***************************Loading .xdf file***************************')
    
    # Use pyxdf library to load data from the XDF file
    streams, header = pyxdf.load_xdf(filepath)
    print('*******************************Completed*******************************')

    return streams, header


#**************************************EEG RELATED FUNCTIONS**************************************

def eegTransitionTriggerPoints(triggerArray):
    """
    Identifies the transition points in an EEG trigger array.

    This function takes a 1D numpy array of EEG trigger values and identifies the indexes where
    transitions occur. A transition is defined as a change from a lower value to a higher value 
    between consecutive elements in the trigger array. The function returns an array of indexes 
    indicating the positions of these transition points.

    Parameters:
    triggerArray (np.ndarray): A 1D numpy array containing the trigger values from EEG data.

    Returns:
    np.ndarray: An array of indexes where transitions occur in the trigger array. The first 
                element of the returned array is always 0 to indicate the start of the array.
                
    Example:
    >>> triggerArray = np.array([0, 0, 1, 1, 0, 0, 1, 1, 0])
    >>> EegTransitionTriggerPoints(triggerArray)
    array([0, 2, 6])
    """
    
    differenceArray = np.where(np.diff(triggerArray) > 0)[0] + 1
    transitionPointsIndexes = np.array([0] + differenceArray.tolist())
  
    return transitionPointsIndexes

def triggerEncodings(code):
    """
    Converts trigger codes into their corresponding marker names based on a predefined dictionary.
    If the exact code is not found, the closest code is used.

    This function maps an integer trigger code to a human-readable marker name using a predefined 
    dictionary of codes and their corresponding marker names. If the exact code is not found in the 
    dictionary, the function finds and returns the marker name of the closest available code.

    Parameters:
    code (int): Trigger code to be converted.

    Returns:
        str: Corresponding marker name if the code is found in the dictionary. If the exact code is 
         not found, the marker name of the closest code is returned.

    Example:
    >>> TriggerEncodings(200)
    'StartSaying'

    >>> TriggerEncodings(10)
    'ExperimentEnded'
    """
    
    markerNames = {
        255: 'StartReading',
        224: 'EndReading',
        192: 'StartSaying',
        160: 'EndSaying',
        128: 'StartBlockSaying',
        96: 'StartBlockThinking',
        64: 'EXPERIMENT_RESTART',
        32: 'ExperimentResting',
        16: 'ExperimentStarted',
        8: 'ExperimentEnded'
    }

    markerName = markerNames.get(code)
    
    if markerName:
        return markerName
    
    closestCode = min(markerNames.keys(), key=lambda k: abs(k - code))
    closestMarkerName = markerNames[closestCode]
    
    return closestMarkerName

def eegEventsMapping(triggerArray, triggerPoints, timestamps):
    """
    Maps EEG trigger values to their corresponding start and end points.

    This function takes an array of trigger values, an array of trigger points (indexes where trigger 
    values change), and an array of timestamps. It identifies events based on the trigger values and 
    maps them to their start and end points. Each event is represented by its corresponding marker 
    name, start timestamp, end timestamp, start index, end index, and duration.

    Parameters:
    triggerArray (np.ndarray): An array of trigger values recorded during the EEG session.
    triggerPoints (np.ndarray): An array of indexes in the trigger values array where the trigger values change.
    timestamps (np.ndarray): An array of timestamps corresponding to the trigger values.

    Returns:
    List[List]: A list of lists, each representing an event with the following information:
        - Marker name (str)
        - Start timestamp (float)
        - End timestamp (float)
        - Start index (int)
        - End index (int)
        - Duration (int)
    
    Example:
    >>> triggerArray = np.array([0, 0, 1, 1, 0, 0, 2, 2, 0])
    >>> triggerPoints = np.array([0, 2, 6])
    >>> timestamps = np.array([0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0])
    >>> EegEventsMapping(triggerArray, triggerPoints, timestamps)
    [['StartReading', 0.0, 1.0, 0, 2, 2],
     ['EndReading', 2.0, 3.0, 6, 8, 2]]
    """
    
    eventsStartEnd = []

    for i in range(triggerPoints.shape[0] - 1):
        
        start = triggerPoints[i]
        end = triggerPoints[i + 1]
        event = triggerEncodings(triggerArray[start])
        
        if end - start < 25:
            continue
        eventsStartEnd.append([event, timestamps[start], timestamps[end], start, end, end - start])
        
    return eventsStartEnd

def calculateTimeGaps(timeArray, timeInterval):
    """
    Identifies significant time gaps in an array of timestamps.

    This function takes an array of timestamps and a time interval. It calculates the differences 
    between consecutive timestamps and identifies those differences that are greater than the given 
    time interval. The function returns the time gaps and the corresponding timestamps where these 
    gaps occur.

    Parameters:
    timeArray (np.ndarray): An array of timestamps.
    timeInterval (int): The threshold time interval to identify significant gaps.

    Returns:
    Tuple[np.ndarray, np.ndarray]: 
        - An array of time gaps that are greater than the specified time interval.
        - An array of timestamps corresponding to the identified time gaps.

    Example:
    >>> timeArray = np.array([0, 1, 2, 5, 6, 10])
    >>> timeInterval = 2
    >>> CalculateTimeGaps(timeArray, timeInterval)
    (array([3, 4]), array([5, 10]))
    """
    
    differences = np.diff(timeArray).astype('int')
    indices = np.where(differences > timeInterval)[0]

    timeGaps = differences[indices]
    correspondingItems = timeArray[1:][indices]
    
    return timeGaps, correspondingItems

def correctEegTriggers(triggers):
    """
    Corrects a list of EEG triggers by mapping them to the nearest valid code
    from a predefined set of correct codes.

    This function takes a list of integer EEG trigger codes and corrects them by mapping 
    each trigger to the nearest valid code from a predefined set of valid codes. If a trigger 
    code is not in the predefined set, it is mapped to the closest valid code.

    Parameters:
    triggers (list of int): A list of integer trigger codes to be corrected.

    Returns:
    list of int: A list of corrected trigger codes. Each input trigger is either directly 
                 mapped if it exists in the valid codes, or mapped to the nearest valid code 
                 if it does not.

    Example:
    >>> triggers = [5, 20, 100, 130]
    >>> CorrectEegTriggers(triggers)
    [8, 16, 96, 128]
    """

    correctCodings = {
        255: 255, 224: 224, 192: 192, 160: 160,
        128: 128, 96: 96, 64: 64, 32: 32, 16: 16, 8: 8
    }

    validCodes = sorted(correctCodings.keys())

    maxTrigger = max(validCodes)
    nearestCodeMap = {}

    for i in range(maxTrigger + 1):
        nearestCode = min(validCodes, key=lambda x: abs(x - i))
        nearestCodeMap[i] = correctCodings[nearestCode]

    correctedTriggers = []
    for trigger in triggers:
        if trigger in nearestCodeMap:
            correctedTriggers.append(nearestCodeMap[trigger])
        else:
            correctedTriggers.append(nearestCodeMap[maxTrigger])
    
    return correctedTriggers

def normalizeEegTriggers(triggerValues):
    """
    Normalizes EEG trigger values to a range from 0 to 255.

    This function normalizes an array of EEG trigger values using the formula:
    normalizedValue = (triggerValue - triggerMin) / (triggerMax - triggerMin) * 255.
    The trigger values are first inverted (multiplied by -1) before normalization. The resulting 
    normalized values are rounded to the nearest integer.

    Parameters:
    triggerValues (np.ndarray): Array containing trigger values to be normalized.

    Returns:
    np.ndarray: Array of normalized trigger values rounded to the nearest integer.

    Example:
    >>> triggerValues = np.array([10, 20, 30, 40, 50])
    >>>
        >>> triggerValues = np.array([10, 20, 30, 40, 50])
    >>> NormalizeEegTriggers(triggerValues)
    array([255, 204, 153, 102,  51])
    """
    
    triggerValues = triggerValues * -1
    triggerMin = np.min(triggerValues)
    triggerMax = np.max(triggerValues)
    
    normalizedTriggers = (triggerValues - triggerMin) / (triggerMax - triggerMin) * 255
    normalizedTriggers = np.round(normalizedTriggers).astype(int)
    
    return normalizedTriggers

def convertEegUnixTimestampsToDatetime(timestamps, start):
    """
    Convert Unix timestamps to datetime objects using NumPy vectorized operations.

    This function takes an array of Unix timestamps and converts them into corresponding 
    datetime objects. The conversion is done using NumPy vectorized operations for efficiency. 
    A start time is provided as a reference point for the conversion.

    Parameters:
    timestamps (array_like): Array of Unix timestamps.
    start (str or datetime-like): The start time to add to the converted datetime objects.

    Returns:
    datetime_objects (np.ndarray): Array of corresponding datetime objects.

    Example:
    >>> timestamps = np.array([1621914057, 1621914058, 1621914059])
    >>> startTime = np.datetime64('2022-05-25T00:00:00')
    >>> ConvertEegUnixTimestampsToDatetime(timestamps, startTime)
    array(['2022-05-25T00:00:57.000', '2022-05-25T00:00:58.000',
           '2022-05-25T00:00:59.000'], dtype='datetime64[ms]')
    """
    
    return timestamps.astype('datetime64[s]')

def loadEdfFile(filepath):
    """
    Load data from an EDF (European Data Format) file.

    This function loads raw EEG data from an EDF file using the MNE library, a Python library 
    for EEG data analysis.

    Parameters:
    - filepath (str): The filepath to the EDF file.

    Returns:
    - streams (object): Raw EEG data object loaded from the EDF file using the MNE library.

    Dependencies:
    - mne: Python library for EEG data analysis.

    Example:
    >>> filepath = "path/to/your/file.edf"
    >>> eegData = LoadEdfFile(filepath)
    """
    print('*********************************************************************************')
    print('***************************Loading .edf file***************************')
    
    # Use mne library to read the raw EEG data from the EDF file
    print(filepath)
    streams = mne.io.read_raw_edf(filepath, preload=True)
    print('*******************************Completed*******************************')

    return streams

#******************************************EEG_AUDIO_FUNCTION **********************************

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