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

from numpy.fft import fft
from pyqtgraph import ImageView
from scipy.io import wavfile

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
        self.modes_list = {
            'Unifrom Range': [[self.verticalSlider_1, self.verticalSlider_2, self.verticalSlider_3, self.verticalSlider_4,
                               self.verticalSlider_5, self.verticalSlider_6, self.verticalSlider_7,
                               self.verticalSlider_8, self.verticalSlider_9, self.verticalSlider_10],
                              [self.label_1, self.label_2, self.label_3, self.label_4, self.label_5, self.label_6,
                               self.label_7, self.label_8, self.label_9, self.label_10
                               ],
                              ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"], True],
            'Musical Instruments': [
                                [self.verticalSlider_1, self.verticalSlider_2, self.verticalSlider_3, self.verticalSlider_4],
                                [self.label_1, self.label_2, self.label_3, self.label_4],
                                ["Piano", "Guitar", "Violin", "Trumpet"], False],
            'Animal Sounds': [
                [self.verticalSlider_1, self.verticalSlider_2, self.verticalSlider_3, self.verticalSlider_4],
                [self.label_1, self.label_2, self.label_3, self.label_4],
                ["Lion", "Monkey", "Bird", "Elephant"], False],
            'ECG Abnormalities': [
                [self.verticalSlider_1, self.verticalSlider_2, self.verticalSlider_3, self.verticalSlider_4],
                [self.label_1, self.label_2, self.label_3, self.label_4],
                ["PVC", "PAC", "LBBB", "RBBB"], False]
        }
        self.sliders_labels = []
        self.uniform_flag = True
        self.musical_flag = False
        self.animal_flag = False
        self.ecg_flag = False
        self.previous_selection = None
        self.handel_buttons()
        self.comboBox.setCurrentText("Unifrom Range")

    def select_mode(self):
        selected_mode = self.modes_comboBox.currentText()
        if selected_mode == 'Unifrom Range':
            self.unifrom_flag = True
            self.musical_flag = False
            self.animal_flag = False
            self.ecg_flag = False
            self.num_sliders = 10
        elif selected_mode == 'Musical Instruments':
            self.musical_flag = True
            self.unifrom_flag = False
            self.animal_flag = False
            self.ecg_flag = False
            self.num_sliders = 4
        elif selected_mode == 'Animal Sounds':
            self.animal_flag = True
            self.musical_flag = False
            self.unifrom_flag = False
            self.ecg_flag = False
            self.num_sliders = 4
        elif selected_mode == 'ECG Abnormalities':
            self.ecg_flag = True
            self.musical_flag = False
            self.animal_flag = False
            self.unifrom_flag = False
            self.num_sliders = 4

    def handel_buttons(self):
        self.comboBox.currentIndexChanged.connect(self.handle_combobox)

    def showElements(self, elements, show=True):
        for element in elements:
            if show:
                element.show()
            else:
                element.hide()

    def handle_combobox(self):
        selected_mode = self.comboBox.currentText()
        if selected_mode == "Musical Instruments":
            self.showElements(
                [self.verticalSlider_5, self.verticalSlider_6, self.verticalSlider_7, self.verticalSlider_8,
                 self.verticalSlider_9, self.verticalSlider_10
                    , self.label_5, self.label_6, self.label_7, self.label_8, self.label_9, self.label_10], False)

            self.showElements(
                [self.verticalSlider_1, self.verticalSlider_2, self.verticalSlider_3, self.verticalSlider_4, self.label_1,
                 self.label_2, self.label_3, self.label_4])
            self.label_1.setText("Piano")
            self.label_2.setText("Guitar")
            self.label_3.setText("Violin")
            self.label_4.setText("Trumpet")
        elif selected_mode == "Animal Sounds":
            self.showElements(
                [self.verticalSlider_5, self.verticalSlider_6, self.verticalSlider_7, self.verticalSlider_8,
                 self.verticalSlider_9, self.verticalSlider_10,
                 self.label_5, self.label_6, self.label_7, self.label_8, self.label_9, self.label_10], False)
            self.showElements(
                [self.verticalSlider_1, self.verticalSlider_2, self.verticalSlider_3, self.verticalSlider_4, self.label_1,
                 self.label_2, self.label_3, self.label_4])
            self.label_1.setText("Lion")
            self.label_2.setText("Monkey")
            self.label_3.setText("Bird")
            self.label_4.setText("Elephant")
        elif selected_mode == "ECG Abnormalities":
            self.showElements(
                [self.verticalSlider_5, self.verticalSlider_6, self.verticalSlider_7, self.verticalSlider_8,
                 self.verticalSlider_9, self.verticalSlider_10, self.label_5, self.label_6, self.label_7, self.label_8,
                 self.label_9, self.label_10], False)

            self.showElements(
                [self.verticalSlider_1, self.verticalSlider_2, self.verticalSlider_3, self.verticalSlider_4, self.label_1,
                 self.label_2, self.label_3, self.label_4])
            self.label_1.setText("PVC")
            self.label_2.setText("PAC")
            self.label_3.setText("LBBB")
            self.label_4.setText("RBBB")
        elif selected_mode == "Unifrom Range":
            self.showElements([self.verticalSlider_1, self.verticalSlider_2, self.verticalSlider_3, self.verticalSlider_4,
                               self.verticalSlider_5, self.verticalSlider_6, self.verticalSlider_7,
                               self.verticalSlider_8, self.verticalSlider_9, self.verticalSlider_10, self.label_1,
                               self.label_2, self.label_3, self.label_4, self.label_5, self.label_6, self.label_7,
                               self.label_8, self.label_9, self.label_10
                               ])
            self.label_1.setText("1")
            self.label_2.setText("2")
            self.label_3.setText("3")
            self.label_4.setText("4")
            self.label_5.setText("5")
            self.label_6.setText("6")
            self.label_7.setText("7")
            self.label_8.setText("8")
            self.label_9.setText("9")
            self.label_10.setText("10")

    def read_wav(self):
        self.samplerate, data = wavfile.read('eleph.wav')
        if data.ndim == 2:
            self.data = data.mean(axis=1)
        else:
            self.data = data
        self.time_a = np.arange(0, len(self.data)) / self.samplerate
        imageView = ImageView()

    # Compute spectrogram and set image
    #

    # colors = [(0, 0, 255, 255), (255, 255, 255, 255), (255, 0, 0, 255)]
    # img = pg.ImageItem(image = Sxx , lut = colors)
    # self.graphicsView_3.addItem(img)
    # self.graphicsView.plot(self.time_a,self.data, pen='r')
    # Compute the spectrogram for the audio

    def DFT(self):
        transformed = fft(self.data)
        N = len(self.data)
        xf = np.linspace(0.0, 0.5 * self.samplerate, N // 2)

        self.graphicsView_2.plot(xf, 2.0 / N * np.abs(transformed[:N // 2]), pen='r')


def main():  # method to start app
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    app.exec_()  # infinite Loop


if __name__ == '__main__':
    main()
