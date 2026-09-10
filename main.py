# Standard library imports
import os
import sys
import datetime
import math
import platform
import re
import subprocess
from typing import Optional

# Third-party imports
import cv2
import numpy as np
import serial.tools.list_ports

# OpenCV may set Qt plugin paths that conflict with PyQt5 on Linux/Wayland.
for env_key in ("QT_QPA_PLATFORM_PLUGIN_PATH", "QT_PLUGIN_PATH"):
    env_value = os.environ.get(env_key, "")
    if "cv2" in env_value:
        os.environ.pop(env_key, None)

# PyQt5 imports
from PyQt5 import QtCore, QtGui, QtSvg
from PyQt5.QtCore import Qt, pyqtSlot, QFile, QTextStream, QTimer, pyqtSignal, QThread, QRectF
from PyQt5.QtGui import QColor, QPixmap, QPainter, QFont, QPen, QTransform
from PyQt5.QtWidgets import (QMainWindow, QApplication, QPushButton, QWidget, 
                           QGraphicsDropShadowEffect, QGridLayout)

# Local imports
from qfi import qfi_ADI, qfi_ALT, qfi_SI, qfi_HSI, qfi_VSI, qfi_TC
from sidebar import Ui_MainWindow as Ui_Mainwindow_sidebar
from splash import Ui_MainWindow
from map_widget import MapWidget

# Constants
class Constants:
    """Application constants for better maintainability."""
    
    # Window and display settings
    DISPLAY_WIDTH = 640
    DISPLAY_HEIGHT = 480
    WINDOW_TITLE = "AYBUHAVK"
    
    # Flight instrument settings
    INSTRUMENT_SIZE = 240
    UPDATE_INTERVAL_MS = 50
    
    # Camera settings
    CAMERA_UPDATE_INTERVAL_MS = 35
    
    # Splash screen settings
    SPLASH_PROGRESS_MAX = 100
    SPLASH_TIMER_INTERVAL = 35
    
    # UI text constants
    SPLASH_WELCOME_TEXT = "<strong>WELCOME</strong> TO MY APPLICATION"
    SPLASH_LOADING_DB_TEXT = "<strong>LOADING</strong> DATABASE"
    SPLASH_LOADING_UI_TEXT = "<strong>LOADING</strong> USER INTERFACE"
    
    # Console messages
    CAMERA_STARTED_MSG = "Kamera başlatıldı"
    CAMERA_STOPPED_MSG = "Kamera durduruldu"
    CAMERA_OFF_TEXT = "Kamera Kapalı"
    
    # Baud rate options
    BAUD_RATES = [110, 300, 600, 1200, 2400, 4800, 9600, 
                  14400, 19200, 38400, 57600, 115200, 128000, 256000]
    
    # Flight instrument simulation
    ROLL_INCREMENT = 0.5
    PITCH_AMPLITUDE = 30
    HEADING_INCREMENT = 1
    AIRSPEED_BASE = 1.5
    AIRSPEED_MULTIPLIER = 10
    ALTITUDE_BASE = 1.5
    ALTITUDE_MULTIPLIER = 50


class VideoThread(QThread):
    """
    Thread class for handling video capture from camera devices.
    
    This class runs in a separate thread to prevent blocking the main UI
    while capturing video frames from the camera.
    """
    change_pixmap_signal = pyqtSignal(np.ndarray)

    def __init__(self) -> None:
        """Initialize the video thread with default settings."""
        super().__init__()
        self._run_flag: bool = True
        self.cap_index: int = 0
        
    def run(self) -> None:
        """
        Main thread execution method.
        
        Captures video frames from the specified camera device and emits
        them via the change_pixmap_signal for display in the UI.
        """
        cap = cv2.VideoCapture(self.cap_index)
        while self._run_flag:
            ret, cv_img = cap.read()
            if ret:
                self.change_pixmap_signal.emit(cv_img)
        cap.release()

    def stop(self) -> None:
        """
        Stop the video thread gracefully.
        
        Sets the run flag to False and waits for the thread to finish
        execution before returning.
        """
        self._run_flag = False
        self.wait()
# Global variables
counter = 0


class MainWindow(QMainWindow):
    """
    Main application window class.
    
    This class handles the primary user interface including flight instruments,
    camera controls, map widget, and various UI interactions.
    """
    def __init__(self) -> None:
        """Initialize the main window with all UI components and settings."""
        super(MainWindow, self).__init__()
        self._setup_ui()
        self._setup_flight_instruments()
        self._setup_camera()
        self._setup_map_widget()
        self._setup_serial_ports()
        self._initialize_ui_state()

    def _setup_ui(self) -> None:
        """Setup the main UI components."""
        self.ui1 = Ui_Mainwindow_sidebar()
        self.ui1.setupUi(self)
        self.setWindowTitle(Constants.WINDOW_TITLE)

    def _setup_flight_instruments(self) -> None:
        """Initialize and configure flight instrument widgets."""
        # Add ADI (Attitude Direction Indicator)
        self.adi = FlightInstrumentWidget(self)
        self.adi.resize(Constants.INSTRUMENT_SIZE, Constants.INSTRUMENT_SIZE)
        self.adi.setParent(self.ui1.ADI_frame)

        # Add HSI (Horizontal Situation Indicator)
        self.hsi = qfi_HSI.qfi_HSI(self)
        self.hsi.resize(Constants.INSTRUMENT_SIZE, Constants.INSTRUMENT_SIZE)
        self.hsi.reinit()
        self.hsi.setParent(self.ui1.HSI_frame)

        # Add SI (Speed Indicator)
        self.si = qfi_SI.qfi_SI(self)
        self.si.resize(Constants.INSTRUMENT_SIZE, Constants.INSTRUMENT_SIZE)
        self.si.reinit()
        self.si.setParent(self.ui1.SI_frame)

    def _setup_camera(self) -> None:
        """Initialize camera components and video thread."""
        self.display_width = Constants.DISPLAY_WIDTH
        self.display_height = Constants.DISPLAY_HEIGHT
        self.thread = VideoThread()
        self.thread.change_pixmap_signal.connect(self.update_image)
        self.stop_camera()

        # Connect camera control buttons
        self.ui1.openCamera.clicked.connect(self.start_camera)
        self.ui1.closeCamera.clicked.connect(self.stop_camera)

    def _setup_map_widget(self) -> None:
        """Setup the map widget for navigation."""
        self.setup_map_widget()

    def _setup_serial_ports(self) -> None:
        """Initialize serial port and baud rate settings."""
        self.update_port()
        self.camera_port()
        self.baud_rate_list = Constants.BAUD_RATES
        self.update_baudrate()

    def _initialize_ui_state(self) -> None:
        """Set initial UI state and visibility."""
        self.ui1.full_menu_widget.hide()
        self.ui1.profile_widget.hide()
        self.ui1.stackedWidget.setCurrentIndex(0)
        self.ui1.homeBtn.setChecked(True)
        
        # Setup console scrollbar
        self.vertical_scrollbar = self.ui1.console_home.verticalScrollBar()
        self.vertical_scrollbar.setValue(self.vertical_scrollbar.maximum())


    def closeEvent(self, event) -> None:
        """
        Handle application close event.
        
        Args:
            event: The close event
        """
        self.thread.stop()
        event.accept()

    # Camera related methods
    @pyqtSlot(np.ndarray)
    def update_image(self, cv_img: np.ndarray) -> None:
        """
        Update the image label with a new OpenCV image.
        
        Args:
            cv_img: OpenCV image array to display
        """
        qt_img = self.convert_cv_qt(cv_img)
        self.ui1.image_label.setPixmap(qt_img)
    
    # Serial port and device management
    def update_port(self) -> None:
        """Update the list of available serial ports."""
        self.ui1.PortSelect.clear()
        ports = serial.tools.list_ports.comports()
        print(f"Available ports: {ports}")
        for port in ports:
            self.ui1.PortSelect.addItem(port.device)
    
    def update_baudrate(self) -> None:
        """Populate the baud rate selection dropdown."""
        for baud_rate in self.baud_rate_list:
            self.ui1.BaudRateSelect.addItem(str(baud_rate))
        
        # Set default baud rate to 115200
        default_baud_rate = "115200"
        index = self.ui1.BaudRateSelect.findText(default_baud_rate)
        if index >= 0:
            self.ui1.BaudRateSelect.setCurrentIndex(index)

    def camera_port(self) -> None:
        """Detect and populate available camera devices."""
        system = platform.system().lower()

        if "windows" in system:
            cmd = ['ffmpeg', '-list_devices', 'true', '-f', 'dshow', '-i', 'dummy']
        elif "linux" in system:
            cmd = ['ffmpeg', '-f', 'v4l2', '-list_devices', 'true', '-i', '']
        elif "darwin" in system:  # macOS
            cmd = ['ffmpeg', '-f', 'avfoundation', '-list_devices', 'true', '-i', '']
        else:
            raise Exception("Unsupported operating system")

        try:
            result = subprocess.run(cmd, stderr=subprocess.PIPE, text=True)
            devices = re.findall(r'\[.*?\] "(.*?)"', result.stderr)
            for device in devices:
                self.ui1.cameraSelect.addItem(device)
        except Exception as e:
            print(f"Error detecting camera devices: {e}")
        
    def convert_cv_qt(self, cv_img: np.ndarray) -> QPixmap:
        """
        Convert OpenCV image to QPixmap for display.
        
        Args:
            cv_img: OpenCV image array
            
        Returns:
            QPixmap: Converted image for Qt display
        """
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        p = convert_to_Qt_format.scaled(self.display_width, self.display_height, Qt.KeepAspectRatio)
        return QPixmap.fromImage(p)
    

    # UI Navigation methods
    def on_homeBtn_toggled(self) -> None:
        """Switch to home page and scroll console to bottom."""
        self.ui1.stackedWidget.setCurrentIndex(0)
        self.vertical_scrollbar.setValue(self.vertical_scrollbar.maximum())

    def on_mapsBtn_toggled(self) -> None:
        """Switch to maps page."""
        self.ui1.stackedWidget.setCurrentIndex(5)

    def on_terminalBtn_toggled(self) -> None:
        """Switch to terminal page."""
        self.ui1.stackedWidget.setCurrentIndex(1)
    
    def on_settingsBtn_toggled(self) -> None:
        """Switch to settings page."""
        self.ui1.stackedWidget.setCurrentIndex(2)
    
    def on_infoBtn_toggled(self) -> None:
        """Switch to info page."""
        self.ui1.stackedWidget.setCurrentIndex(3)

    def on_helpBtn_toggled(self) -> None:
        """Switch to help page."""
        self.ui1.stackedWidget.setCurrentIndex(4)
        
    # Map widget methods
    def setup_map_widget(self) -> None:
        """Setup and configure the map widget."""
        self.map_widget = MapWidget()
        
        # Remove existing label and add map widget
        self.ui1.pageMaps.setParent(None)
        self.ui1.horizontalLayout_7.addWidget(self.map_widget)
        
        # Connect map widget signals
        self.map_widget.coordinate_clicked.connect(self.on_coordinate_clicked)
        self.map_widget.command_executed.connect(self.on_command_executed)
        
    def on_coordinate_clicked(self, lat: float, lon: float) -> None:
        """
        Handle map coordinate click events.
        
        Args:
            lat: Latitude coordinate
            lon: Longitude coordinate
        """
        print(f"Map clicked: Latitude={lat:.6f}, Longitude={lon:.6f}")
        
    def on_command_executed(self, command: str) -> None:
        """
        Handle command execution events from map widget.
        
        Args:
            command: The executed command string
        """
        print(f"Command executed: {command}")
        
        # Add message to console
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        message = f"[{timestamp}] Command: {command}"
        self.ui1.console_home.append(message)
        
        # Scroll to bottom
        scrollbar = self.ui1.console_home.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
        
    
        
    # Camera control methods
    def start_camera(self) -> None:
        """Start camera capture and update UI accordingly."""
        try:
            if not self.thread._run_flag:
                # Create new thread
                self.thread = VideoThread()
                self.thread.cap_index = self.ui1.cameraSelect.currentIndex()
                self.thread.change_pixmap_signal.connect(self.update_image)
                self.thread.start()
                
                # Update button states
                self.ui1.openCamera.setEnabled(False)
                self.ui1.closeCamera.setEnabled(True)
                
                # Add message to console
                self._add_console_message(Constants.CAMERA_STARTED_MSG)
                
        except Exception as e:
            print(f"Camera start error: {e}")
            
    def stop_camera(self) -> None:
        """Stop camera capture and update UI accordingly."""
        try:
            if self.thread._run_flag:
                # Stop thread
                self.thread.stop()
                
                # Update button states
                self.ui1.openCamera.setEnabled(True)
                self.ui1.closeCamera.setEnabled(False)
                
                # Clear camera image
                self.ui1.image_label.clear()
                self.ui1.image_label.setText(Constants.CAMERA_OFF_TEXT)
                
                # Add message to console
                self._add_console_message(Constants.CAMERA_STOPPED_MSG)
                
        except Exception as e:
            print(f"Camera stop error: {e}")

    def _add_console_message(self, message: str) -> None:
        """
        Add a timestamped message to the console and scroll to bottom.
        
        Args:
            message: Message to add to console
        """
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}"
        self.ui1.console_home.append(formatted_message)
        
        # Scroll to bottom
        scrollbar = self.ui1.console_home.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
        
        print(formatted_message)



class SplashScreen(QMainWindow):
    """
    Splash screen window displayed during application startup.
    
    Shows a loading progress bar and welcome messages while the main
    application initializes.
    """
    
    def __init__(self) -> None:
        """Initialize the splash screen with UI and effects."""
        super(SplashScreen, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self._setup_window_properties()
        self._setup_visual_effects()
        self._setup_timer()
        self._setup_text_sequence()

    def _setup_window_properties(self) -> None:
        """Configure window properties for splash screen."""
        # Remove title bar
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

    def _setup_visual_effects(self) -> None:
        """Setup visual effects like drop shadow."""
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(20)
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(0)
        self.shadow.setColor(QColor(0, 0, 0, 90))
        self.ui.dropShadowFrame.setGraphicsEffect(self.shadow)

    def _setup_timer(self) -> None:
        """Setup progress timer."""
        self.timer = QTimer()
        self.timer.timeout.connect(self.progress)
        self.timer.start(Constants.SPLASH_TIMER_INTERVAL)

    def _setup_text_sequence(self) -> None:
        """Setup the sequence of text changes during loading."""
        # Initial text
        self.ui.label_2_description.setText(Constants.SPLASH_WELCOME_TEXT)

        # Change texts at specific intervals
        QtCore.QTimer.singleShot(1500, lambda: self.ui.label_2_description.setText(Constants.SPLASH_LOADING_DB_TEXT))
        QtCore.QTimer.singleShot(3000, lambda: self.ui.label_2_description.setText(Constants.SPLASH_LOADING_UI_TEXT))

    def progress(self) -> None:
        """Update progress bar and handle splash screen completion."""
        global counter

        # Set progress bar value
        self.ui.progressBar.setValue(counter)

        # Close splash screen and open main application
        if counter > Constants.SPLASH_PROGRESS_MAX:
            self.timer.stop()
            self.window = MainWindow()
            self.window.show()
            self.close()

        counter += 1


class FlightInstrumentWidget(QWidget):
    """
    Custom flight instrument widget for displaying aircraft attitude.
    
    This widget displays an artificial horizon with roll and pitch indicators,
    along with airspeed and altitude displays.
    """
    
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Initialize the flight instrument widget."""
        super().__init__(parent)
        self.setMinimumSize(Constants.INSTRUMENT_SIZE, Constants.INSTRUMENT_SIZE)
        
        # Flight parameters
        self.roll: float = 0.0      # Roll angle (degrees)
        self.pitch: float = 0.0     # Pitch angle (degrees)
        self.heading: int = 0       # Heading (degrees)
        self.airspeed: float = 0.0  # Airspeed
        self.altitude: float = 0.0  # Altitude

    def simulate_data(self) -> None:
        """Simulate flight data for demonstration purposes."""
        self.roll = (self.roll + Constants.ROLL_INCREMENT) % 360
        self.pitch = math.sin(self.roll * math.pi / 180 * 0.1) * Constants.PITCH_AMPLITUDE
        self.heading = (self.heading + Constants.HEADING_INCREMENT) % 360
        self.airspeed = (math.sin(self.roll * math.pi / 180 * 0.05) + Constants.AIRSPEED_BASE) * Constants.AIRSPEED_MULTIPLIER
        self.altitude = (math.sin(self.roll * math.pi / 180 * 0.02) + Constants.ALTITUDE_BASE) * Constants.ALTITUDE_MULTIPLIER
        self.update()  # Redraw widget

    def paintEvent(self, event) -> None:
        """
        Paint the flight instrument display.
        
        Args:
            event: Paint event
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        width = self.width()
        height = self.height()
        center_x = width / 2
        center_y = height / 2

        # Draw background (sky)
        painter.setBrush(QColor(0, 150, 255))  # Sky blue
        painter.drawRect(0, 0, width, height)

        # Apply transformation for horizon line and ground
        painter.save()
        painter.translate(center_x, center_y)
        painter.rotate(-self.roll)  # Rotate according to roll angle
        painter.translate(0, -self.pitch * (height / 60))  # Shift up/down according to pitch

        # Draw ground (below horizon line)
        painter.setBrush(QColor(100, 200, 50))  # Grass green
        ground_rect = QRectF(-width * 2, 0, width * 4, height * 4)
        painter.drawRect(ground_rect)

        # Draw horizon line
        painter.setPen(QPen(Qt.white, 2))
        painter.drawLine(int(-width / 2), 0, int(width / 2), 0)

        # Draw pitch lines
        painter.setPen(QPen(Qt.white, 1))
        for i in range(-30, 31, 10):  # -30 to +30 degrees
            y_offset = -i * (height / 60)  # Specific height for each 10 degrees
            painter.drawLine(-30, int(y_offset), 30, int(y_offset))
            if i != 0:
                painter.drawText(-50, int(y_offset) + 5, str(abs(i)))
                painter.drawText(35, int(y_offset) + 5, str(abs(i)))

        painter.restore()  # Restore transformation state

        # Draw instrument frame and fixed elements
        painter.setPen(QPen(Qt.white, 2))
        painter.setBrush(Qt.NoBrush)
        painter.drawRect(0, 0, width, height)  # Window borders

        # Draw heading indicator (top)
        painter.setPen(QPen(Qt.red, 2))
        painter.drawLine(int(center_x), 0, int(center_x), 20)  # Center marker
        painter.setFont(QFont("Arial", 10))
        painter.setPen(Qt.white)

        # Draw airspeed indicator (left)
        painter.setPen(QPen(Qt.white, 2))
        painter.setBrush(QColor(0, 0, 0, 150))  # Semi-transparent black
        painter.drawRect(0, int(center_y) - 80, 40, 160)
        painter.setPen(Qt.white)
        painter.drawText(5, int(center_y - self.airspeed * 3) + 5, str(int(self.airspeed)))

        # Draw altitude indicator (right)
        painter.setPen(QPen(Qt.white, 2))
        painter.setBrush(QColor(0, 0, 0, 150))  # Semi-transparent black
        painter.drawRect(width - 40, int(center_y) - 80, 40, 160)
        painter.setPen(Qt.white)
        painter.drawText(width - 35, int(center_y - self.altitude * 0.5) + 5, str(int(self.altitude)))

        # Draw fixed center marker
        painter.setPen(QPen(Qt.white, 2))
        painter.drawLine(int(center_x - 50), int(center_y), int(center_x - 20), int(center_y))
        painter.drawLine(int(center_x + 20), int(center_y), int(center_x + 50), int(center_y))
        painter.drawLine(int(center_x), int(center_y - 10), int(center_x), int(center_y - 30))

        # Draw "DISARMED" text
        painter.setPen(QPen(Qt.red, 3))
        painter.setFont(QFont("Arial", 24, QFont.Bold))
        painter.drawText(self.rect(), Qt.AlignCenter, "DISARMED")


if __name__ == "__main__":
    """Main application entry point."""
    app = QApplication(sys.argv)
    
    # Create and show splash screen
    splash_window = SplashScreen()
    splash_window.show()
    
    # Start application event loop
    sys.exit(app.exec())