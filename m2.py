from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.uic import loadUiType
from PyQt5.QtWidgets import QApplication, QFileDialog
import pandas as pd
import pyqtgraph as pg
import sys
import numpy as np
from os import path
import functools
import scipy
from scipy.io import wavfile
from numpy.fft import fft
from pyqtgraph import ImageView
from scipy.io import wavfile

# Load the UI file and connect it with the Python file
FORM_CLASS, _ = loadUiType(path.join(path.dirname(__file__), "smoothingWindow.ui"))


class MainApp(QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """
        Constructor to initiate the main window in the design.

        Parameters:
        - parent: The parent widget, which is typically None for the main window.
        """
        super(MainApp, self).__init__(parent)
        self.setupUi(self)
        # self.setFixedSize(750, 600)
        self.rectangle = True
        self.hamming = False
        self.hanning = False
        self.gaussian = False
        self.handle_button()
        # Generating a uniformly distributed signal with 100 data points between 0 and 10
        self.signal = self.generate_signal(num_frequencies=100, duration=1, num_points=200)
        self.visualize_window()

    def handle_button(self):
        self.window_comboBox.currentIndexChanged.connect(self.select_window)
        self.parameter_slider.valueChanged.connect(self.visualize_window)

    def visualize_window(self):
        selected_window = self.window_comboBox.currentText()
        freqs, amps = self.get_frequency_amplitude(self.signal)
        scale_factor =  self.parameter_slider.value() / 50
        freqs, amps, modified_signal_time, window_title = self.apply_window_to_frequency_range( freqs, amps, 20, 40, scale_factor, selected_window)

        self.graphicsView.clear()
        self.graphicsView2.clear()
        self.graphicsView.plot(freqs, amps, pen='b')
        # set label and title
        self.graphicsView.setTitle(window_title)
        self.graphicsView.setLabel('left', 'Amplitude')
        self.graphicsView.setLabel('bottom', 'Frequency')
        self.graphicsView2.setTitle('Time Domain')
        self.graphicsView2.setLabel('left', 'Amplitude')
        self.graphicsView2.setLabel('bottom', 'Time')
        self.graphicsView2.plot(modified_signal_time.real)

    # Function to apply a window to a specific frequency range
    def apply_window_to_frequency_range(self, freqs, amps, start_freq, end_freq, scale_factor, selected_window='Select window', sampledrate = 200):

        # Find indices corresponding to start and end frequencies
        start_index = np.where(freqs >= start_freq)[0][0]
        end_index = np.where(freqs <= end_freq)[0][-1]


        # Apply the window function to the specific frequency range in the time domain
        if selected_window == "Hamming":
            window = self.hamming_window(end_index - start_index + 1)
            window_title = "Hamming Window Function"
        elif selected_window == "Hanning":
            window = self.hanning_window(end_index - start_index + 1)
            window_title = "Hanning Window Function"
        elif selected_window == "Gaussian":
            window = self.gaussian_window(end_index - start_index + 1)
            window_title = "Gaussian Window Function"
        elif selected_window == "Rectangle":
            window = self.rectangular_window(end_index - start_index + 1)
            window_title = "Rectangular Window Function"
        else:
            window = 1
            scale_factor = 1
            window_title = "No Window Function"

        amps[start_index:end_index + 1] *= window * scale_factor
        modified_signal_time = np.fft.irfft(amps).real
        print(sampledrate)
        scipy.io.wavfile.write('music_trash/processed_signal.wav', sampledrate, modified_signal_time.real.astype(np.int16))

        return  freqs, amps, modified_signal_time, window_title

    def select_window(self):
        selected_mode = self.window_comboBox.currentText()
        if selected_mode == 'Rectangle':
            self.rectangle = True
            self.hamming = False
            self.hanning = False
            self.gaussian = False
            self.label.setText('Window size')


        elif selected_mode == 'Hamming':
            self.rectangle = False
            self.hamming = True
            self.hanning = False
            self.gaussian = False
            self.label.setText('Window size')


        elif selected_mode == 'Hanning':
            self.rectangle = False
            self.hamming = False
            self.hanning = True
            self.gaussian = False
            self.label.setText('Window size')


        elif selected_mode == 'Gaussian':
            self.rectangle = False
            self.hamming = False
            self.hanning = False
            self.gaussian = True
            self.label.setText('Window size')

        self.visualize_window()

    # Define window functions
    def rectangular_window(self, window_size):
        return np.ones(window_size)

    def hamming_window(self, window_size):
        return np.hamming(window_size)

    def hanning_window(self, window_size):
        return np.hanning(window_size)

    def gaussian_window(self, window_size, sigma=1):
        return np.exp(-0.5 * ((np.arange(window_size) - (window_size - 1) / 2) / sigma) ** 2)

    # def set_label_text(self):
    #     if self.rectangle:
    #         self.label.setText('Window size')
    #     elif self.hamming:
    #
    #     elif self.hanning:
    #
    #     elif self.gaussian:

    def adjust_window_size(self, window, signal):
        # Adjust window size to match the signal length
        if len(window) != len(signal):
            window = np.resize(window, len(signal))
        return window

    def generate_signal(self, num_frequencies=5, duration=1, num_points=200):
        # Generating a signal with multiple frequencies
        t = np.linspace(0, duration, num_points, endpoint=False)  # Time points
        frequencies = np.random.uniform(1, 100, num_frequencies)  # Generate random frequencies
        amplitudes = np.random.rand(num_frequencies)  # Random amplitudes for each frequency

        signal = np.sum([amp * np.sin(2 * np.pi * freq * t) for freq, amp in zip(frequencies, amplitudes)], axis=0)
        return signal



    def get_amplitudes_in_range(self, freqs, amplitudes, start_freq, end_freq):
        # Find the indices corresponding to start and end frequencies
        start_index = np.where(freqs >= start_freq)[0][0]
        end_index = np.where(freqs <= end_freq)[0][-1]

        # Extract amplitudes within the frequency range
        amplitudes_in_range = amplitudes[start_index:end_index + 1]
        freqs_in_range = freqs[start_index:end_index + 1]

        return freqs_in_range, amplitudes_in_range,start_index ,end_index

    def get_frequency_amplitude(self,sig):
        N = len(sig)
        T = 1 / 200  # Sample spacing (assuming 1000 samples)
        freqs = np.fft.fftfreq(N, T)[:N // 2]  # Get the frequencies
        fft_vals = np.fft.fft(sig)  # Compute FFT
        fft_vals = 2.0 / N * np.abs(fft_vals[0:N // 2])  # Get amplitude

        return freqs, fft_vals


def main():  # method to start app
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    app.exec_()  # infinite Loop


if __name__ == '__main__':
    main()
