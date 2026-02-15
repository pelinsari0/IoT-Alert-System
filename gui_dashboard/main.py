import sys
from datetime import datetime
from typing import List, Dict, Optional

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QComboBox, QSpinBox, QCheckBox, QTableWidget,
    QTableWidgetItem, QTabWidget, QMessageBox, QHeaderView, QGroupBox
)
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QColor, QFont

from gui_dashboard.api_client import APIClient
from gui_dashboard.chart_widget import ChartWidget


class MainWindow(QMainWindow):
    
    def __init__(self):
        super().__init__()
        self.api_client = APIClient()
        self.auto_refresh_timer = QTimer()
        self.auto_refresh_timer.timeout.connect(self.refresh_data)
        
        self.setup_ui()
        self.refresh_data()
    
    def setup_ui(self):
        self.setWindowTitle("IoT Alert System Dashboard")
        self.setMinimumSize(1200, 800)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        # Left panel (controls)
        left_panel = self.create_left_panel()
        main_layout.addWidget(left_panel, stretch=0)
        
        # Right panel (content)
        right_panel = self.create_right_panel()
        main_layout.addWidget(right_panel, stretch=1)
        
        # Status bar
        self.status_label = QLabel("Status: Checking connection...")
        self.last_refresh_label = QLabel("Last refresh: Never")
        self.statusBar().addPermanentWidget(self.status_label)
        self.statusBar().addPermanentWidget(self.last_refresh_label)
    
    def create_left_panel(self) -> QWidget:
        panel = QGroupBox("Controls")
        layout = QVBoxLayout(panel)
        
        filter_label = QLabel("Filter by Device:")
        filter_label.setFont(QFont("Arial", 10, QFont.Bold))
        layout.addWidget(filter_label)
        
        self.device_combo = QComboBox()
        self.device_combo.addItem("All Devices", None)
        self.device_combo.currentIndexChanged.connect(self.on_filter_changed)
        layout.addWidget(self.device_combo)
        
        layout.addSpacing(20)
        
        limit_label = QLabel("Number of Records:")
        limit_label.setFont(QFont("Arial", 10, QFont.Bold))
        layout.addWidget(limit_label)
        
        self.limit_spinbox = QSpinBox()
        self.limit_spinbox.setMinimum(10)
        self.limit_spinbox.setMaximum(200)
        self.limit_spinbox.setValue(50)
        self.limit_spinbox.setSuffix(" records")
        self.limit_spinbox.valueChanged.connect(self.on_filter_changed)
        layout.addWidget(self.limit_spinbox)
        
        layout.addSpacing(20)
        
        self.refresh_button = QPushButton("🔄 Refresh Now")
        self.refresh_button.clicked.connect(self.refresh_data)
        layout.addWidget(self.refresh_button)
        
        layout.addSpacing(10)
        
        self.auto_refresh_checkbox = QCheckBox("Auto Refresh")
        self.auto_refresh_checkbox.setChecked(False)
        self.auto_refresh_checkbox.stateChanged.connect(self.toggle_auto_refresh)
        layout.addWidget(self.auto_refresh_checkbox)
        
        auto_refresh_info = QLabel("(Every 7 seconds)")
        auto_refresh_info.setStyleSheet("color: gray; font-size: 9pt;")
        layout.addWidget(auto_refresh_info)
        
        layout.addStretch()
        
        connection_group = QGroupBox("Connection Info")
        conn_layout = QVBoxLayout(connection_group)
        
        self.connection_status_label = QLabel("🔴 Offline")
        self.connection_status_label.setFont(QFont("Arial", 11, QFont.Bold))
        conn_layout.addWidget(self.connection_status_label)
        
        api_url_label = QLabel("API: http://127.0.0.1:9000")
        api_url_label.setStyleSheet("color: gray; font-size: 9pt;")
        conn_layout.addWidget(api_url_label)
        
        layout.addWidget(connection_group)
        
        panel.setMaximumWidth(300)
        return panel
    
    def create_right_panel(self) -> QWidget:
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        self.tab_widget = QTabWidget()
        
        self.readings_table = self.create_readings_table()
        self.tab_widget.addTab(self.readings_table, "📊 Readings")
        
        self.alerts_table = self.create_alerts_table()
        self.tab_widget.addTab(self.alerts_table, "🚨 Alerts")
        
        self.chart_widget = ChartWidget()
        self.tab_widget.addTab(self.chart_widget, "📈 Charts")
        
        self.emails_table = self.create_emails_table()
        self.tab_widget.addTab(self.emails_table, "📧 Emails")
        
        layout.addWidget(self.tab_widget)
        return panel
    
    def create_readings_table(self) -> QTableWidget:
        table = QTableWidget()
        table.setColumnCount(7)
        table.setHorizontalHeaderLabels([
            "ID", "Device ID", "Location", "Temperature (°C)", 
            "Humidity (%)", "Motion", "Created At"
        ])
        
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)
        
        table.setAlternatingRowColors(True)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        
        return table
    
    def create_alerts_table(self) -> QTableWidget:
        table = QTableWidget()
        table.setColumnCount(7)
        table.setHorizontalHeaderLabels([
            "ID", "Device ID", "Location", "Alert Type", 
            "Message", "Emailed", "Created At"
        ])
        
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.Stretch)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)
        
        table.setAlternatingRowColors(True)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        
        return table
    
    def create_emails_table(self) -> QTableWidget:
        table = QTableWidget()
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels([
            "ID", "To", "Subject", "Body", "Sent At"
        ])
        
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        
        table.setAlternatingRowColors(True)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setWordWrap(True)
        
        return table
    
    def refresh_data(self):
        is_connected = self.api_client.check_connection()
        self.update_connection_status(is_connected)
        
        if not is_connected:
            QMessageBox.warning(
                self, 
                "Connection Error",
                "Unable to connect to the API at http://127.0.0.1:9000\n\n"
                "Please ensure the FastAPI backend is running:\n"
                "uvicorn app.main:app --reload --host 127.0.0.1 --port 9000"
            )
            return
        
        device_id = self.device_combo.currentData()
        limit = self.limit_spinbox.value()
        
        try:
            readings = self.api_client.get_readings(limit=limit, device_id=device_id)
            alerts = self.api_client.get_alerts(limit=limit, device_id=device_id)
            emails = self.api_client.get_email_log(limit=limit)
            
            self.update_readings_table(readings)
            self.update_alerts_table(alerts)
            self.update_emails_table(emails)
            
            self.chart_widget.update_charts(readings)
            
            if self.device_combo.currentIndex() == 0:
                self.update_device_combo()
            
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.last_refresh_label.setText(f"Last refresh: {current_time}")
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"An error occurred while fetching data:\n{str(e)}"
            )
    
    def update_connection_status(self, is_connected: bool):
        if is_connected:
            self.connection_status_label.setText("🟢 Connected")
            self.connection_status_label.setStyleSheet("color: green;")
            self.status_label.setText("Status: Connected")
            self.status_label.setStyleSheet("color: green;")
        else:
            self.connection_status_label.setText("🔴 Offline")
            self.connection_status_label.setStyleSheet("color: red;")
            self.status_label.setText("Status: Offline")
            self.status_label.setStyleSheet("color: red;")
    
    def update_device_combo(self):
        current_device = self.device_combo.currentData()
        device_ids = self.api_client.get_unique_device_ids()
        
        self.device_combo.blockSignals(True)
        
        self.device_combo.clear()
        self.device_combo.addItem("All Devices", None)
        
        for device_id in device_ids:
            self.device_combo.addItem(device_id, device_id)
        
        if current_device:
            index = self.device_combo.findData(current_device)
            if index >= 0:
                self.device_combo.setCurrentIndex(index)
        
        self.device_combo.blockSignals(False)
    
    def update_readings_table(self, readings: List[Dict]):
        self.readings_table.setRowCount(0)
        
        for row_idx, reading in enumerate(readings):
            self.readings_table.insertRow(row_idx)
            
            self.readings_table.setItem(row_idx, 0, 
                QTableWidgetItem(str(reading.get('id', ''))))
            
            self.readings_table.setItem(row_idx, 1,
                QTableWidgetItem(str(reading.get('device_id', ''))))
            
            self.readings_table.setItem(row_idx, 2,
                QTableWidgetItem(str(reading.get('location', ''))))
            
            temp = reading.get('temperature', 0)
            temp_item = QTableWidgetItem(f"{temp:.1f}")
            temp_item.setTextAlignment(Qt.AlignCenter)
            self.readings_table.setItem(row_idx, 3, temp_item)
            
            humidity = reading.get('humidity', 0)
            humidity_item = QTableWidgetItem(f"{humidity:.1f}")
            humidity_item.setTextAlignment(Qt.AlignCenter)
            self.readings_table.setItem(row_idx, 4, humidity_item)
            
            motion = reading.get('motion', False)
            motion_item = QTableWidgetItem("●" if motion else "○")
            motion_item.setTextAlignment(Qt.AlignCenter)
            motion_item.setFont(QFont("Arial", 12, QFont.Bold))
            if motion:
                motion_item.setForeground(QColor(200, 0, 0))
            else:
                motion_item.setForeground(QColor(150, 150, 150))
            self.readings_table.setItem(row_idx, 5, motion_item)
            
            created_at = reading.get('created_at', '')
            self.readings_table.setItem(row_idx, 6,
                QTableWidgetItem(str(created_at)))
    
    def update_alerts_table(self, alerts: List[Dict]):
        self.alerts_table.setRowCount(0)
        
        for row_idx, alert in enumerate(alerts):
            self.alerts_table.insertRow(row_idx)
            
            alert_type = alert.get('alert_type', '')
            
            if alert_type == 'HIGH_TEMP':
                bg_color = QColor(255, 180, 180)
                text_color = QColor(139, 0, 0)
            elif alert_type == 'HUMIDITY':
                bg_color = QColor(255, 200, 120)
                text_color = QColor(139, 69, 0)
            elif alert_type == 'MOTION':
                bg_color = QColor(255, 240, 150)
                text_color = QColor(139, 115, 0)
            else:
                bg_color = QColor(200, 200, 240)
                text_color = QColor(0, 0, 139)
            id_item = QTableWidgetItem(str(alert.get('id', '')))
            id_item.setBackground(bg_color)
            id_item.setForeground(text_color)
            self.alerts_table.setItem(row_idx, 0, id_item)
            
            device_item = QTableWidgetItem(str(alert.get('device_id', '')))
            device_item.setBackground(bg_color)
            device_item.setForeground(text_color)
            self.alerts_table.setItem(row_idx, 1, device_item)
            
            location_item = QTableWidgetItem(str(alert.get('location', '')))
            location_item.setBackground(bg_color)
            location_item.setForeground(text_color)
            self.alerts_table.setItem(row_idx, 2, location_item)
            
            type_item = QTableWidgetItem(alert_type)
            type_item.setBackground(bg_color)
            type_item.setForeground(text_color)
            type_item.setFont(QFont("Arial", 9, QFont.Bold))
            self.alerts_table.setItem(row_idx, 3, type_item)
            
            message_item = QTableWidgetItem(str(alert.get('message', '')))
            message_item.setBackground(bg_color)
            message_item.setForeground(text_color)
            self.alerts_table.setItem(row_idx, 4, message_item)
            
            emailed = alert.get('emailed', False)
            emailed_item = QTableWidgetItem("✓" if emailed else "✗")
            emailed_item.setTextAlignment(Qt.AlignCenter)
            emailed_item.setBackground(bg_color)
            emailed_item.setForeground(text_color)
            emailed_item.setFont(QFont("Arial", 10, QFont.Bold))
            self.alerts_table.setItem(row_idx, 5, emailed_item)
            
            created_item = QTableWidgetItem(str(alert.get('created_at', '')))
            created_item.setBackground(bg_color)
            created_item.setForeground(text_color)
            self.alerts_table.setItem(row_idx, 6, created_item)
    
    def update_emails_table(self, emails: List[Dict]):
        self.emails_table.setRowCount(0)
        
        if not emails:
            emails = [
                {
                    'id': 1,
                    'to_address': 'demo@example.com',
                    'subject': 'IoT Alert: HIGH_TEMP',
                    'body': 'High temperature detected at living_room (sensor-1)\n\nTime: 2025-12-01T10:00:00',
                    'sent_at': '2025-12-01T10:00:00'
                },
                {
                    'id': 2,
                    'to_address': 'demo@example.com',
                    'subject': 'IoT Alert: HUMIDITY',
                    'body': 'Abnormal humidity detected in kitchen (sensor-2)\n\nTime: 2025-12-01T11:30:00',
                    'sent_at': '2025-12-01T11:30:00'
                },
                {
                    'id': 3,
                    'to_address': 'demo@example.com',
                    'subject': 'IoT Alert: MOTION_NIGHT',
                    'body': 'Motion detected at night in garage (sensor-3)\n\nTime: 2025-12-01T02:15:00',
                    'sent_at': '2025-12-01T02:15:00'
                }
            ]
        
        for row_idx, email in enumerate(emails):
            self.emails_table.insertRow(row_idx)
            
            subject = email.get('subject', '')
            
            if 'HIGH_TEMP' in subject:
                bg_color = QColor(255, 180, 180)
                text_color = QColor(139, 0, 0)
            elif 'HUMIDITY' in subject:
                bg_color = QColor(255, 200, 120)
                text_color = QColor(139, 69, 0)
            elif 'MOTION' in subject:
                bg_color = QColor(255, 240, 150)
                text_color = QColor(139, 115, 0)
            else:
                bg_color = QColor(240, 240, 240)
                text_color = QColor(0, 0, 0)
            
            id_item = QTableWidgetItem(str(email.get('id', '')))
            id_item.setBackground(bg_color)
            id_item.setForeground(text_color)
            self.emails_table.setItem(row_idx, 0, id_item)
            
            to_item = QTableWidgetItem(str(email.get('to_address', '')))
            to_item.setBackground(bg_color)
            to_item.setForeground(text_color)
            self.emails_table.setItem(row_idx, 1, to_item)
            
            subject_item = QTableWidgetItem(subject)
            subject_item.setBackground(bg_color)
            subject_item.setForeground(text_color)
            subject_item.setFont(QFont("Arial", 9, QFont.Bold))
            self.emails_table.setItem(row_idx, 2, subject_item)
            
            body_item = QTableWidgetItem(str(email.get('body', '')))
            body_item.setBackground(bg_color)
            body_item.setForeground(text_color)
            self.emails_table.setItem(row_idx, 3, body_item)
            
            sent_item = QTableWidgetItem(str(email.get('sent_at', '')))
            sent_item.setBackground(bg_color)
            sent_item.setForeground(text_color)
            self.emails_table.setItem(row_idx, 4, sent_item)
        
        self.emails_table.resizeRowsToContents()
    
    def on_filter_changed(self):
        self.refresh_data()
    
    def toggle_auto_refresh(self, state):
        if state == Qt.Checked:
            self.auto_refresh_timer.start(7000)
            self.auto_refresh_checkbox.setText("Auto Refresh (ON)")
        else:
            self.auto_refresh_timer.stop()
            self.auto_refresh_checkbox.setText("Auto Refresh")


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
