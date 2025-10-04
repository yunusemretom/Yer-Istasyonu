"""
Executable dosya oluşturma script'i
PyInstaller kullanarak tek dosya executable oluşturur
"""

import os
import sys
import subprocess

def install_pyinstaller():
    """PyInstaller'ı yükle"""
    try:
        import PyInstaller
        print("PyInstaller zaten yüklü")
    except ImportError:
        print("PyInstaller yükleniyor...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

def create_executable():
    """Executable dosya oluştur"""
    print("Executable dosya oluşturuluyor...")
    
    # PyInstaller komutu
    cmd = [
        "pyinstaller",
        "--onefile",  # Tek dosya olarak
        "--windowed",  # Console penceresi gösterme
        "--name=ModernGUI",  # Executable adı
        "--icon=icons/logo.png",  # İkon (varsa)
        "--add-data=icons;icons",  # İkonları dahil et
        "--add-data=logs;logs",  # Log klasörünü dahil et
        "--hidden-import=PyQt5.QtWebEngineWidgets",
        "--hidden-import=folium",
        "--hidden-import=cv2",
        "main.py"
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print("✅ Executable başarıyla oluşturuldu!")
        print("📁 Dosya konumu: dist/ModernGUI.exe")
    except subprocess.CalledProcessError as e:
        print(f"❌ Hata: {e}")
        return False
    
    return True

def main():
    """Ana fonksiyon"""
    print("🚀 ModernGUI Executable Builder")
    print("=" * 40)
    
    # PyInstaller'ı yükle
    install_pyinstaller()
    
    # Executable oluştur
    if create_executable():
        print("\n🎉 Build tamamlandı!")
        print("📋 Sonraki adımlar:")
        print("   1. dist/ModernGUI.exe dosyasını test edin")
        print("   2. Gerekirse ikon dosyasını ekleyin")
        print("   3. Executable'ı dağıtım için hazırlayın")
    else:
        print("\n❌ Build başarısız!")
        print("🔧 Sorun giderme:")
        print("   1. Tüm gereksinimlerin yüklü olduğundan emin olun")
        print("   2. Python path'ini kontrol edin")
        print("   3. Gerekli dosyaların mevcut olduğunu kontrol edin")

if __name__ == "__main__":
    main()
