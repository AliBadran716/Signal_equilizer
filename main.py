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
        self.modes_dict = {
            'Unifrom Range': [10, [self.verticalSlider_1, self.verticalSlider_2, self.verticalSlider_3, self.verticalSlider_4,
                               self.verticalSlider_5, self.verticalSlider_6, self.verticalSlider_7,
                               self.verticalSlider_8, self.verticalSlider_9, self.verticalSlider_10],
                              ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"], True],
            'Musical Instruments': [4,
                                [self.verticalSlider_1, self.verticalSlider_2, self.verticalSlider_3, self.verticalSlider_4],
                                ["Piano", "Guitar", "Violin", "Trumpet"], False],
            'Animal Sounds': [4,
                [self.verticalSlider_1, self.verticalSlider_2, self.verticalSlider_3, self.verticalSlider_4],
                ["Lion", "Monkey", "Bird", "Elephant"], False],
            'ECG Abnormalities': [4,
                [self.verticalSlider_1, self.verticalSlider_2, self.verticalSlider_3, self.verticalSlider_4],
                ["PVC", "PAC", "LBBB", "RBBB"], False]
        }
        self.sliders_labels = [self.label_1,self.label_2,self.label_3,self.label_4,self.label_5,self.label_6,self.label_7,self.label_8,self.label_9,self.label_10]
        self.previous_selection = None
        self.handel_buttons()
        #self.comboBox.setCurrentText("Unifrom Range")

            

    def handel_buttons(self):
        self.actionOpen.triggered.connect(self.add_signal)
        self.comboBox.currentIndexChanged.connect(self.handle_sliders)

    def showElements(self, elements, show=True):
        for element in elements:
            if show:
                element.show()
            else:
                element.hide()

    def handle_sliders(self, mode_name):
        selected_mode = self.comboBox.currentText()
        num_sliders = self.modes_dict[selected_mode][0]
        self.showElements(self.modes_dict['Unifrom Range'][1], False)
        self.showElements(self.sliders_labels, False)
        self.showElements(self.modes_dict[selected_mode][1])
        shown_labels = []
        for i in range(num_sliders):
            #exec(f"self.showElements(self.label_{i+1})")
            exec(f"self.label_{i+1}.setText(self.modes_dict[selected_mode][2][i])")
            exec(f"shown_labels.append(self.label_{i+1})")
        self.showElements(shown_labels)


    def add_signal(self):
        """
        Load a WAV signal file, add it to the application's data, and plot it.
        """
        try:
            options = QFileDialog().options()
            options |= QFileDialog.ReadOnly
            filepath, _ = QFileDialog.getOpenFileName(self, "Open WAV File", "", "WAV Files (.wav);;All Files ()",
                                                       options=options)
            if filepath:
                self.read_wav(filepath)
        except Exception as e:
            print(e)

    def read_wav(self, file_path):
        self.samplerate, data = wavfile.read(file_path)
        if data.ndim == 2:
            self.data = data.mean(axis=1)
        else:
            self.data = data
        self.time_a = np.arange(0, len(self.data)) / self.samplerate
        # plot the signal
        self.graphicsView.plot(self.time_a, self.data, pen='r')
        self.DFT()

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
