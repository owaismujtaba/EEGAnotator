***Build on Python 3.10.14***

***Naming Conventions***
1. module name : my_module_name
2. variable name : myVariableName
3. class name : MyClassName
4. function name : myFunctionName

# EEG and Audio Data Integration System

## Overview:

The EEG and Audio Data Integration System is a software tool designed to facilitate the analysis and synchronization of EEG (Electroencephalogram) and audio data for research purposes. By aligning EEG signals with audio stimuli, researchers can gain insights into cognitive processes, brain activity, and auditory perception.

## Features:

- Load and preprocess EEG data from EDF (European Data Format) files.
- Extract marker data and timestamps from audio recordings in XDF (Extensible Data Format) files.
- Integrate EEG and audio data streams by mapping EEG events to corresponding audio markers.
- Provide a user-friendly GUI (Graphical User Interface) for data visualization and synchronization.
- Implement utility functions for timestamp conversion, trigger mapping, and time gap analysis.

## Components:

### 1. EEG Module (`eeg.py`):

- **Loading and Preprocessing:** Utilizes the MNE library to load raw EEG data from EDF files and preprocess it for analysis.
- **Trigger Analysis:** Identifies trigger points, maps trigger codes to events, and calculates time gaps between events.
- **Data Normalization:** Normalizes trigger values and converts timestamps to datetime objects for consistency.

### 2. Audio Module (`audio.py`):

- **Loading and Preprocessing:** Uses the PyXDF library to load audio data from XDF files and extract marker information.
- **Marker Bundling:** Bundles audio markers with corresponding timestamps and calculates time gaps between markers.
- **Timestamp Conversion:** Converts Unix timestamps to datetime objects for synchronization with EEG data.

### 3. EEG-Audio Integration Module (`eeg_audio.py`):

- **Synchronization:** Integrates EEG and audio data streams by aligning EEG events with audio markers.
- **Mapping:** Maps EEG actions to marker words and timestamps, enabling synchronization between EEG and audio data.
- **Closest Starting Point Detection:** Finds the closest starting point in EEG events based on audio marker timestamps.

### 4. Utility Functions (`utils.py`):

- **Shared Functions:** Contains utility functions shared across modules, such as timestamp conversion and trigger mapping.
- **Time Gap Analysis:** Identifies significant time gaps in timestamp arrays and corrects EEG trigger codes for consistency.

### 5. Graphical User Interface (GUI):

- **User-Friendly Interface:** Provides an intuitive interface for loading data files, visualizing EEG and audio data, and performing synchronization tasks.
- **Customization Options:** Allows users to adjust settings, select visualization parameters, and interact with synchronized data.

## Workflow:

1. **Data Loading:** Researchers load EEG and audio data files into the system using the GUI.
2. **Preprocessing:** The EEG and audio modules preprocess the data, extracting relevant information such as trigger values and timestamps.
3. **Integration:** The EEG-audio integration module aligns EEG events with audio markers, enabling synchronization between the two data streams.
4. **Visualization and Analysis:** Researchers visualize synchronized data and perform further analysis using built-in tools and functions.

## Conclusion:

The EEG and Audio Data Integration System offers a comprehensive solution for researchers working with EEG and audio data. By providing robust data processing capabilities and an intuitive user interface, the system streamlines the analysis process and facilitates meaningful insights into brain-behavior relationships.

  
## Prerequisites

Before running the scripts, make sure you have the following dependencies installed:

- Python 3.10.14
- NumPy
- MNE (for EEG data processing)
- PyXDF (for loading XDF files)
- Other required libraries as specified in `requirements.txt`

## Usage

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/owaismujtaba/EEGAnotator.git
   cd EEGAnotator
   pip install -r requirements.txt
   python src/main.py
