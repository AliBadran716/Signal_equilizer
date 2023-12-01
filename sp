def spectrogram(self, data, sampling_rate,widget):
        
        _, _, Sxx = spectrogram(data, sampling_rate)
        time_axis = np.linspace(0, len(data) / sampling_rate, num=Sxx.shape[1])

        fig = Figure()
        fig = Figure(figsize=(5,3))
        ax = fig.add_subplot(111)
        ax.imshow(10 * np.log10(Sxx), aspect='auto', cmap='viridis', extent=[time_axis[0], time_axis[-1], 0, sampling_rate / 2],origin='upper')
        ax.invert_yaxis()
        ax.axes.plot()
        canvas = FigureCanvas(fig)
        layout = QVBoxLayout()
        layout.addWidget(canvas)
        widget.setLayout(layout)