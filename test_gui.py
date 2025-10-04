"""
GUI Arayüz Test Script'i
Temel fonksiyonaliteleri test eder
"""

import sys
import os
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import QTimer

def test_imports():
    """Gerekli modüllerin import edilebilirliğini test et"""
    print("Modul import testleri...")
    
    try:
        import PyQt5
        print("OK - PyQt5")
    except ImportError as e:
        print(f"HATA - PyQt5: {e}")
        return False
    
    # Folium artık gerekli değil (basit harita kullanıyoruz)
    print("OK - Folium (Gerekli degil)")
    
    try:
        import cv2
        print("OK - OpenCV")
    except ImportError as e:
        print(f"HATA - OpenCV: {e}")
        return False
    
    try:
        import numpy
        print("OK - NumPy")
    except ImportError as e:
        print(f"HATA - NumPy: {e}")
        return False
    
    return True

def test_map_widget():
    """MapWidget'ın çalışabilirliğini test et"""
    print("\nMapWidget testi...")
    
    try:
        from map_widget import MapWidget
        print("OK - MapWidget import")
        
        # Widget oluşturma testi
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        widget = MapWidget()
        print("OK - MapWidget olusturma")
        
        # Temel fonksiyonları test et
        widget.update_coordinates(39.9334, 32.8597, 100)
        print("OK - Koordinat guncelleme")
        
        widget.log_message("Test mesaji")
        print("OK - Log sistemi")
        
        # Marker ekleme testi
        widget.add_marker(39.9334, 32.8597, "Test Marker")
        print("OK - Marker ekleme")
        
        return True
        
    except Exception as e:
        print(f"HATA - MapWidget testi: {e}")
        return False

def test_main_app():
    """Ana uygulamanın çalışabilirliğini test et"""
    print("\nAna uygulama testi...")
    
    try:
        # Ana modülü import et
        import main
        print("OK - Ana modul import")
        
        return True
        
    except Exception as e:
        print(f"HATA - Ana uygulama testi: {e}")
        return False

def test_file_structure():
    """Dosya yapısını kontrol et"""
    print("\nDosya yapisi kontrolu...")
    
    required_files = [
        "main.py",
        "map_widget.py", 
        "sidebar.py",
        "requirements.txt",
        "KULLANIM_KILAVUZU.md"
    ]
    
    missing_files = []
    for file in required_files:
        if os.path.exists(file):
            print(f"OK - {file}")
        else:
            print(f"EKSIK - {file}")
            missing_files.append(file)
    
    # Logs klasörünü kontrol et
    if not os.path.exists("logs"):
        print("logs klasoru olusturuluyor...")
        os.makedirs("logs")
        print("OK - logs klasoru")
    else:
        print("OK - logs klasoru")
    
    return len(missing_files) == 0

def run_gui_test():
    """GUI'yi kısa süre çalıştırarak test et"""
    print("\nGUI calistirma testi...")
    
    try:
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        # Ana pencereyi oluştur
        from main import MainWindow
        window = MainWindow()
        window.show()
        
        print("OK - GUI baslatma")
        
        # 2 saniye bekle ve kapat
        QTimer.singleShot(2000, app.quit)
        app.exec_()
        
        print("OK - GUI kapatma")
        return True
        
    except Exception as e:
        print(f"HATA - GUI testi: {e}")
        return False

def main():
    """Ana test fonksiyonu"""
    print("ModernGUI Test Suite")
    print("=" * 50)
    
    tests = [
        ("Dosya Yapısı", test_file_structure),
        ("Modül Import", test_imports),
        ("MapWidget", test_map_widget),
        ("Ana Uygulama", test_main_app),
        ("GUI Çalıştırma", run_gui_test)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_func():
                passed += 1
                print(f"BASARILI - {test_name}")
            else:
                print(f"BASARISIZ - {test_name}")
        except Exception as e:
            print(f"HATA - {test_name}: {e}")
    
    print(f"\n{'='*50}")
    print(f"Test Sonuclari: {passed}/{total} basarili")
    
    if passed == total:
        print("Tum testler basarili! Uygulama calismaya hazir.")
        return True
    else:
        print("Bazi testler basarisiz. Lutfen hatalari kontrol edin.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
