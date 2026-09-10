# ModernGUI2 - Drone/İHA Kontrol Arayüzü

Bu proje, drone/İHA operasyonları için tasarlanmış kapsamlı bir GUI arayüz programıdır. PyQt5 framework'ü kullanılarak geliştirilmiştir ve harita entegrasyonu, komut butonları ve log sistemi içerir.

## 🚀 Özellikler

### ✅ Tamamlanan Özellikler

- **5 Farklı Komut Butonu**: Kalkış, İniş, Waypoint Ekle, Mission Başlat, Acil Durdur
- **Harita Entegrasyonu**: OpenStreetMap tabanlı interaktif harita
- **GPS Koordinat Gösterimi**: Gerçek zamanlı koordinat bilgileri
- **Marker Ekleme/Çıkarma**: Harita üzerinde işaretleyici yönetimi
- **Log Sistemi**: Tüm operasyonların kayıt altına alınması
- **Terminal/Console Bildirimleri**: Komut çalıştırma bildirimleri
- **Flight Instruments**: ADI, HSI, SI göstergeleri
- **Kamera Görüntüsü**: Gerçek zamanlı video akışı

## 📋 Gereksinimler

- Python 3.7+
- PyQt5
- Folium (harita entegrasyonu için)
- OpenCV (kamera görüntüleri için)
- NumPy

## 🛠️ Kurulum

1. **Repository'yi klonlayın:**
```bash
git clone <repository-url>
cd moderngui2
```

2. **Gerekli paketleri yükleyin:**
```bash
pip install -r requirements.txt
```

3. **Uygulamayı çalıştırın:**
```bash
python main.py
```

## 🧪 Test

Uygulamayı test etmek için:
```bash
python test_gui.py
```

## 📦 Executable Oluşturma

Tek dosya executable oluşturmak için:
```bash
python build_executable.py
```

## 📖 Kullanım

Detaylı kullanım bilgileri için [KULLANIM_KILAVUZU.md](KULLANIM_KILAVUZU.md) dosyasını inceleyin.

### Hızlı Başlangıç

1. Uygulamayı başlatın
2. Sol menüden "Maps" butonuna tıklayın
3. Harita üzerinde istediğiniz yere tıklayarak koordinatları görün
4. Komut butonlarını kullanarak drone operasyonlarını simüle edin

## 🗂️ Proje Yapısı

```
moderngui2/
├── main.py                 # Ana uygulama dosyası
├── map_widget.py          # Harita widget'ı
├── sidebar.py             # Sidebar arayüzü
├── arayuz.py              # PFD (Primary Flight Display)
├── requirements.txt       # Python paket gereksinimleri
├── KULLANIM_KILAVUZU.md   # Detaylı kullanım kılavuzu
├── test_gui.py           # Test script'i
├── build_executable.py   # Executable oluşturma script'i
├── logs/                 # Log dosyaları
│   └── map_operations.log
└── icons/                # İkon dosyaları
```

## 🎯 Komut Butonları

- **🚁 Kalkış**: Drone'u kalkışa hazırlar
- **🛬 İniş**: Drone'u güvenli inişe yönlendirir
- **📍 Waypoint Ekle**: Harita üzerinde waypoint ekleme modunu aktifleştirir
- **🎯 Mission Başlat**: Önceden tanımlanmış görevi başlatır
- **🚨 Acil Durdur**: Tüm operasyonları acil durdurur

## 🗺️ Harita Özellikleri

- PyQt5 Graphics View tabanlı basit harita
- GPS koordinat gösterimi
- Marker ekleme/çıkarma
- Harita tıklama ile koordinat alma
- Gerçek zamanlı log sistemi
- Grid tabanlı koordinat sistemi

## 📊 Log Sistemi

- Tüm komut çalıştırmaları otomatik loglanır
- Loglar hem ekranda hem de dosyada saklanır
- Zaman damgalı log girişleri
- Hata ve bilgi mesajları ayrımı

## 🔧 Teknik Detaylar

### Framework ve Teknolojiler

- **GUI Framework**: PyQt5
- **Harita**: Basit Graphics View haritası (PyQt5 Graphics Scene)
- **Log Sistemi**: Python logging modülü
- **Koordinat Sistemi**: WGS84 (GPS standardı)
- **Video**: OpenCV

### Koordinat Sistemi

- **Enlem (Latitude)**: -90° ile +90° arası
- **Boylam (Longitude)**: -180° ile +180° arası
- **Yükseklik**: Metre cinsinden (deniz seviyesinden)

## 🐛 Sorun Giderme

### Yaygın Sorunlar

1. **Harita Yüklenmiyor**
   - İnternet bağlantınızı kontrol edin
   - PyQtWebEngine paketinin yüklü olduğundan emin olun

2. **Komut Butonları Çalışmıyor**
   - Console çıktısını kontrol edin
   - Log dosyalarını inceleyin

3. **Koordinatlar Görünmüyor**
   - Harita üzerinde bir yere tıkladığınızdan emin olun

## 📝 Lisans

Bu proje eğitim amaçlı geliştirilmiştir.

## 🤝 Katkıda Bulunma

1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/AmazingFeature`)
3. Commit yapın (`git commit -m 'Add some AmazingFeature'`)
4. Push yapın (`git push origin feature/AmazingFeature`)
5. Pull Request oluşturun

## 📞 İletişim

Proje hakkında sorularınız için:
- GitHub Issues kullanın
- E-posta ile iletişime geçin

---

**⚠️ Önemli Not**: Bu program drone/İHA operasyonları için tasarlanmıştır. Gerçek uçuşlarda kullanmadan önce gerekli güvenlik önlemlerini alın ve yerel yasalara uygun hareket edin.

## 🎉 Teşekkürler

Bu projeyi geliştirirken kullanılan açık kaynak kütüphanelere teşekkürler:
- PyQt5
- OpenCV
- NumPy
- Python Standard Library