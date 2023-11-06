from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.uic import loadUiType
from PyQt5.QtWidgets import QApplication, QFileDialog
import pandas as pd
# import pyqtgraph as pg
import sys
import numpy as np
from os import path

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
        self.modes_list = ['Unifrom Range', 'Musical Instruments', 'Animal Sounds', 'ECG Abnormalities']
        self.sliders_labels = []
        self.uniform_flag = True
        self.musical_flag = False
        self.animal_flag = False
        self.ecg_flag = False


    def select_mode(self):
        selected_mode = self.modes_comboBox.currentText()
        if selected_mode == 'Unifrom Range' : 
            self.unifrom_flag = True
            self.musical_flag = False
            self.animal_flag = False
            self.ecg_flag = False
            self.num_sliders = 10
        elif selected_mode == 'Musical Instruments' : 
            self.musical_flag = True
            self.unifrom_flag = False
            self.animal_flag = False
            self.ecg_flag = False
            self.num_sliders = 4
        elif selected_mode == 'Animal Sounds' : 
            self.animal_flag = True
            self.musical_flag = False
            self.unifrom_flag = False
            self.ecg_flag = False
            self.num_sliders = 4
        elif selected_mode == 'ECG Abnormalities' :
            self.ecg_flag = True
            self.musical_flag = False
            self.animal_flag = False
            self.unifrom_flag = False
            self.num_sliders = 4



def main():  # method to start app
        app = QApplication(sys.argv)
        window = MainApp()
        window.show()
        app.exec_()  # infinite Loop

   


if __name__ == '__main__':
    main()
