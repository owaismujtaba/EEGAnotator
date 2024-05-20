import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt
import numpy as np
from pydub import AudioSegment
import pygame
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

class AudioPlayer(QMainWindow):
    def __init__(self):
        super().__init__()

        # Initialize pygame mixer
        pygame.mixer.init()

        # Create a sample numpy array representing audio data
        self.audio_array = np.random.uniform(-1, 1, 44100).astype(np.float32)

        # Convert the numpy array to an AudioSegment
        self.audio_segment = self.array_to_audio_segment(self.audio_array)

        # Save the AudioSegment to a temporary file
        self.audio_segment.export("temp_audio.wav", format="wav")

        # Set up the user interface
        self.init_ui()

    def array_to_audio_segment(self, array, sample_rate=44100):
        # Convert numpy array to pydub AudioSegment
        audio_segment = AudioSegment(
            array.tobytes(), 
            frame_rate=sample_rate, 
            sample_width=array.dtype.itemsize, 
            channels=1
        )
        return audio_segment

    def init_ui(self):
        self.setWindowTitle('PyQt5 Audio Player with Waveform')

        # Create buttons
        play_button = QPushButton('Play')
        pause_button = QPushButton('Pause')
        stop_button = QPushButton('Stop')

        # Connect buttons to their respective methods
        play_button.clicked.connect(self.play_audio)
        pause_button.clicked.connect(self.pause_audio)
        stop_button.clicked.connect(self.stop_audio)

        # Set up the matplotlib figure and canvas
        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)

        # Plot the waveform
        self.plot_waveform(self.audio_array)

        # Set up layout
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        layout.addWidget(play_button)
        layout.addWidget(pause_button)
        layout.addWidget(stop_button)

        # Set the central widget
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def plot_waveform(self, audio_array):
        self.ax.clear()
        self.ax.plot(audio_array)
        self.ax.set_title("Waveform")
        self.ax.set_xlabel("Samples")
        self.ax.set_ylabel("Amplitude")
        self.canvas.draw()

    def play_audio(self):
        pygame.mixer.music.load("temp_audio.wav")
        pygame.mixer.music.play()

    def pause_audio(self):
        pygame.mixer.music.pause()

    def stop_audio(self):
        pygame.mixer.music.stop()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = AudioPlayer()
    window.show()
    sys.exit(app.exec_())
