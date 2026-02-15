from PySide6.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from datetime import datetime
from typing import List, Dict
import matplotlib.dates as mdates


class ChartWidget(QWidget):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        self.figure = Figure(figsize=(10, 8))
        self.canvas = FigureCanvas(self.figure)
        self.ax_temp = self.figure.add_subplot(2, 1, 1)
        self.ax_humidity = self.figure.add_subplot(2, 1, 2)
        layout.addWidget(self.canvas)
        self.figure.tight_layout(pad=3.0)
        
    def update_charts(self, readings: List[Dict]):
        self.ax_temp.clear()
        self.ax_humidity.clear()
        
        if not readings:
            self.ax_temp.text(0.5, 0.5, 'No data available', 
                            ha='center', va='center', transform=self.ax_temp.transAxes)
            self.ax_humidity.text(0.5, 0.5, 'No data available',
                                ha='center', va='center', transform=self.ax_humidity.transAxes)
            self.canvas.draw()
            return
        
        sorted_readings = sorted(readings, key=lambda x: x.get('created_at', ''))
        timestamps = []
        temperatures = []
        humidities = []
        
        for reading in sorted_readings:
            try:
                ts_str = reading.get('created_at', '')
                if ts_str:
                    if '.' in ts_str:
                        ts = datetime.fromisoformat(ts_str.replace('Z', '+00:00'))
                    else:
                        ts = datetime.fromisoformat(ts_str.replace('Z', '+00:00'))
                    timestamps.append(ts)
                    temperatures.append(reading.get('temperature', 0))
                    humidities.append(reading.get('humidity', 0))
            except (ValueError, TypeError) as e:
                print(f"Error parsing timestamp: {e}")
                continue
        
        if not timestamps:
            self.ax_temp.text(0.5, 0.5, 'No valid data to display',
                            ha='center', va='center', transform=self.ax_temp.transAxes)
            self.ax_humidity.text(0.5, 0.5, 'No valid data to display',
                                ha='center', va='center', transform=self.ax_humidity.transAxes)
            self.canvas.draw()
            return
        
        self.ax_temp.plot(timestamps, temperatures, 'r-', marker='o', markersize=4, linewidth=2, label='Temperature')
        self.ax_temp.set_xlabel('Time')
        self.ax_temp.set_ylabel('Temperature (°C)', color='r')
        self.ax_temp.set_title('Temperature Over Time')
        self.ax_temp.tick_params(axis='y', labelcolor='r')
        self.ax_temp.grid(True, alpha=0.3)
        self.ax_temp.legend(loc='upper left')
        self.ax_temp.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        self.ax_temp.tick_params(axis='x', rotation=45)
        
        self.ax_humidity.plot(timestamps, humidities, 'b-', marker='s', markersize=4, linewidth=2, label='Humidity')
        self.ax_humidity.set_xlabel('Time')
        self.ax_humidity.set_ylabel('Humidity (%)', color='b')
        self.ax_humidity.set_title('Humidity Over Time')
        self.ax_humidity.tick_params(axis='y', labelcolor='b')
        self.ax_humidity.grid(True, alpha=0.3)
        self.ax_humidity.legend(loc='upper left')
        self.ax_humidity.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        self.ax_humidity.tick_params(axis='x', rotation=45)
        
        self.figure.tight_layout(pad=3.0)
        self.canvas.draw()
