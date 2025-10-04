import sys
import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QTextEdit, QFrame, QGridLayout, QMessageBox, QGraphicsView, QGraphicsScene)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QThread, pyqtSlot, QRectF, QPointF
from PyQt5.QtGui import QFont, QPixmap, QPainter, QColor, QPen, QBrush, QPolygonF
import json
import datetime
import logging
import math

class SimpleMapWidget(QWidget):
    """Basit harita widget'ı - PyQt5 Graphics View kullanarak"""
    
    # Sinyaller
    coordinate_clicked = pyqtSignal(float, float)  # lat, lon
    command_executed = pyqtSignal(str)  # komut adı
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.markers = []  # Harita işaretleyicileri
        self.waypoints = []  # Waypoint'ler
        self.mission_active = False
        self.current_position = (39.9334, 32.8597)  # Ankara koordinatları (varsayılan)
        self.zoom_level = 1.0
        self.pan_offset = QPointF(0, 0)
        
        self.setup_ui()
        self.setup_logging()
        self.create_simple_map()
        
    def setup_ui(self):
        """Arayüz bileşenlerini oluştur"""
        layout = QVBoxLayout(self)
        
        # Üst panel - Komut butonları
        self.create_command_panel(layout)
        
        # Ana harita alanı
        self.create_simple_map_area(layout)
        
        # Alt panel - Koordinat gösterimi ve log
        self.create_info_panel(layout)
        
    def create_command_panel(self, parent_layout):
        """Komut butonları panelini oluştur"""
        command_frame = QFrame()
        command_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(22, 25, 29, 220);
                border-radius: 15px;
                margin: 5px;
            }
        """)
        
        command_layout = QHBoxLayout(command_frame)
        
        # Komut butonları
        self.btn_takeoff = QPushButton("🚁 Kalkış")
        self.btn_landing = QPushButton("🛬 İniş")
        self.btn_waypoint = QPushButton("📍 Waypoint Ekle")
        self.btn_mission = QPushButton("🎯 Mission Başlat")
        self.btn_emergency = QPushButton("🚨 Acil Durdur")
        
        # Buton stilleri
        button_style = """
            QPushButton {
                background-color: #2c3e50;
                color: white;
                border: 2px solid #34495e;
                border-radius: 8px;
                padding: 10px 15px;
                font-size: 12px;
                font-weight: bold;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #34495e;
                border-color: #3498db;
            }
            QPushButton:pressed {
                background-color: #1abc9c;
            }
        """
        
        emergency_style = """
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: 2px solid #c0392b;
                border-radius: 8px;
                padding: 10px 15px;
                font-size: 12px;
                font-weight: bold;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #c0392b;
                border-color: #e74c3c;
            }
            QPushButton:pressed {
                background-color: #a93226;
            }
        """
        
        self.btn_takeoff.setStyleSheet(button_style)
        self.btn_landing.setStyleSheet(button_style)
        self.btn_waypoint.setStyleSheet(button_style)
        self.btn_mission.setStyleSheet(button_style)
        self.btn_emergency.setStyleSheet(emergency_style)
        
        # Buton bağlantıları
        self.btn_takeoff.clicked.connect(lambda: self.execute_command("Kalkış"))
        self.btn_landing.clicked.connect(lambda: self.execute_command("İniş"))
        self.btn_waypoint.clicked.connect(lambda: self.execute_command("Waypoint Ekle"))
        self.btn_mission.clicked.connect(lambda: self.execute_command("Mission Başlat"))
        self.btn_emergency.clicked.connect(lambda: self.execute_command("Acil Durdur"))
        
        # Butonları layout'a ekle
        command_layout.addWidget(self.btn_takeoff)
        command_layout.addWidget(self.btn_landing)
        command_layout.addWidget(self.btn_waypoint)
        command_layout.addWidget(self.btn_mission)
        command_layout.addWidget(self.btn_emergency)
        
        parent_layout.addWidget(command_frame)
        
    def create_simple_map_area(self, parent_layout):
        """Basit harita alanını oluştur"""
        map_frame = QFrame()
        map_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(22, 25, 29, 220);
                border-radius: 15px;
                margin: 5px;
            }
        """)
        
        map_layout = QHBoxLayout(map_frame)
        
        # Graphics View için harita
        self.map_view = QGraphicsView()
        self.map_view.setMinimumHeight(400)
        self.map_view.setStyleSheet("""
            QGraphicsView {
                background-color: #2c3e50;
                border: 2px solid #34495e;
                border-radius: 10px;
            }
        """)
        
        # Graphics Scene oluştur
        self.map_scene = QGraphicsScene()
        self.map_view.setScene(self.map_scene)
        
        # Mouse olaylarını bağla
        self.map_view.mousePressEvent = self.on_map_clicked
        
        map_layout.addWidget(self.map_view)
        
        parent_layout.addWidget(map_frame)
        
    def create_info_panel(self, parent_layout):
        """Bilgi panelini oluştur (koordinatlar ve log)"""
        info_frame = QFrame()
        info_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(22, 25, 29, 220);
                border-radius: 15px;
                margin: 5px;
            }
        """)
        
        info_layout = QHBoxLayout(info_frame)
        
        # Sol taraf - Koordinat bilgileri
        coord_frame = QFrame()
        coord_layout = QVBoxLayout(coord_frame)
        
        self.coord_label = QLabel("GPS Koordinatları:")
        self.coord_label.setStyleSheet("color: white; font-weight: bold; font-size: 14px;")
        
        self.lat_label = QLabel("Enlem: --")
        self.lon_label = QLabel("Boylam: --")
        self.alt_label = QLabel("Yükseklik: --")
        
        coord_style = "color: #3498db; font-size: 12px; margin: 2px;"
        self.lat_label.setStyleSheet(coord_style)
        self.lon_label.setStyleSheet(coord_style)
        self.alt_label.setStyleSheet(coord_style)
        
        coord_layout.addWidget(self.coord_label)
        coord_layout.addWidget(self.lat_label)
        coord_layout.addWidget(self.lon_label)
        coord_layout.addWidget(self.alt_label)
        
        # Sağ taraf - Log alanı
        log_frame = QFrame()
        log_layout = QVBoxLayout(log_frame)
        
        log_title = QLabel("Sistem Logları:")
        log_title.setStyleSheet("color: white; font-weight: bold; font-size: 14px;")
        
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(150)
        self.log_text.setStyleSheet("""
            QTextEdit {
                background-color: #2c3e50;
                color: #ecf0f1;
                border: 1px solid #34495e;
                border-radius: 5px;
                font-family: 'Courier New', monospace;
                font-size: 10px;
            }
        """)
        self.log_text.setReadOnly(True)
        
        log_layout.addWidget(log_title)
        log_layout.addWidget(self.log_text)
        
        info_layout.addWidget(coord_frame)
        info_layout.addWidget(log_frame)
        
        parent_layout.addWidget(info_frame)
        
    def setup_logging(self):
        """Log sistemi kurulumu"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/map_operations.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def create_simple_map(self):
        """Basit harita oluştur"""
        try:
            # Harita arka planını çiz
            self.draw_map_background()
            
            # Merkez noktasını işaretle
            self.add_center_marker()
            
            self.log_message("Basit harita başarıyla oluşturuldu")
            
        except Exception as e:
            self.log_message(f"Harita oluşturma hatası: {str(e)}", "ERROR")
            
    def draw_map_background(self):
        """Harita arka planını çiz"""
        # Grid çizgileri ekle
        pen = QPen(QColor(100, 100, 100), 1)
        
        # Dikey çizgiler
        for i in range(0, 800, 50):
            self.map_scene.addLine(i, 0, i, 600, pen)
            
        # Yatay çizgiler  
        for i in range(0, 600, 50):
            self.map_scene.addLine(0, i, 800, i, pen)
            
        # Merkez çizgileri (kalın)
        center_pen = QPen(QColor(200, 200, 200), 2)
        self.map_scene.addLine(400, 0, 400, 600, center_pen)
        self.map_scene.addLine(0, 300, 800, 300, center_pen)
        
    def add_center_marker(self):
        """Merkez noktasını işaretle"""
        # Merkez noktası (Ankara koordinatları)
        center_x, center_y = 400, 300
        
        # Merkez işareti
        center_pen = QPen(QColor(255, 0, 0), 3)
        center_brush = QBrush(QColor(255, 0, 0))
        
        # Daire çiz
        self.map_scene.addEllipse(center_x - 5, center_y - 5, 10, 10, center_pen, center_brush)
        
        # Koordinat etiketi
        text_item = self.map_scene.addText("Ankara\n39.9334°N, 32.8597°E")
        text_item.setPos(center_x + 10, center_y - 20)
        text_item.setDefaultTextColor(QColor(255, 255, 255))
        
    def on_map_clicked(self, event):
        """Harita tıklama olayı"""
        if event.button() == Qt.LeftButton:
            # Tıklanan pozisyonu al
            scene_pos = self.map_view.mapToScene(event.pos())
            x, y = scene_pos.x(), scene_pos.y()
            
            # Koordinatları hesapla (basit dönüşüm)
            # Merkez noktası: 400, 300 (Ankara)
            # 1 piksel ≈ 0.001 derece (yaklaşık)
            lat_offset = (300 - y) * 0.001
            lon_offset = (x - 400) * 0.001
            
            lat = 39.9334 + lat_offset
            lon = 32.8597 + lon_offset
            
            # Koordinatları güncelle
            self.update_coordinates(lat, lon)
            self.coordinate_clicked.emit(lat, lon)
            self.log_message(f"Harita tıklandı: ({lat:.6f}, {lon:.6f})")
            
            # Tıklanan yere marker ekle
            self.add_click_marker(x, y, lat, lon)
            
    def execute_command(self, command):
        """Komut çalıştır"""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        
        if command == "Kalkış":
            self.log_message(f"[{timestamp}] Kalkış komutu çalıştırıldı")
            self.command_executed.emit("TAKEOFF")
            
        elif command == "İniş":
            self.log_message(f"[{timestamp}] İniş komutu çalıştırıldı")
            self.command_executed.emit("LANDING")
            
        elif command == "Waypoint Ekle":
            self.log_message(f"[{timestamp}] Waypoint ekleme modu aktif")
            self.command_executed.emit("ADD_WAYPOINT")
            
        elif command == "Mission Başlat":
            self.mission_active = True
            self.log_message(f"[{timestamp}] Mission başlatıldı")
            self.command_executed.emit("START_MISSION")
            
        elif command == "Acil Durdur":
            self.mission_active = False
            self.log_message(f"[{timestamp}] ACİL DURDUR - Tüm operasyonlar durduruldu!", "ERROR")
            self.command_executed.emit("EMERGENCY_STOP")
            
        # Terminal/console'a bildirim gönder
        print(f"[{timestamp}] Komut çalıştırıldı: {command}")
        
    def add_click_marker(self, x, y, lat, lon):
        """Tıklanan yere marker ekle"""
        try:
            # Marker çiz
            marker_pen = QPen(QColor(0, 255, 0), 2)
            marker_brush = QBrush(QColor(0, 255, 0))
            
            # Daire marker
            self.map_scene.addEllipse(x - 8, y - 8, 16, 16, marker_pen, marker_brush)
            
            # Koordinat etiketi
            text_item = self.map_scene.addText(f"WP{len(self.markers)+1}\n{lat:.4f}°N\n{lon:.4f}°E")
            text_item.setPos(x + 10, y - 20)
            text_item.setDefaultTextColor(QColor(0, 255, 0))
            
            # Marker'ı listeye ekle
            self.markers.append((lat, lon, f"WP{len(self.markers)+1}"))
            
            self.log_message(f"Marker eklendi: WP{len(self.markers)} ({lat:.6f}, {lon:.6f})")
            
        except Exception as e:
            self.log_message(f"Marker ekleme hatası: {str(e)}", "ERROR")
            
    def add_marker(self, lat, lon, title="Marker"):
        """Haritaya marker ekle"""
        try:
            # Koordinatları piksel koordinatlarına çevir
            x = 400 + (lon - 32.8597) * 1000  # Yaklaşık dönüşüm
            y = 300 - (lat - 39.9334) * 1000
            
            # Marker çiz
            marker_pen = QPen(QColor(255, 255, 0), 2)
            marker_brush = QBrush(QColor(255, 255, 0))
            
            # Daire marker
            self.map_scene.addEllipse(x - 8, y - 8, 16, 16, marker_pen, marker_brush)
            
            # Koordinat etiketi
            text_item = self.map_scene.addText(f"{title}\n{lat:.4f}°N\n{lon:.4f}°E")
            text_item.setPos(x + 10, y - 20)
            text_item.setDefaultTextColor(QColor(255, 255, 0))
            
            # Marker'ı listeye ekle
            self.markers.append((lat, lon, title))
            
            self.log_message(f"Marker eklendi: {title} ({lat:.6f}, {lon:.6f})")
            
        except Exception as e:
            self.log_message(f"Marker ekleme hatası: {str(e)}", "ERROR")
            
    def remove_marker(self, lat, lon):
        """Haritadan marker kaldır"""
        try:
            # Marker'ı listeden kaldır
            self.markers = [(m_lat, m_lon, m_title) for m_lat, m_lon, m_title in self.markers 
                           if not (abs(m_lat - lat) < 0.0001 and abs(m_lon - lon) < 0.0001)]
            
            # Haritayı yenile
            self.refresh_simple_map()
            
            self.log_message(f"Marker kaldırıldı: ({lat:.6f}, {lon:.6f})")
            
        except Exception as e:
            self.log_message(f"Marker kaldırma hatası: {str(e)}", "ERROR")
            
    def refresh_simple_map(self):
        """Basit haritayı yenile"""
        try:
            # Scene'i temizle
            self.map_scene.clear()
            
            # Arka planı yeniden çiz
            self.draw_map_background()
            self.add_center_marker()
            
            # Mevcut marker'ları yeniden ekle
            for lat, lon, title in self.markers:
                self.add_marker(lat, lon, title)
            
        except Exception as e:
            self.log_message(f"Harita yenileme hatası: {str(e)}", "ERROR")
            
    def update_coordinates(self, lat, lon, alt=0):
        """GPS koordinatlarını güncelle"""
        self.current_position = (lat, lon)
        self.lat_label.setText(f"Enlem: {lat:.6f}°")
        self.lon_label.setText(f"Boylam: {lon:.6f}°")
        self.alt_label.setText(f"Yükseklik: {alt:.1f} m")
        
    def on_map_clicked_coordinate(self, lat, lon):
        """Harita tıklama olayı (koordinat ile)"""
        self.update_coordinates(lat, lon)
        self.coordinate_clicked.emit(lat, lon)
        self.log_message(f"Harita tıklandı: ({lat:.6f}, {lon:.6f})")
        
    def log_message(self, message, level="INFO"):
        """Log mesajı ekle"""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {level}: {message}"
        
        # Log text widget'ına ekle
        self.log_text.append(log_entry)
        
        # Scroll'u en alta taşı
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
        
        # Dosyaya da yaz
        self.logger.info(message)
        
    def get_waypoints(self):
        """Waypoint listesini döndür"""
        return self.waypoints
        
    def clear_waypoints(self):
        """Tüm waypoint'leri temizle"""
        self.waypoints.clear()
        self.markers.clear()
        self.refresh_simple_map()
        self.log_message("Tüm waypoint'ler temizlendi")


# MapWidget için alias oluştur (geriye uyumluluk için)
MapWidget = SimpleMapWidget
