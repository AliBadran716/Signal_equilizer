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
from PyQt5.QtWidgets import QFileDialog
import pandas as pd
import os
from scipy.io.wavfile import write
import wfdb
import array
import csv

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
        self.ecg_arr = {
            
            'Atrial Trachycardia': 100,
            'Atrial Flutter': 178,
            'Atrial Fibrillation': 100,
            'Normal': 100,
        }
        self.modes_dict = {
            'Unifrom Range': [10, [self.verticalSlider_1, self.verticalSlider_2, self.verticalSlider_3,
                                   self.verticalSlider_4,
                                   self.verticalSlider_5, self.verticalSlider_6, self.verticalSlider_7,
                                   self.verticalSlider_8, self.verticalSlider_9, self.verticalSlider_10],
                              ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"], True,
                              []
                              ],
            'Musical Instruments': [4,
                                    [self.verticalSlider_1, self.verticalSlider_2, self.verticalSlider_3,
                                     self.verticalSlider_4],
                                    ["Violin", "Trumpet", "Xylo", "Triangle"], False,
                                    # frequency ranges
                                    [[0, 1000], [1000, 2000], [2000, 3000], [4000, 5000]]
                                    ],
            'Animal Sounds': [4,
                              [self.verticalSlider_1, self.verticalSlider_2, self.verticalSlider_3,
                               self.verticalSlider_4],
                              ["Cow", "Whale", "Cat", "Cricket"], False,
                              #  frequency ranges
                              [[0, 620], [650, 900], [750, 4500], [3800, 22000]]
                              ],
            'ECG Abnormalities': [4,
                                  [self.verticalSlider_1, self.verticalSlider_2, self.verticalSlider_3,
                                   self.verticalSlider_4],
                                  ["Normal", "Atrial Fibrillation" , "Atrial Flutter", "Ventricular fibrillation"], False,
                                  #  frequency ranges
                                  [[0, 3], [15, 20], [2, 8], [0,5]]
                                  ],
        }
        self.sliders_labels = [self.label_1, self.label_2, self.label_3, self.label_4, self.label_5, self.label_6,
                               self.label_7, self.label_8, self.label_9, self.label_10]
        self.signal_freqs = None
        self.signal_amps = None
        self.transformed_signal = None
        self.original_signal = None
        self.sampling_rate = None
        self.processed_time_signal = None
        self.signal_added = False
        self.zoom_counter = 0
        self.end_indx = 0
        # Initialize a QMediaPlayer instance
        self.media_player = QMediaPlayer()
        self.handel_buttons()
        from m2 import MainApp as m2
        self.m2 = m2()
        self.graphicsView.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.graphicsView.setMinimumSize(200, 200)
        self.graphicsView_2.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.graphicsView_2.setMinimumSize(200, 200)
        self.graphicsView_3.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.graphicsView_3.setMinimumSize(200, 200)

    def handel_buttons(self):
        self.actionOpen.triggered.connect(self.add_signal)
        self.comboBox.currentIndexChanged.connect(self.handle_sliders)
        self.signal_choosen.currentIndexChanged.connect(self.clear_media_player)
        self.speed_selection.currentIndexChanged.connect(self.change_speed)
        self.play_pause_btn.clicked.connect(self.toggle_playback)
        # Connect the stateChanged signal to the update_plot method
        self.media_player.stateChanged.connect(self.update_plot)
        # Connect the stateChanged signal to the update_icon method
        self.media_player.stateChanged.connect(self.update_icon)
        self.zoom_out_push_btn.clicked.connect(self.zoom_out)
        self.zoom_in_push_btn.clicked.connect(self.zoom_in)
        self.rewind_push_btn.clicked.connect(self.rewind_signal)
        slider = self.verticalSlider_1
        self.window_combo_box.currentIndexChanged.connect(functools.partial(self.slider_changed, slider))
        for i in range(10):
            slider = getattr(self, f"verticalSlider_{i + 1}")
            slider.valueChanged.connect(functools.partial(self.slider_changed, slider))
    def showElements(self, elements, show=True):
        for element in elements:
            if show:
                element.show()
            else:
                element.hide()
    def spectrogram(self, data, sampling_rate,widget):
        if widget.layout() is not None:
            widget.layout().deleteLater()
        _, _, Sxx = spectrogram(data, sampling_rate)
        time_axis = np.linspace(0, len(data) / sampling_rate, num=Sxx.shape[1])
        fig = Figure()
        fig = Figure(figsize=(3,3))
        ax = fig.add_subplot(111)
        ax.imshow(10 * np.log10(Sxx), aspect='auto', cmap='viridis',extent=[time_axis[0], time_axis[-1], 0, sampling_rate / 2])
        # ax = np.rot90(ax, k=1)
        # ax.invert_yaxis()
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
        Load a WAV or CSV and if its csv convert it into wav signal file, add it to the application's data, and plot it.
        """
        options = QFileDialog().options()
        options |= QFileDialog.ReadOnly
        self.filepath, _ = QFileDialog.getOpenFileName(self, "Open WAV or CSV File", "", "WAV Files (*.wav);;CSV Files (*.csv);;All Files ()",
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
            if path_file_upload.endswith('.csv'):
                self.mode = 'ECG'   
                self.graphicsView.setTitle('ECG Signal')
                signal_data = pd.read_csv(path_file_upload) 
                time_a = np.arange(0, len(signal_data)) / 1000
                # signal transpose
                self.original_signal = signal_data.iloc[:,0]
                # print(self.original_signal)
                self.processed_time_signal = signal_data.iloc[:, 0]
                self.sampling_rate = 1000
                self.time_a = time_a
                self.time_a_processed= time_a
                self.graphicsView.plot(self.time_a, self.original_signal, pen='r')
                self.graphicsView.setTitle('Time Domain')
                self.spectrogram(self.original_signal, self.sampling_rate,self.widget)
                self.signal_freqs, self.signal_amps, self.transformed_signal = self.DFT()
                self.graphicsView_3.plot(self.time_a, self.original_signal, pen='r')
                self.spectrogram(self.original_signal, self.sampling_rate, self.widget_2)
                # divide xf into 10 equal frequency ranges and store it in frequencey range of self.modes_dict of uniform ranges
                if len(self.signal_freqs) > 10:
                    n = len(self.signal_freqs) // 10
                    for i in range(10):
                        self.modes_dict['Unifrom Range'][4].append([self.signal_freqs[i * n], self.signal_freqs[min((i + 1) * n, len(self.signal_freqs) - 1)]])
            if path_file_upload.endswith('.hea'):
                self.mode = 'ECG'
                self.graphicsView.setTitle('ECG Signal')  
                record = wfdb.rdrecord(self.filepath[:-4])
                ecg_data = record.p_signal
                ecg_df = pd.DataFrame(data=ecg_data[:6000], columns=[f'Channel_{i+1}' for i in range(ecg_data.shape[1])])
                time_a = np.arange(0, len(ecg_df)) / record.fs
                sampling_rate = record.fs
                
                self.original_signal = ecg_df.iloc[:, 0]
                self.processed_time_signal = ecg_df.iloc[:, 0]
                self.sampling_rate = sampling_rate
                # if (len(self.original_signal.shape) > 1):
                #     self.original_signal = self.original_signal[:,0]
                self.time_a = time_a
                self.time_a_processed= time_a
                
                self.graphicsView.plot(self.time_a, self.original_signal, pen='r')
                self.graphicsView.setTitle('Time Domain')
                self.spectrogram(self.original_signal, self.sampling_rate,self.widget)
                
                # self.signal_freqs, self.signal_amps, self.transformed_signal = self.DFT()
               
                self.signal_freqs, self.signal_amps, self.transformed_signal = self.DFT()
                self.graphicsView_3.plot(self.time_a, self.original_signal, pen='r')
                self.spectrogram(self.original_signal, self.sampling_rate, self.widget_2)
                # divide xf into 10 equal frequency ranges and store it in frequencey range of self.modes_dict of uniform ranges
                if len(self.signal_freqs) > 10:
                    n = len(self.signal_freqs) // 10
                    for i in range(10):
                        self.modes_dict['Unifrom Range'][4].append([self.signal_freqs[i * n], self.signal_freqs[min((i + 1) * n, len(self.signal_freqs) - 1)]])
            
            if path_file_upload.endswith('.wav'):
                self.mode = 'Audio'
                sampling_rate , audio_samples= scipy.io.wavfile.read(path_file_upload)
                self.original_signal = audio_samples
                self.processed_time_signal = audio_samples
                self.sampling_rate = sampling_rate
                if (len(self.original_signal.shape) > 1):
                    self.original_signal = self.original_signal[:,0]
                self.time_a = np.arange(0, len(self.original_signal)) / self.sampling_rate
                self.time_a_processed= np.arange(0, len(self.processed_time_signal)) / self.sampling_rate
                self.graphicsView.plot(self.time_a, self.original_signal, pen='r')
                self.graphicsView.setTitle('Time Domain')
                self.spectrogram(self.original_signal, self.sampling_rate,self.widget)
                
                self.signal_freqs, self.signal_amps, self.transformed_signal = self.DFT()
                
                self.graphicsView_3.plot(self.time_a, self.original_signal, pen='r')
                self.spectrogram(self.original_signal, self.sampling_rate, self.widget_2)
                # divide xf into 10 equal frequency ranges and store it in frequencey range of self.modes_dict of uniform ranges
                if len(self.signal_freqs) > 10:
                    n = len(self.signal_freqs) // 10
                    for i in range(10):
                        self.modes_dict['Unifrom Range'][4].append([self.signal_freqs[i * n], self.signal_freqs[min((i + 1) * n, len(self.signal_freqs) - 1)]])

                # Set the x-axis range to 0 to 0.04 if the file is an ECG file
                if 'ECG_Arr.wav' in path_file_upload:
                    self.graphicsView.getViewBox().setXRange(0, 0.04)
                    self.graphicsView_3.getViewBox().setXRange(0, 0.04)


    def dynamic_plot(self, signal,time, graphicsView):
        self.timer_1 = QTimer()
        self.timer_1.setInterval(45)
        self.timer_1.timeout.connect(functools.partial(self.update_plot_data_1, signal, time,graphicsView))
        self.timer_1.start()


    def update_plot_data_1(self,signal,time, graphicsView):
        if self.signal_added:
            # chunk_size = len(self.original_signal) // 100  # Adjust the chunk size as needed
            chunk_size = int((len(signal) * 50 * 10 ** -3) / self.time_a[-1])
            start_indx = self.end_indx
            end_indx = min(start_indx + chunk_size, len(signal))
            graphicsView.plot(time[start_indx:end_indx],signal[start_indx:end_indx], pen='b')
            self.end_indx = end_indx
            if self.end_indx >= len(signal):
                self.end_indx = len(signal)
                self.timer_1.stop()
                graphicsView.clear()
                graphicsView.plot(time, signal, pen='r')

    def update_plot(self, state):
        signal_choosen = self.signal_choosen.currentText()
        if signal_choosen == 'Original Signal':
            signal = self.original_signal
            time = self.time_a
            graphicsView = self.graphicsView
        else:
            signal = self.processed_time_signal
            time = self.time_a_processed
            graphicsView = self.graphicsView_3

        if state == QMediaPlayer.PlayingState:
            self.dynamic_plot(signal, time, graphicsView)

        elif state == QMediaPlayer.PausedState:
            self.timer_1.stop()
        elif state == QMediaPlayer.StoppedState:
            graphicsView.clear()
            graphicsView.plot(time, signal, pen='r')
            self.timer_1.stop()
            self.end_indx = 0

    def slider_changed(self, slider):
        if self.signal_added:
            selected_mode = self.comboBox.currentText()
            num_sliders = self.modes_dict[selected_mode][0]
            
            sliders_values = self.get_sliders_values(num_sliders)
            #sliders_scale_factors = sliders_values // 50
            processed_freqs, processed_amps, processed_signal = self.DFT()
            
            self.graphicsView_2.clear()
            for i in range(num_sliders):
                start_freq = self.modes_dict[selected_mode][4][i][0]
                end_freq = self.modes_dict[selected_mode][4][i][1]
                # ecg_arr = self.ecg_arr[self.modes_dict[selected_mode][2][i]]
                selected_window = self.window_combo_box.currentText()
                print (sliders_values[i]    )
                if selected_mode == 'ECG Abnormalities':
                    if sliders_values[i]<24 and i < 3:
                        sliders_values[i]=24
                    if sliders_values[3] < 6:
                        sliders_values[3] = 6
                        
                scale_factor = sliders_values[i] / 50

                processed_freqs, processed_amps, processed_signal, window = self.m2.apply_window_to_frequency_range(
                processed_freqs, processed_amps, processed_signal, start_freq, end_freq, scale_factor, selected_window, self.sampling_rate )

                # Find indices corresponding to start and end frequencies
                start_index = np.where(processed_freqs >= start_freq)[0][0]
                end_index = np.where(processed_freqs <= end_freq)[0][-1]
                max_amp = self.m2.get_max_amplitude(processed_amps[start_index:end_index+1])
                # print(max_amp)
                # Plot the windowed signal on graphicsView_2
                self.graphicsView_2.plot(processed_freqs[start_index:end_index+1], window * max_amp, pen='b')

            # Construct the complex spectrum
            if self.mode == 'ECG':
                self.processed_time_signal = self.m2.Inverse_Fourier_Transform(processed_signal)
                
                # output_file = "vf.csv"

                # # Open the CSV file for writing
                # with open(output_file, 'w') as csvfile:
                #     # Create a writer object from csv module
                #     csvwriter = csv.writer(csvfile)
                #     # Write the header in the CSV file
                #     csvwriter.writerow([ 'Amplitude'])
                #     # Loop through the time and amplitude arrays and write each row in the CSV file
                #     for i in range(len(self.processed_time_signal)):
                #         csvwriter.writerow([self.processed_time_signal[i]])
                 
            else:
                self.processed_time_signal = np.int16(self.m2.Inverse_Fourier_Transform(processed_signal))
            # make len of self.time_a equal to len of self.processed_time_signal
            self.time_a_processed = np.arange(0, len(self.processed_time_signal)) / self.sampling_rate
            self.clear_media_player()
            self.graphicsView_2.plot(processed_freqs, processed_amps, pen='r')
            self.spectrogram(self.processed_time_signal, self.sampling_rate, self.widget_2)

 
    def get_sliders_values(self, num_sliders):
        sliders_values = []
        for i in range(num_sliders):
            slider = getattr(self, f"verticalSlider_{i + 1}")
            sliders_values.append(slider.value())
        return sliders_values

    def DFT(self):
        transformed, xf = self.m2.Fourier_Transform_Signal(self.original_signal, self.sampling_rate)
        self.graphicsView_2.plot(xf,abs(transformed), pen='r')
        
        return xf, abs(transformed), transformed

    def create_temp_wav_file(self):
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        temp_file.close()
        wav_file_path = temp_file.name
        with wave.open(wav_file_path, 'w') as wav_file:
            wav_file.setnchannels(1)  # Mono audio
            wav_file.setsampwidth(2)  # 16-bit audio
            wav_file.setframerate(44100)  # Sample rate
            wav_file.writeframes(self.processed_time_signal.tobytes())
        return wav_file_path

    
    def toggle_playback(self):
        if self.signal_added:

            signal_choosen = self.signal_choosen.currentText()
            if signal_choosen == 'Original Signal':
                signal = self.original_signal
                time = self.time_a
                graphicsView = self.graphicsView

            else:
                signal = self.processed_time_signal
                time= self.time_a_processed
                graphicsView = self.graphicsView_3
            self.dynamic_plot(signal, time, graphicsView)

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
            self.end_indx = 0
            signal_choosen = self.signal_choosen.currentText()
            if signal_choosen == 'Original Signal':
                signal = self.original_signal
                time = self.time_a
                graphicsView = self.graphicsView
            else:
                signal = self.processed_time_signal
                time = self.time_a_processed
                graphicsView = self.graphicsView_3
            self.dynamic_plot(signal, time, graphicsView)
            graphicsView.clear()
            graphicsView.plot(time, signal, pen='r')

       
    def clear_media_player(self):
        self.media_player.stop()  # Stop playback if currently playing
        self.media_player.setMedia(QMediaContent())  # Clear media content
        self.graphicsView.clear()
        self.graphicsView_3.clear()
        self.end_indx = 0
        self.graphicsView.plot(self.time_a, self.original_signal, pen='r')
        self.graphicsView_3.plot(self.time_a_processed,self.processed_time_signal,pen='r')


  
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
        # Calculate the new visible x and y ranges (zoom)
        new_x_min = x_min * zoom_factor
        new_x_max = x_max * zoom_factor
        # Set the new visible x and y ranges
        graphicsView.getViewBox().setRange(xRange=[new_x_min, new_x_max])

    # A function used to zoom in the graph
    def zoom_in(self):
        if self.zoom_counter < 5:  # Set your desired limit
            self.zoom(self.graphicsView, 1.3)
            self.zoom(self.graphicsView_3, 1.3)
            self.zoom_counter += 1

    # A function used to zoom out from the graph
    def zoom_out(self):
        if self.zoom_counter > -3:
            self.zoom(self.graphicsView, 0.5)
            self.zoom(self.graphicsView_3, 0.5)
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

    def getindex(self, freq_Hz):
        f_max = self.m2.Get_Max_Frequency(self.original_signal, self.sampling_rate)
        signal = self.original_signal
        return freq_Hz / f_max * len(signal)


def main():  # method to start app
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    app.exec_()  # infinite Loop


if __name__ == '__main__':
    main()
