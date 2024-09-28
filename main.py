import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import spectrogram
import sys
import pandas as pd
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QPushButton, QLabel, QVBoxLayout, QWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Calculador de Frecuencias y Espectrograma")
        self.setGeometry(100, 100, 600, 400)
        
        self.layout = QVBoxLayout()
        
        self.label = QLabel("Cargar archivo CSV:")
        self.layout.addWidget(self.label)
        
        self.button = QPushButton("Abrir CSV")
        self.button.clicked.connect(self.open_file)
        self.layout.addWidget(self.button)
        
        self.result_label = QLabel("")
        self.layout.addWidget(self.result_label)
        
        self.spectrogram_button = QPushButton("Generar Espectrograma")
        self.spectrogram_button.clicked.connect(self.generate_spectrogram)
        self.layout.addWidget(self.spectrogram_button)
        
        self.container = QWidget()
        self.container.setLayout(self.layout)
        self.setCentralWidget(self.container)
        
        self.df = None
        self.freq_initial = None
        self.freq_final = None
        self.sampling_rate = None
    
    def open_file(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self, "Abrir Archivo CSV", "", "CSV Files (*.csv);;All Files (*)", options=options)
        if fileName:
            self.load_csv(fileName)
    
    def load_csv(self, filename):
        try:
            self.df = pd.read_csv(filename, encoding='utf-8-sig', delimiter=',', on_bad_lines='skip')
            self.label.setText(f"Archivo cargado: {filename}")
            print(f"Archivo cargado: {filename}")
            print("Columnas disponibles en el archivo CSV:")
            print(self.df.columns)
            self.calculate_frequencies()
        except Exception as e:
            self.label.setText(f"Error al cargar el archivo: {e}")
            print(f"Error al cargar el archivo: {e}")
    
    def calculate_frequencies(self):
        try:
            # Suponiendo que las frecuencias están en la columna 'Sweep (T1)'
            if 'Sweep (T1)' in self.df.columns:
                frequencies = pd.to_numeric(self.df['Sweep (T1)'], errors='coerce').dropna().sort_values()
                self.freq_initial = frequencies.iloc[0]
                self.freq_final = frequencies.iloc[-1]
                self.sampling_rate = (self.freq_final - self.freq_initial) / (len(frequencies) - 1)
                
                result_text = (f"Frecuencia Inicial: {self.freq_initial} Hz\n"
                               f"Frecuencia Final: {self.freq_final} Hz\n"
                               f"Frecuencia de Muestreo: {self.sampling_rate} Hz")
                self.result_label.setText(result_text)
                print(result_text)
            else:
                self.result_label.setText("Columna 'Sweep (T1)' no encontrada en el archivo CSV.")
                print("Columna 'Sweep (T1)' no encontrada en el archivo CSV.")
        except Exception as e:
            self.result_label.setText(f"Error al calcular las frecuencias: {e}")
            print(f"Error al calcular las frecuencias: {e}")
    
    def generate_spectrogram(self):
        try:
            if self.freq_initial is not None and self.freq_final is not None:
                # Parámetros de la señal
                fs = float(self.sampling_rate)  # Frecuencia de muestreo calculada
                t = np.linspace(0, 2, int(fs * 2), dtype=float)  # Duración de 2 segundos
                f0 = float(self.freq_initial)  # Frecuencia inicial (Hz)
                f1 = float(self.freq_final)  # Frecuencia final (Hz)

                # Crear una señal de barrido (sweep)
                x = np.sin(2 * np.pi * (f0 + (f1 - f0) * t / max(t)) * t)

                # Calcular el espectrograma
                f, t_spec, Sxx = spectrogram(x, fs, nperseg=64)  # Ajustar nperseg

                # Graficar el espectrograma
                plt.pcolormesh(t_spec, f, 10 * np.log10(Sxx), shading='gouraud')
                plt.ylabel('Frecuencia [Hz]')
                plt.xlabel('Tiempo [s]')
                plt.title('Espectrograma de la señal')
                plt.colorbar(label='Potencia/Frecuencia (dB/Hz)')
                plt.show()
            else:
                self.result_label.setText("Las frecuencias no han sido calculadas correctamente.")
                print("Las frecuencias no han sido calculadas correctamente.")
        except Exception as e:
            self.result_label.setText(f"Error al generar el espectrograma: {e}")
            print(f"Error al generar el espectrograma: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
