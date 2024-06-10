***Build on Python 3.10.14***

***Naming Conventions***
1. module name : my_module_name
2. variable name : myVariableName
3. class name : MyClassName
4. function name : myFunctionName

# EEG and Audio Data Processing

This project provides a set of Python scripts and utility functions for processing EEG (Electroencephalogram) and audio data. The softawre maps the events of the eeg and the audio based on the time and the markers in audio and the triggers in the eeg. The scripts are designed to load, preprocess, and analyze EEG and audio recordings, facilitating research and experiments in neuroscience, cognitive science, and related fields.

## Features
- **EEG Data Processing**:
  - Load data from EDF files.
  - Identify significant time gaps in EEG recordings.
  - Map EEG triggers to corresponding events.
  
- **Audio Data Processing**:
  - Load data from XDF (Extensible Data Format) files.
  - Preprocess audio data, including marker bundling, timestamp conversion, and marker sequence validation.
  - Check the correctness of audio marker sequences.

- **Integration of EEG and Audio Data**:
  - Align EEG and audio events based on timestamps.
  - Map EEG actions to corresponding audio markers.
  - Map EEG events to audio events based on both timestamps and triggers.

  
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
