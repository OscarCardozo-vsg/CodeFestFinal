import sys
import pandas as pd
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QPushButton, QLabel, QVBoxLayout, QWidget, QFrame
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Calculador de Amplitud, Potencia y Resistencia")
        self.setGeometry(100, 100, 800, 600)
        
        self.main_layout = QVBoxLayout()
        self.container = QWidget()
        self.container.setLayout(self.main_layout)
        self.setCentralWidget(self.container)
        
        # Frame para la descripción
        self.desc_frame = QFrame()
        self.main_layout.addWidget(self.desc_frame)
        self.desc_layout = QVBoxLayout(self.desc_frame)
        self.desc_label = QLabel("Simulación de la señal capturada por un satélite. Carga un archivo CSV para analizar la señal.")
        self.desc_label.setFont(QFont("Arial", 14))
        self.desc_label.setAlignment(Qt.AlignCenter)
        self.desc_layout.addWidget(self.desc_label)

        # Frame para el gráfico
        self.graph_frame = QFrame()
        self.main_layout.addWidget(self.graph_frame)
        self.graph_layout = QVBoxLayout(self.graph_frame)

        # Crear el gráfico
        self.figure, self.ax = plt.subplots(figsize=(7, 5))
        self.canvas = FigureCanvas(self.figure)
        self.graph_layout.addWidget(self.canvas)

        # Botón para cargar archivo CSV
        self.button_frame = QFrame()
        self.main_layout.addWidget(self.button_frame)
        self.button_layout = QVBoxLayout(self.button_frame)
        self.button = QPushButton("Abrir CSV")
        self.button.clicked.connect(self.open_file)
        self.button_layout.addWidget(self.button)
        
        self.result_label = QLabel("")
        self.main_layout.addWidget(self.result_label)
        
        self.df = None
    
    def open_file(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self, "Abrir Archivo CSV", "", "CSV Files (*.csv);;All Files (*)", options=options)
        if fileName:
            self.load_csv(fileName)
    
    def load_csv(self, filename):
        try:
            # Leer el archivo CSV completo con el delimitador correcto y manejar líneas problemáticas
            self.df = pd.read_csv(filename, encoding='utf-8-sig', delimiter=';', on_bad_lines='skip', header=None)
            self.result_label.setText(f"Archivo cargado: {filename}")
            print(f"Archivo cargado: {filename}")
            print("Primeras filas del archivo CSV:")
            print(self.df.head())
            self.calculate_values()
        except Exception as e:
            self.result_label.setText(f"Error al cargar el archivo: {e}")
            print(f"Error al cargar el archivo: {e}")
    
    def calculate_values(self):
        try:
            # Extraer la resistencia de la fila 'RF Input'
            rf_input_row = self.df[self.df[0].str.contains('RF Input', na=False)]
            if not rf_input_row.empty:
                resistance_str = rf_input_row.iloc[0, 1]
                resistance = float(resistance_str.split()[0])  # Asumiendo que el valor está en la primera parte de la cadena
            else:
                self.result_label.setText("Fila 'RF Input' no encontrada en el archivo CSV.")
                print("Fila 'RF Input' no encontrada en el archivo CSV.")
                return
            
            # Extraer la potencia de la fila 'marker_1_value_dbm'
            marker_1_row = self.df[self.df[0].str.contains('marker_1_value_dbm', na=False)]
            if not marker_1_row.empty:
                marker_1_value_dbm_str = marker_1_row.iloc[0, 1]
                marker_1_value_dbm = float(marker_1_value_dbm_str.split()[0])  # Asumiendo que el valor está en la primera parte de la cadena
                
                # Convertir dBm a potencia en mW
                power_mw = 10 ** (marker_1_value_dbm / 10)
                
                # Calcular la amplitud (suponiendo que la amplitud es la raíz cuadrada de la potencia)
                amplitude = power_mw ** 0.5
                
                result_text = (f"Resistencia: {resistance} Ohmios\n"
                               f"Potencia [dBm]: {marker_1_value_dbm} dBm\n"
                               f"Potencia [mW]: {power_mw} mW\n"
                               f"Amplitud: {amplitude}")
                self.result_label.setText(result_text)
                print(result_text)
                
                # Crear la gráfica
                self.plot_graph()
            else:
                self.result_label.setText("Fila 'marker_1_value_dbm' no encontrada en el archivo CSV.")
                print("Fila 'marker_1_value_dbm' no encontrada en el archivo CSV.")
        except Exception as e:
            self.result_label.setText(f"Error al calcular los valores: {e}")
            print(f"Error al calcular los valores: {e}")
    
    def plot_graph(self):
        try:
            # Suponiendo que las frecuencias y potencias están en las columnas 1 y 2 respectivamente
            frecuencias = pd.to_numeric(self.df[1], errors='coerce').dropna()
            potencias = pd.to_numeric(self.df[2], errors='coerce').dropna()
            
            # Crear la gráfica
            self.ax.clear()
            self.ax.plot(frecuencias, potencias, marker='o')
            
            # Etiquetas y título
            self.ax.set_title('Amplitud de Potencia vs Frecuencia')
            self.ax.set_xlabel('Frecuencia (Hz)')
            self.ax.set_ylabel('Potencia (dBm)')
            self.ax.grid(True)
            self.ax.axhline(0, color='grey', lw=0.5, ls='--')  # Línea en 0 dBm para referencia
            self.canvas.draw()
        except Exception as e:
            print(f"Error al crear la gráfica: {e}")

    def animate_opacity(self, widget):
        # Crear una animación de opacidad
        self.animation = QPropertyAnimation(widget, b"windowOpacity")
        self.animation.setDuration(1000)
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)
        self.animation.start()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())