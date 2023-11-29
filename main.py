from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.uic import loadUiType
from PyQt5.QtWidgets import QApplication, QFileDialog
from PyQt5.QtCore import Qt, QUrl, QTemporaryFile
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
import pandas as pd
import pyqtgraph as pg
import sys
import numpy as np
import os
from os import path
import threading
import functools
import pyaudio
import sounddevice as sd
import wave
from PyQt5.QtGui import QIcon
from numpy.fft import fft, ifft
from pyqtgraph import ImageView
import scipy
from scipy.io import wavfile
#Import necessary libraries
#import  streamlit_vertical_slider  as svs
#from Signal_Generation_class import Signal
import numpy as np
import pandas as pd
import librosa
import librosa.display      
from numpy.fft import fft,rfft,rfftfreq,irfft,fftfreq
#import plotly.graph_objects as go
#import streamlit as st
#import soundfile as soundf
#import matplotlib.pyplot as plt
import time
#import altair as alt
#import plotly.graph_objs as go
#from plotly.offline import iplot
import scipy.io.wavfile as wav 

# Load the UI file and connect it with the Python file
FORM_CLASS, _ = loadUiType(path.join(path.dirname(__file__), "main.ui"))


class MainApp(QMainWindow, FORM_CLASS):
    def __init__(self, parent=None):
        """
        Constructor to initiate the main window in the design.

        Parameters:
        - parent: The parent widget, which is typically None for the main window.
        """
        super(MainApp, self).__init__(parent)
        self.setupUi(self)
        self.modes_dict = {
            'Unifrom Range': [10, [self.verticalSlider_1, self.verticalSlider_2, self.verticalSlider_3,
                                   self.verticalSlider_4,
                                   self.verticalSlider_5, self.verticalSlider_6, self.verticalSlider_7,
                                   self.verticalSlider_8, self.verticalSlider_9, self.verticalSlider_10],
                              ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"], True,
                              []],
            'Musical Instruments': [4,
                                    [self.verticalSlider_1, self.verticalSlider_2, self.verticalSlider_3,
                                     self.verticalSlider_4],
                                    ["Piano", "Guitar", "Violin", "Trumpet"], False,
                                    # frequency ranges
                                    [[0, 1000], [1000, 2000], [2000, 3000], [3000, 4000]]],
            'Animal Sounds': [4,
                              [self.verticalSlider_1, self.verticalSlider_2, self.verticalSlider_3,
                               self.verticalSlider_4],
                              ["Lion", "Monkey", "Bird", "Elephant"], False,
                              #  frequency ranges
                              [[0, 1000], [1000, 2000], [2000, 3000], [3000, 4000]]],
            'ECG Abnormalities': [4,
                                  [self.verticalSlider_1, self.verticalSlider_2, self.verticalSlider_3,
                                   self.verticalSlider_4],
                                  ["PVC", "PAC", "LBBB", "RBBB"], False,
                                  #  frequency ranges
                                  [[0, 1000], [1000, 2000], [2000, 3000], [3000, 4000]]],
        }
        self.sliders_labels = [self.label_1, self.label_2, self.label_3, self.label_4, self.label_5, self.label_6,
                               self.label_7, self.label_8, self.label_9, self.label_10]
        self.previous_selection = None
        self.proccessed_freqs = None
        self.proccessed_amps = None
        self.proccessed_signal = None
        self.ifft_signal = None
        self.signal_added = False
        self.zoom_counter = 0
        self.playing = False
        self.paused = False
        self.stop_event = threading.Event()  # Event to signal when to stop playback
        self.p = None  # PyAudio instance
        self.stream = None
        self.playback_position = 0  # To keep track of playback position
        self.chunk_size = 400000 # Adjust this value
        self.handel_buttons()
        self.media_player = QMediaPlayer()
        from m2 import MainApp as m2
        self.m2 = m2()

    def handel_buttons(self):
        self.actionOpen.triggered.connect(self.add_signal)
        self.comboBox.currentIndexChanged.connect(self.handle_sliders)
        self.play_pause_btn.clicked.connect(self.play_pause_processed)
        self.zoom_out_push_btn.clicked.connect(self.zoom_out)
        self.zoom_in_push_btn.clicked.connect(self.zoom_in)
        self.rewind_push_btn.clicked.connect(self.rewind_signal)
        slider = self.verticalSlider_1
        self.window_combo_box.currentIndexChanged.connect(functools.partial(self.proccess_signal, slider))
        for i in range(10):
            slider = getattr(self, f"verticalSlider_{i + 1}")
            slider.valueChanged.connect(functools.partial(self.slider_changed, slider, i))

    def showElements(self, elements, show=True):
        for element in elements:
            if show:
                element.show()
            else:
                element.hide()

    def handle_sliders(self):
        selected_mode = self.comboBox.currentText()
        num_sliders = self.modes_dict[selected_mode][0]
        # reset slider positions
        for i in range(10):
            exec(f"self.verticalSlider_{i + 1}.setValue(50)")
        self.showElements(self.modes_dict['Unifrom Range'][1], False)
        self.showElements(self.sliders_labels, False)
        self.showElements(self.modes_dict[selected_mode][1])
        shown_labels = []
        for i in range(num_sliders):
            exec(f"self.label_{i + 1}.setText(self.modes_dict[selected_mode][2][i])")
            exec(f"shown_labels.append(self.label_{i + 1})")
        self.showElements(shown_labels)

    def clear_graphs(self):
        self.graphicsView.clear()
        self.graphicsView_2.clear()
        self.graphicsView_3.clear()
        self.graphicsView_4.clear()

    def add_signal(self):
        """
        Load a WAV signal file, add it to the application's data, and plot it.
        """

        options = QFileDialog().options()
        options |= QFileDialog.ReadOnly
        filepath, _ = QFileDialog.getOpenFileName(self, "Open WAV File", "", "WAV Files (*.wav);;All Files ()",
                                                  options=options)
        if filepath:
            self.clear_graphs()
            self.load_audio_file(filepath)
            self.signal_added = True
            _, _, _ = self.DFT()

       
    def load_audio_file(self, path_file_upload):
    
        """
        Function to upload audio file given file path using librosa
        
        (Librosa is a Python package for analyzing and working with audio files,
        and it can handle a variety of audio file formats, including WAV, MP3, FLAC, OGG, 
        and many more.)
        
        Parameters:
        Audio file path
        
        Output:
        Audio samples
        Sampling rate
        """
        if path_file_upload is not None:
            audio_samples,sampling_rate=librosa.load(path_file_upload)
            self.data = audio_samples
            self.samplerate = sampling_rate
             # plot the signal
            self.time_a = np.arange(0, len(self.data)) / self.samplerate
            self.graphicsView.plot(self.time_a, self.data, pen='r')
            self.graphicsView.setTitle('Time Domain')
            print('Signal added successfully')


    def proccess_signal(self, slider):
        if self.signal_added:
            self.graphicsView_2.clear()
            selected_window = self.window_combo_box.currentText()
            freq, amps, transformed = self.DFT()
            scale_factor = slider.value() / 50
            #print(self.samplerate)
            self.proccessed_freqs, self.proccessed_amps, self.proccessed_signal, window_title = self.m2.apply_window_to_frequency_range(
                freq, amps, 1, 1000, scale_factor, selected_window, self.samplerate)
            self.graphicsView_2.plot(self.proccessed_freqs, self.proccessed_amps, pen='r')
            self.graphicsView_3.plot(self.proccessed_signal.real, pen='r')
            ifft_data = np.int16(self.proccessed_signal.real)
            if ifft_data :
                print('ifft_data tmam')
                scipy.io.wavfile.write('music_trash/inversed_signal.wav', self.samplerate, ifft_data)
                audio_url = QUrl.fromLocalFile('music_trash/inversed_signal.wav')
                media_content = QMediaContent(audio_url)
                self.media_player.setMedia(media_content)



    def slider_changed(self, slider, slider_index):
        if self.signal_added:
            print('slider changed')
            self.graphicsView_2.clear()
            selected_mode = self.comboBox.currentText()
            start_freq = self.modes_dict[selected_mode][4][slider_index][0]
            end_freq = self.modes_dict[selected_mode][4][slider_index][1]
            selected_window = self.window_combo_box.currentText()
            freq, amps, transformed = self.DFT()
            scale_factor = slider.value() / 50

            self.proccessed_freqs, self.proccessed_amps, self.proccessed_signal, window_title = self.m2.apply_window_to_frequency_range(
                freq, amps, start_freq, end_freq, scale_factor, selected_window, self.samplerate)
            self.graphicsView_2.plot(self.proccessed_freqs, self.proccessed_amps, pen='r')
            self.graphicsView_3.plot(self.proccessed_signal.real, pen='r')
            ifft_data = np.int16(self.proccessed_signal.real)
            scipy.io.wavfile.write('music_trash/inversed_signal.wav', self.sampling_rate, ifft_data)
            audio_url = QUrl.fromLocalFile('music_trash/inversed_signal.wav')
            media_content = QMediaContent(audio_url)
            self.media_player.setMedia(media_content)


    def DFT(self):
        transformed, _ = self.m2.Fourier_Transform_Signal(self.data, self.samplerate)
        N = len(self.data)
        xf = np.linspace(0.0, 0.5 * self.samplerate, N // 2)
        amps = 2.0 / N * np.abs(transformed[:N // 2])
        self.graphicsView_2.plot(xf, amps, pen='r')
        # divide xf into 10 equal frequency ranges and store it in frequencey range of self.modes_dict of uniform ranges
        if len(xf) > 10:
            n = len(xf) // 10
            for i in range(10):
                self.modes_dict['Unifrom Range'][4].append([xf[i * n], xf[(i + 1) * n]])
            self.proccessed_freqs = xf
            self.proccessed_amps = amps
            self.proccessed_signal = transformed
            print('DFT tmam')
        return xf, amps, transformed

    # play and pause
    def play_pause_processed(self):
        if self.playing:
            self.playing = False
            self.paused = True
            icon_path = os.path.join("imgs", "play-button.png")
            self.play_pause_btn.setIcon(QIcon(icon_path))
            self.play()
        elif self.paused:
            self.playing = True
            self.paused = False
            icon_path = os.path.join("imgs", "OIP.png")
            self.play_pause_btn.setIcon(QIcon(icon_path))
            self.pause()
        
        
    def play(self):
        self.media_player.play()

    def pause(self):
        self.media_player.pause()

    def get_next_chunk(self, in_data, frame_count, time_info, status):
        data = self.ifft_signal[self.playback_position:self.playback_position + self.chunk_size]
        self.playback_position += self.chunk_size
        if self.playback_position >= len(self.ifft_signal):
            self.playback_position = 0
            self.stop_event.set()
        return data, pyaudio.paContinue

    # replay
    def replay(self):
        self.playback_position = 0
        self.playing = True
        self.paused = False
        icon_path = os.path.join("imgs", "OIP.png")
        self.play_pause_btn.setIcon(QIcon(icon_path))
        threading.Thread(target=self.play).start()

    # stop
    def stop(self):
        self.playback_position = 0
        self.playing = False
        self.paused = False
        icon_path = os.path.join("imgs", "OIP.png")
        self.play_pause_btn.setIcon(QIcon(icon_path))
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()



    # A function used to zoom in and out of the graph
    def zoom(self, graphicsView, zoom_factor):
        # Get the current visible x and y ranges
        x_min, x_max = graphicsView.getViewBox().viewRange()[0]
        y_min, y_max = graphicsView.getViewBox().viewRange()[1]
        # Calculate the new visible x and y ranges (zoom)
        new_x_min = x_min * zoom_factor
        new_x_max = x_max * zoom_factor
        new_y_min = y_min * zoom_factor
        new_y_max = y_max * zoom_factor
        # Set the new visible x and y ranges
        graphicsView.getViewBox().setRange(xRange=[new_x_min, new_x_max], yRange=[new_y_min, new_y_max])

    # A function used to zoom out from the graph
    def zoom_out(self):
        if self.zoom_counter > -3:
            self.zoom(self.graphicsView, 0.5)
            self.zoom(self.graphicsView_2, 0.5)
            self.zoom_counter -= 1

    # A function used to zoom in the graph
    def zoom_in(self):
        if self.zoom_counter < 5:  # Set your desired limit
            self.zoom(self.graphicsView, 1.3)
            self.zoom(self.graphicsView_2, 1.3)
            self.zoom_counter += 1

    def rewind_signal(self):
        self.playback_position = 0
        self.playing = True
        self.paused = False
        icon_path = os.path.join("imgs", "OIP.png")
        self.play_pause_btn.setIcon(QIcon(icon_path))  # Change to pause icon
        threading.Thread(target=self.play).start()


def main():  # method to start app
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    app.exec_()  # infinite Loop


if __name__ == '__main__':
    main()
