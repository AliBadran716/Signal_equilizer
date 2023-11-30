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
import tempfile
import functools
import sounddevice as sd
import wave
from PyQt5.QtGui import QIcon
from pyqtgraph import ImageView
import scipy
from scipy.io import wavfile
import numpy as np
import pandas as pd
import librosa
import librosa.display      
from numpy.fft import fft, ifft, rfft, rfftfreq, irfft, fftfreq
import scipy.io.wavfile as wav 
from scipy.signal import spectrogram
from pyqtgraph import GraphicsLayoutWidget
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

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
        self.speed_list = ['x0.5', 'x1', 'x1.5','x1.75', 'x2']
        self.proccessed_freqs = None
        self.proccessed_amps = None
        self.proccessed_signal = None
        self.signal_added = False
        self.zoom_counter = 0
        # Initialize a QMediaPlayer instance
        self.media_player = QMediaPlayer()
        self.handel_buttons()
        from m2 import MainApp as m2
        self.m2 = m2()

    def handel_buttons(self):
        self.actionOpen.triggered.connect(self.add_signal)
        self.comboBox.currentIndexChanged.connect(self.handle_sliders)
        self.signal_choosen.currentIndexChanged.connect(self.clear_media_player)
        self.speed_selection.currentIndexChanged.connect(self.change_speed)
        self.play_pause_btn.clicked.connect(self.toggle_playback)
        # Connect the stateChanged signal to the update_icon method
        self.media_player.stateChanged.connect(self.update_icon)
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
    def spectrogram(self, data, sampling_rate,widget):
        _, _, Sxx = spectrogram(data, sampling_rate)
        fig = Figure()
        ax = fig.add_subplot(111)
        ax.imshow(10 * np.log10(Sxx), aspect='auto', cmap='viridis')
        ax.invert_yaxis()
        ax.axes.plot()
        canvas = FigureCanvas(fig)
        layout = QVBoxLayout()
        layout.addWidget(canvas)
        widget.setLayout(layout)

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
       

    def add_signal(self):
        """
        Load a WAV signal file, add it to the application's data, and plot it.
        """

        options = QFileDialog().options()
        options |= QFileDialog.ReadOnly
        self.filepath, _ = QFileDialog.getOpenFileName(self, "Open WAV File", "", "WAV Files (*.wav);;All Files ()",
                                                  options=options)
        if self.filepath:
            self.clear_graphs()
            self.load_audio_file(self.filepath)
            self.signal_added = True

       
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
            sampling_rate , audio_samples= scipy.io.wavfile.read(path_file_upload)
            self.data = audio_samples
            self.sampling_rate = sampling_rate
             # plot the signal
            self.time_a = np.arange(0, len(self.data)) / self.sampling_rate
            self.graphicsView.plot(self.time_a, self.data, pen='r')
            self.graphicsView.setTitle('Time Domain')
            self.spectrogram(self.data, self.sampling_rate,self.widget)
            xf, _, _ = self.DFT()
            # divide xf into 10 equal frequency ranges and store it in frequencey range of self.modes_dict of uniform ranges
            if len(xf) > 10:
                n = len(xf) // 10
                for i in range(10):
                    self.modes_dict['Unifrom Range'][4].append([xf[i * n], xf[(i + 1) * n]])
            

    def proccess_signal(self, slider):
        if self.signal_added:
            self.graphicsView_2.clear()
            selected_window = self.window_combo_box.currentText()
            freq, amps, transformed = self.DFT()
            scale_factor = slider.value() / 50
            
            self.proccessed_freqs, self.proccessed_amps, self.proccessed_signal, window_title = self.m2.apply_window_to_frequency_range(
                freq, amps, transformed, 1, 1000, scale_factor, selected_window, self.sampling_rate )
            
            self.graphicsView_2.plot(self.proccessed_freqs, abs(self.proccessed_amps), pen='r')
            # Construct the complex spectrum
            self.graphicsView_3.plot(self.time_a ,self.proccessed_signal, pen='r')
            self.spectrogram(self.proccessed_signal, self.sampling_rate ,self.widget_2)


    def slider_changed(self, slider, slider_index):
        if self.signal_added:
            self.graphicsView_2.clear()
            selected_mode = self.comboBox.currentText()
            start_freq = self.modes_dict[selected_mode][4][slider_index][0]
            end_freq = self.modes_dict[selected_mode][4][slider_index][1]
            selected_window = self.window_combo_box.currentText()
            freq, amps, transformed = self.DFT()
            scale_factor = slider.value() / 50

            self.proccessed_freqs, self.proccessed_amps, self.proccessed_signal, window_title = self.m2.apply_window_to_frequency_range(
                freq, amps,transformed, start_freq, end_freq, scale_factor, selected_window, self.sampling_rate)
            
            self.graphicsView_2.plot(self.proccessed_freqs, self.proccessed_amps, pen='r')
            # Construct the complex spectrum      
            self.graphicsView_3.plot(self.time_a,self.proccessed_signal, pen='r')
            self.spectrogram(self.proccessed_signal, self.sampling_rate,self.widget_2)
            

    def DFT(self):
        transformed, xf = self.m2.Fourier_Transform_Signal(self.data, self.sampling_rate)
        self.graphicsView_2.plot(xf,abs(transformed), pen='r')
        return xf, abs(transformed), transformed

    def create_temp_wav_file(self):
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        temp_file.close()
        wav_file_path = temp_file.name
        # Normalize the audio data
        normalized_data = self.proccessed_signal
        # Write the normalized audio data to the temporary WAV file
        with wave.open(wav_file_path, 'w') as wav_file:
            wav_file.setnchannels(1)  # Mono audio
            wav_file.setsampwidth(2)  # 16-bit audio
            wav_file.setframerate(44100)  # Sample rate
            wav_file.writeframes(normalized_data.tobytes())
        return wav_file_path

    
    def toggle_playback(self):
        if self.signal_added:
            if self.media_player.mediaStatus() == QMediaPlayer.NoMedia:
                # Set media content if not already set
                signal_choosen = self.signal_choosen.currentText()
                if signal_choosen == 'Original Signal':
                    self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(self.filepath)))
                else:
                    self.temp_wav_file = self.create_temp_wav_file()
                    self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(self.temp_wav_file)))
            if self.media_player.state() == QMediaPlayer.PlayingState:
                self.media_player.pause()
            else:
                self.media_player.play()
        else:
            self.add_signal()


    def rewind_signal(self):
        if self.signal_added:
            self.media_player.setPosition(0)
            self.media_player.play()

       
    def clear_media_player(self):
        self.media_player.stop()  # Stop playback if currently playing
        self.media_player.setMedia(QMediaContent())  # Clear media content

  
    def update_icon(self, state):
        if state == QMediaPlayer.PlayingState:
            icon_path = os.path.join("imgs", "pause.png")
        elif state == QMediaPlayer.PausedState:
            icon_path = os.path.join("imgs", "play.png")
        elif state == QMediaPlayer.StoppedState:
            icon_path = os.path.join("imgs", "play.png")
            # You may want to seek back to the beginning for replay
            self.media_player.setPosition(0)
        # Change the button icon
        self.play_pause_btn.setIcon(QIcon(icon_path))


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

    # A function used to zoom in the graph
    def zoom_in(self):
        if self.zoom_counter < 5:  # Set your desired limit
            self.zoom(self.graphicsView, 1.3)
            self.zoom(self.graphicsView_2, 1.3)
            self.zoom_counter += 1

    # A function used to zoom out from the graph
    def zoom_out(self):
        if self.zoom_counter > -3:
            self.zoom(self.graphicsView, 0.5)
            self.zoom(self.graphicsView_2, 0.5)
            self.zoom_counter -= 1

    
    def change_speed(self):
        speed = self.speed_selection.currentText()
        if speed == 'x0.5':
            self.media_player.setPlaybackRate(0.5)
        elif speed == 'x1':
            self.media_player.setPlaybackRate(1)
        elif speed == 'x1.5':
            self.media_player.setPlaybackRate(1.5)
        elif speed == 'x1.75':
            self.media_player.setPlaybackRate(1.75)
        elif speed == 'x2':
            self.media_player.setPlaybackRate(2)

def main():  # method to start app
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    app.exec_()  # infinite Loop


if __name__ == '__main__':
    main()
