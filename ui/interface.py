"""
PyQt5 GUI for OpenFace application
"""
import sys
import cv2
import numpy as np
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QImage, QPixmap
import os


class MainWindow(QMainWindow):
    def __init__(self, app_controller):
        super().__init__()
        self.app_controller = app_controller
        self.init_ui()
        
        # Timer for frame updates
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)  # ~30 FPS
    
    def init_ui(self):
        """Initialize UI components"""
        self.setWindowTitle("OpenFace 3.0 Multi-Person Tracker")
        self.setGeometry(100, 100, 1280, 800)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        
        # Video display
        self.video_label = QLabel()
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setMinimumSize(1280, 720)
        layout.addWidget(self.video_label)
        
        # Status label
        self.status_label = QLabel("Ready")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)
        
        # Button layout
        button_layout = QHBoxLayout()
        layout.addLayout(button_layout)
        
        # Calibration button
        self.calib_button = QPushButton("Start Calibration")
        self.calib_button.clicked.connect(self.on_calibration_clicked)
        button_layout.addWidget(self.calib_button)
        
        # Detection toggle button
        self.detect_button = QPushButton("Start Detection")
        self.detect_button.clicked.connect(self.on_detection_clicked)
        button_layout.addWidget(self.detect_button)
        
        # Open captures folder button
        self.folder_button = QPushButton("Open Captures Folder")
        self.folder_button.clicked.connect(self.on_open_folder_clicked)
        button_layout.addWidget(self.folder_button)
    
    def update_frame(self):
        """Update video frame"""
        frame = self.app_controller.get_current_frame()
        if frame is not None:
            # Convert to Qt format
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_frame.shape
            bytes_per_line = ch * w
            qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            
            # Scale to fit label
            pixmap = QPixmap.fromImage(qt_image)
            scaled_pixmap = pixmap.scaled(self.video_label.size(), Qt.KeepAspectRatio)
            self.video_label.setPixmap(scaled_pixmap)
        
        # Update status
        status = self.app_controller.get_status()
        self.status_label.setText(status)
    
    def on_calibration_clicked(self):
        """Handle calibration button click"""
        if self.app_controller.is_calibrating():
            self.app_controller.stop_calibration()
            self.calib_button.setText("Start Calibration")
        else:
            self.app_controller.start_calibration()
            self.calib_button.setText("Stop Calibration")
    
    def on_detection_clicked(self):
        """Handle detection toggle button click"""
        if self.app_controller.is_detecting():
            self.app_controller.stop_detection()
            self.detect_button.setText("Start Detection")
        else:
            self.app_controller.start_detection()
            self.detect_button.setText("Stop Detection")
    
    def on_open_folder_clicked(self):
        """Open captures folder"""
        import subprocess
        import platform
        
        folder = "captures"
        if not os.path.exists(folder):
            os.makedirs(folder)
        
        if platform.system() == "Darwin":  # macOS
            subprocess.Popen(["open", folder])
        elif platform.system() == "Windows":
            os.startfile(folder)
        else:  # Linux
            subprocess.Popen(["xdg-open", folder])
    
    def closeEvent(self, event):
        """Handle window close"""
        self.app_controller.cleanup()
        event.accept()
