import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QWidget,QGraphicsDropShadowEffect
from PyQt5.QtCore import Qt, pyqtSlot, QFile, QTextStream, QTimer, pyqtSignal, pyqtSlot, QThread, QRectF
from PyQt5.QtGui import QColor,QPixmap, QPainter, QFont, QPen, QTransform
from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout
from PyQt5 import QtGui,QtCore,QtSvg

import cv2
from threadGUI import ThreadGUI
import numpy as np
import datetime

from qfi import qfi_ADI, qfi_ALT, qfi_SI, qfi_HSI, qfi_VSI, qfi_TC
import math

from sidebar import Ui_MainWindow as Ui_Mainwindow_sidebar
from splash import Ui_MainWindow
from map_widget import MapWidget

import serial.tools.list_ports

import subprocess
import re
import platform

class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(np.ndarray)

    def __init__(self):
        super().__init__()
        self._run_flag = True
        self.cap_index = 0
        
    def run(self):
        # capture from web cam
        cap = cv2.VideoCapture(self.cap_index)
        while self._run_flag:
            ret, cv_img = cap.read()
            if ret:
                self.change_pixmap_signal.emit(cv_img)
        # shut down capture system
        cap.release()

    def stop(self):
        """Sets run flag to False and waits for thread to finish"""
        self._run_flag = False
        self.wait()
## ==> GLOBALS

counter = 0


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow,self).__init__()
        self.ui1 = Ui_Mainwindow_sidebar()
        self.ui1.setupUi(self)
        self.setWindowTitle("AYBUHAVK")

        #self.ui1.adi.setRoll(10)
        #self.ui1.adi.setPitch(20)

        # ADD ADI
        self.adi = FlightInstrumentWidget(self)
        self.adi.resize(240, 240)
        # self.adi.reinit()
        self.adi.setParent(self.ui1.ADI_frame)

        # ADD HSI
        self.hsi = qfi_HSI.qfi_HSI(self)
        self.hsi.resize(240, 240)
        self.hsi.reinit()
        self.hsi.setParent(self.ui1.HSI_frame)

        # Timer for flight instrument simulation
        """self.flight_instrument_timer = QTimer(self)
        self.flight_instrument_timer.timeout.connect(self.adi.simulate_data)
        self.flight_instrument_timer.start(50) # Update every 50 ms"""

        # ADD SI
        self.si = qfi_SI.qfi_SI(self)
        self.si.resize(240, 240)
        self.si.reinit()
        self.si.setParent(self.ui1.SI_frame)

        #loadJsonStyle(self, self.ui)
        self.ui1.full_menu_widget.hide()
        self.ui1.profile_widget.hide()
        self.ui1.stackedWidget.setCurrentIndex(0)
        self.ui1.homeBtn.setChecked(True)
        self.vertical_scrollbar = self.ui1.console_home.verticalScrollBar()

        # Dikey kaydırma çubuğunu en aşağıya taşı
        self.vertical_scrollbar.setValue(self.vertical_scrollbar.maximum())

        self.disply_width = 640
        self.display_height = 480
        self.thread = VideoThread()
        # connect its signal to the update_image slot
        self.thread.change_pixmap_signal.connect(self.update_image)
        self.stop_camera()

        # Kamera butonlarını ekle
        self.ui1.openCamera.clicked.connect(self.start_camera)
        self.ui1.closeCamera.clicked.connect(self.stop_camera)
        
        # Harita widget'ını ekle
        self.setup_map_widget()

        self.update_port()
        self.camera_port()
        self.baud_rate_list = [110, 300, 600, 1200, 2400, 4800, 9600, 
                                14400, 19200, 38400, 57600, 115200, 128000, 256000]
                                
        self.update_baudrate()


    def closeEvent(self, event):
        self.thread.stop()
        event.accept()

    @pyqtSlot(np.ndarray)
    def update_image(self, cv_img):
        """Updates the image_label with a new opencv image"""
        qt_img = self.convert_cv_qt(cv_img)
        self.ui1.image_label.setPixmap(qt_img)
    
    def update_port(self):
        self.ui1.PortSelect.clear()
        ports = serial.tools.list_ports.comports()
        print(ports)
        for port in ports:
            self.ui1.PortSelect.addItem(port.device)
    
    def update_baudrate(self):
        
        for i in self.baud_rate_list:
            self.ui1.BaudRateSelect.addItem(str(i))
            

    def camera_port(self):
        system = platform.system().lower()

        if "windows" in system:
            cmd = ['ffmpeg', '-list_devices', 'true', '-f', 'dshow', '-i', 'dummy']
        elif "linux" in system:
            cmd = ['ffmpeg', '-f', 'v4l2', '-list_devices', 'true', '-i', '']
        elif "darwin" in system:  # macOS
            cmd = ['ffmpeg', '-f', 'avfoundation', '-list_devices', 'true', '-i', '']
        else:
            raise Exception("Bilinmeyen işletim sistemi")

        result = subprocess.run(cmd, stderr=subprocess.PIPE, text=True)
        devices = re.findall(r'\[.*?\] "(.*?)"', result.stderr)
        for port in devices:
            self.ui1.cameraSelect.addItem(port)
        
    def convert_cv_qt(self, cv_img):
        """Convert from an opencv image to QPixmap"""
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        p = convert_to_Qt_format.scaled(self.disply_width, self.display_height, Qt.KeepAspectRatio)
        return QPixmap.fromImage(p)
    

    def on_homeBtn_toggled(self):
        self.ui1.stackedWidget.setCurrentIndex(0)
        self.vertical_scrollbar.setValue(self.vertical_scrollbar.maximum())

    def on_mapsBtn_toggled(self):
        self.ui1.stackedWidget.setCurrentIndex(5)

    def on_terminalBtn_toggled(self):
        self.ui1.stackedWidget.setCurrentIndex(1)
    
    def on_settingsBtn_toggled(self):
        self.ui1.stackedWidget.setCurrentIndex(2)
    
    def on_infoBtn_toggled(self):
        self.ui1.stackedWidget.setCurrentIndex(3)

    def on_helpBtn_toggled(self):
        self.ui1.stackedWidget.setCurrentIndex(4)
        
    def setup_map_widget(self):
        """Harita widget'ını kur ve harita sayfasına ekle"""
        # Harita widget'ını oluştur
        self.map_widget = MapWidget()
        
        # Harita sayfasındaki mevcut label'ı kaldır ve widget'ı ekle
        self.ui1.pageMaps.setParent(None)
        self.ui1.horizontalLayout_7.addWidget(self.map_widget)
        
        # Harita widget sinyallerini bağla
        self.map_widget.coordinate_clicked.connect(self.on_coordinate_clicked)
        self.map_widget.command_executed.connect(self.on_command_executed)
        
    def on_coordinate_clicked(self, lat, lon):
        """Harita tıklama olayı"""
        print(f"Harita tıklandı: Enlem={lat:.6f}, Boylam={lon:.6f}")
        
    def on_command_executed(self, command):
        """Komut çalıştırma olayı"""
        print(f"Komut çalıştırıldı: {command}")
        
        # Console'a mesaj ekle
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        message = f"[{timestamp}] Komut: {command}"
        self.ui1.console_home.append(message)
        
        # Scroll'u en alta taşı
        scrollbar = self.ui1.console_home.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
        
    
        
    def start_camera(self):
        """Kamerayı başlat"""
        try:
            if not self.thread._run_flag:
                # Yeni thread oluştur
                self.thread = VideoThread()
                self.thread.cap_index = self.ui1.cameraSelect.currentIndex()
                self.thread.change_pixmap_signal.connect(self.update_image)
                self.thread.start()
                
                # Buton durumlarını güncelle
                self.ui1.openCamera.setEnabled(False)
                self.ui1.closeCamera.setEnabled(True)
                
                # Console'a mesaj ekle
                timestamp = datetime.datetime.now().strftime("%H:%M:%S")
                message = f"[{timestamp}] Kamera başlatıldı"
                self.ui1.console_home.append(message)
                
                # Scroll'u en alta taşı
                scrollbar = self.ui1.console_home.verticalScrollBar()
                scrollbar.setValue(scrollbar.maximum())
                
                print(f"[{timestamp}] Kamera başlatıldı")
                
        except Exception as e:
            print(f"Kamera başlatma hatası: {e}")
            
    def stop_camera(self):
        """Kamerayı durdur"""
        try:
            if self.thread._run_flag:
                # Thread'i durdur
                self.thread.stop()
                
                # Buton durumlarını güncelle
                self.ui1.openCamera.setEnabled(True)
                self.ui1.closeCamera.setEnabled(False)
                
                # Kamera görüntüsünü temizle
                self.ui1.image_label.clear()
                self.ui1.image_label.setText("Kamera Kapalı")
                
                # Console'a mesaj ekle
                timestamp = datetime.datetime.now().strftime("%H:%M:%S")
                message = f"[{timestamp}] Kamera durduruldu"
                self.ui1.console_home.append(message)
                
                # Scroll'u en alta taşı
                scrollbar = self.ui1.console_home.verticalScrollBar()
                scrollbar.setValue(scrollbar.maximum())
                
                print(f"[{timestamp}] Kamera durduruldu")
                
        except Exception as e:
            print(f"Kamera durdurma hatası: {e}")



class SplashScreen(QMainWindow):
    def __init__(self):
        super(SplashScreen,self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        #REMOVE TITLE BAR

        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        #DROP SHADOW EFECT

        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(20)
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(0)
        self.shadow.setColor(QColor(0, 0, 0, 90))
        self.ui.dropShadowFrame.setGraphicsEffect(self.shadow)
    
        #QTIMER ==> START
        self.timer = QTimer()
        self.timer.timeout.connect(self.progress)
        self.timer.start(35)

         # Initial Text
        self.ui.label_2_description.setText("<strong>WELCOME</strong> TO MY APPLICATION")

        # Change Texts
        QtCore.QTimer.singleShot(1500, lambda: self.ui.label_2_description.setText("<strong>LOADING</strong> DATABASE"))
        QtCore.QTimer.singleShot(3000, lambda: self.ui.label_2_description.setText("<strong>LOADING</strong> USER INTERFACE"))


    def progress(self):
        global counter


        #SET VALUE TO PROGRESS BAR
        self.ui.progressBar.setValue(counter)

        #CLOSE SPLASH SCREEN AND OPEN APP
        if counter >100:
            #STOP TIMER
            self.timer.stop()
            self.window=MainWindow()
            self.window.show()
            #CLOSE SPLASH SCREEN
            self.close()

        counter +=1


class FlightInstrumentWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(240, 240)
        self.roll = 0.0  # Yatış açısı (derece)
        self.pitch = 0.0 # Eğim açısı (derece)
        self.heading = 0 # Başlık (derece)
        self.airspeed = 0.0 # Hava hızı
        self.altitude = 0.0 # Rakım

    def simulate_data(self):
        # Örnek olarak değerleri yavaşça değiştir
        self.roll = (self.roll + 0.5) % 360
        self.pitch = math.sin(self.roll * math.pi / 180 * 0.1) * 30 # -30 ile +30 arası
        self.heading = (self.heading + 1) % 360
        self.airspeed = (math.sin(self.roll * math.pi / 180 * 0.05) + 1.5) * 10 # 5 ile 25 arası
        self.altitude = (math.sin(self.roll * math.pi / 180 * 0.02) + 1.5) * 50 # 50 ile 150 arası
        self.update() # Widget'ı yeniden çiz

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        width = self.width()
        height = self.height()
        center_x = width / 2
        center_y = height / 2

        # Arka planı çiz (gökyüzü ve yer)
        painter.setBrush(QColor(0, 150, 255)) # Gökyüzü mavisi
        painter.drawRect(0, 0, width, height) # Tüm pencereyi kapla

        # Ufuk çizgisini ve yeri çizmek için dönüşüm uygula
        painter.save()
        painter.translate(center_x, center_y)
        painter.rotate(-self.roll) # Yatış açısına göre döndür
        painter.translate(0, -self.pitch * (height / 60)) # Eğim açısına göre yukarı/aşağı kaydır (örn: 60 derece için tam ekran yüksekliği)

        # Yeri çiz (ufuk çizgisinin altı)
        painter.setBrush(QColor(100, 200, 50)) # Çimen yeşili
        ground_rect = QRectF(-width * 2, 0, width * 4, height * 4) # Geniş bir dikdörtgen
        painter.drawRect(ground_rect)

        # Ufuk çizgisini çiz
        painter.setPen(QPen(Qt.white, 2))
        painter.drawLine(int(-width / 2), 0, int(width / 2), 0)

        # Eğim çizgilerini çiz
        painter.setPen(QPen(Qt.white, 1))
        for i in range(-30, 31, 10): # -30 ile +30 derece arası
            y_offset = -i * (height / 60) # Her 10 derece için belirli bir yükseklik
            painter.drawLine(-30, int(y_offset), 30, int(y_offset))
            if i != 0:
                painter.drawText(-50, int(y_offset) + 5, str(abs(i)))
                painter.drawText(35, int(y_offset) + 5, str(abs(i)))


        painter.restore() # Eski dönüşüm durumuna dön

        # Gösterge çerçevesi ve sabit elemanları çiz
        painter.setPen(QPen(Qt.white, 2))
        painter.setBrush(Qt.NoBrush)
        painter.drawRect(0, 0, width, height) # Pencere kenarları

        # Başlık göstergesini çiz (üst kısım)
        painter.setPen(QPen(Qt.red, 2))
        painter.drawLine(int(center_x), 0, int(center_x), 20) # Orta işaretleyici
        painter.setFont(QFont("Arial", 10))
        painter.setPen(Qt.white)

        # Başlık değerleri
        """for i in range(-60, 61, 10):
            angle_rad = math.radians(i)
            text_x = center_x + i * 2 # Basit bir ölçekleme
            text = str((self.heading + i + 360) % 360) # Güncel başlığa göre göster

            painter.drawText(int(text_x - 15), 35, text)"""


        # Hız göstergesi (sol)
        painter.setPen(QPen(Qt.white, 2))
        painter.setBrush(QColor(0,0,0,150)) # Yarı şeffaf siyah
        painter.drawRect(0, int(center_y) - 80, 40, 160)
        painter.setPen(Qt.white)
        painter.drawText(5, int(center_y - self.airspeed * 3) + 5, str(int(self.airspeed))) # Örnek gösterim

        # Rakım göstergesi (sağ)
        painter.setPen(QPen(Qt.white, 2))
        painter.setBrush(QColor(0,0,0,150)) # Yarı şeffaf siyah
        painter.drawRect(width - 40, int(center_y) - 80, 40, 160)
        painter.setPen(Qt.white)
        painter.drawText(width - 35, int(center_y - self.altitude * 0.5) + 5, str(int(self.altitude))) # Örnek gösterim


        # Sabit orta işaretçiyi çiz
        painter.setPen(QPen(Qt.white, 2))
        painter.drawLine(int(center_x - 50), int(center_y), int(center_x - 20), int(center_y))
        painter.drawLine(int(center_x + 20), int(center_y), int(center_x + 50), int(center_y))
        painter.drawLine(int(center_x), int(center_y - 10), int(center_x), int(center_y - 30))

        # "DISARMED" metni (eğer durum disarmed ise)
        painter.setPen(QPen(Qt.red, 3))
        painter.setFont(QFont("Arial", 24, QFont.Bold))
        painter.drawText(self.rect(), Qt.AlignCenter, "DISARMED")


if __name__=="__main__":
    app = QApplication(sys.argv)

    window=SplashScreen()
    window.show()
    sys.exit(app.exec())