from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.uic import loadUiType
from PyQt5.QtWidgets import QApplication 
import sys
import numpy as np
from os import path     
from numpy.fft import rfft,rfftfreq,irfft

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
      

    def apply_window_to_frequency_range(self, freqs, amps, transformed, start_freq, end_freq, scale_factor,
                                         selected_window='Select window', sampledrate=200):
        """
        Applies a window function to a specified frequency range.

        Parameters:
        - freqs: Frequency array.
        - amps: Amplitude array.
        - transformed: Transformed signal.
        - start_freq: Start frequency of the range.
        - end_freq: End frequency of the range.
        - scale_factor: Scaling factor based on the slider value.
        - selected_window: Selected window type.
        - sampledrate: Sampling rate.

        Returns:
        - Tuple containing processed frequencies, amplitudes, complex coefficients, and the applied window.
        """
        start_index = np.where(freqs >= start_freq)[0][0]
        end_index = np.where(freqs <= end_freq)[0][-1]
        freqs_in_range = freqs[start_index:end_index + 1]

        # Apply the window function to the specific frequency range in the time domain
        if selected_window == "Hamming":
            window = self.hamming_window(end_index - start_index + 1)
        elif selected_window == "Hanning":
            window = self.hanning_window(end_index - start_index + 1)
        elif selected_window == "Gaussian":
            window = self.gaussian_window(end_index - start_index + 1)
        elif selected_window == "Rectangle":
            window = self.rectangular_window(end_index - start_index + 1)
        else:
            window = 1
            scale_factor = 1
         
        amps[start_index:end_index + 1] *= window * scale_factor

        phases = np.angle(transformed)
        complex_coefficients = amps * np.exp(1j * phases)

        return  freqs, amps, complex_coefficients, window * scale_factor



    def Fourier_Transform_Signal(self, amplitude_signal, sampling_rate):
        """
        Computes the Fourier Transform of the input signal.

        Parameters:
        - amplitude_signal: Amplitude signal.
        - sampling_rate: Sampling rate.

        Returns:
        - Tuple containing magnitude frequency components and corresponding frequency components.
        """
        number_of_samples = len(amplitude_signal)
        sampling_period = 1/sampling_rate
        magnitude_freq_components = rfft(amplitude_signal)
        frequency_components = rfftfreq(number_of_samples,sampling_period)

        return magnitude_freq_components,frequency_components



    def Get_Max_Frequency(self, amplitude_signal, sampling_rate):
        """
        Finds the frequency corresponding to the maximum magnitude in the signal.

        Parameters:
        - amplitude_signal: Amplitude signal.
        - sampling_rate: Sampling rate.

        Returns:
        - Max frequency.
        """
        number_of_samples = len(amplitude_signal)
        sampling_period = 1 / sampling_rate
        # Compute magnitude frequency components
        magnitude_freq_components = np.abs(rfft(amplitude_signal))
        # Exclude the zero frequency component
        magnitude_freq_components[0] = 0
        # Compute frequency components
        frequency_components = rfftfreq(number_of_samples, sampling_period)
        # Find the index of the maximum magnitude
        max_magnitude_index = np.argmax(magnitude_freq_components)
        # Find the corresponding frequency
        max_frequency = frequency_components[max_magnitude_index]

        return max_frequency
    

    def Inverse_Fourier_Transform(self, Magnitude_frequency_components):
        """
        Applies inverse Fourier transform to transform the signal back to the time domain.

        Parameters:
        - Magnitude_frequency_components: Magnitude of the frequency components.

        Returns:
        - Time domain signal.
        """
        
        Amplitude_time_domain = irfft(Magnitude_frequency_components).real #Transform the signal back to the time domain.

        return Amplitude_time_domain 
    

    def get_max_amplitude(self, audio_data):
        """
        Gets the maximum amplitude of an audio signal.

        Parameters:
        - audio_data: Numpy array representing the audio signal.

        Returns:
        - Max amplitude value.
        """
        max_amplitude = np.max(np.abs(audio_data))

        return max_amplitude


    # Define window functions
    def rectangular_window(self, window_size):
        """
        Rectangular window function.

        Parameters:
        - window_size: Size of the window.

        Returns:
        - Rectangular window.
        """
        return np.ones(window_size)

    def hamming_window(self, window_size):
        """
        Hamming window function.

        Parameters:
        - window_size: Size of the window.

        Returns:
        - Hamming window.
        """
        return np.hamming(window_size)

    def hanning_window(self, window_size):
        """
        Hanning window function.

        Parameters:
        - window_size: Size of the window.

        Returns:
        - Hanning window.
        """
        return np.hanning(window_size)

    def gaussian_window(self, window_size, sigma=1000):
        """
        Gaussian window function.

        Parameters:
        - window_size: Size of the window.
        - sigma: Standard deviation.

        Returns:
        - Gaussian window.
        """
        return np.exp(-0.5 * ((np.arange(window_size) - (window_size - 1) / 2) / sigma) ** 2)


def main():
    """
    Method to start the application.
    """
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    app.exec_()  # infinite Loop


if __name__ == '__main__':
    main()
