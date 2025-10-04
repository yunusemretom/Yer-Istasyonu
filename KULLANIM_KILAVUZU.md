# GUI Arayüz Programı - Kullanım Kılavuzu

## Proje Hakkında

Bu proje, drone/İHA operasyonları için tasarlanmış kapsamlı bir GUI arayüz programıdır. PyQt5 framework'ü kullanılarak geliştirilmiştir ve harita entegrasyonu, komut butonları ve log sistemi içerir.

## Özellikler

### ✅ Tamamlanan Özellikler

- **5 Farklı Komut Butonu**: Kalkış, İniş, Waypoint Ekle, Mission Başlat, Acil Durdur
- **Harita Entegrasyonu**: OpenStreetMap tabanlı interaktif harita
- **GPS Koordinat Gösterimi**: Gerçek zamanlı koordinat bilgileri
- **Marker Ekleme/Çıkarma**: Harita üzerinde işaretleyici yönetimi
- **Log Sistemi**: Tüm operasyonların kayıt altına alınması
- **Terminal/Console Bildirimleri**: Komut çalıştırma bildirimleri

## Kurulum

### Gereksinimler

- Python 3.7+
- PyQt5
- Folium (harita entegrasyonu için)
- OpenCV (kamera görüntüleri için)
- NumPy

### Kurulum Adımları

1. **Gerekli paketleri yükleyin:**
```bash
pip install -r requirements.txt
```

2. **Projeyi çalıştırın:**
```bash
python main.py
```

## Kullanım

### Ana Arayüz

Program açıldığında aşağıdaki bileşenleri göreceksiniz:

1. **Sol Sidebar**: Navigasyon menüsü
2. **Ana Alan**: Seçilen sayfaya göre değişen içerik
3. **Üst Menü**: Bağlantı ayarları ve profil

### Harita Sayfası

Harita sayfasına erişmek için sol menüden "Maps" butonuna tıklayın.

#### Komut Butonları

- **🚁 Kalkış**: Drone'u kalkışa hazırlar
- **🛬 İniş**: Drone'u güvenli inişe yönlendirir
- **📍 Waypoint Ekle**: Harita üzerinde waypoint ekleme modunu aktifleştirir
- **🎯 Mission Başlat**: Önceden tanımlanmış görevi başlatır
- **🚨 Acil Durdur**: Tüm operasyonları acil durdurur

#### Harita Kullanımı

1. **Koordinat Görüntüleme**: Harita üzerinde herhangi bir yere tıklayarak o noktanın koordinatlarını görebilirsiniz
2. **Marker Ekleme**: "Waypoint Ekle" butonuna bastıktan sonra harita üzerinde istediğiniz yere tıklayarak marker ekleyebilirsiniz
3. **Marker Kaldırma**: Mevcut marker'ları kaldırmak için marker üzerine sağ tıklayın

#### Log Sistemi

- Tüm komut çalıştırmaları otomatik olarak loglanır
- Loglar hem ekranda hem de `logs/map_operations.log` dosyasında saklanır
- Her log girişi zaman damgası içerir

### Terminal Sayfası

Terminal sayfasında:
- Komut satırı arayüzü
- Sistem mesajları
- Manuel komut girişi

### Diğer Sayfalar

- **Home**: Ana kontrol paneli (ADI, HSI, SI göstergeleri)
- **Settings**: Sistem ayarları
- **Info**: Proje bilgileri
- **Help**: Yardım ve dokümantasyon

## Teknik Detaylar

### Framework ve Teknolojiler

- **GUI Framework**: PyQt5
- **Harita**: OpenStreetMap (Folium)
- **Log Sistemi**: Python logging modülü
- **Koordinat Sistemi**: WGS84 (GPS standardı)

### Dosya Yapısı

```
moderngui2/
├── main.py                 # Ana uygulama dosyası
├── map_widget.py          # Harita widget'ı
├── sidebar.py             # Sidebar arayüzü
├── arayuz.py              # PFD (Primary Flight Display)
├── requirements.txt       # Python paket gereksinimleri
├── KULLANIM_KILAVUZU.md   # Bu dosya
├── logs/                  # Log dosyaları
│   └── map_operations.log
└── temp_map.html         # Geçici harita dosyası
```

### Koordinat Sistemi

- **Enlem (Latitude)**: -90° ile +90° arası
- **Boylam (Longitude)**: -180° ile +180° arası
- **Yükseklik**: Metre cinsinden (deniz seviyesinden)

## Sorun Giderme

### Yaygın Sorunlar

1. **Harita Yüklenmiyor**
   - İnternet bağlantınızı kontrol edin
   - PyQtWebEngine paketinin yüklü olduğundan emin olun

2. **Komut Butonları Çalışmıyor**
   - Console çıktısını kontrol edin
   - Log dosyalarını inceleyin

3. **Koordinatlar Görünmüyor**
   - Harita üzerinde bir yere tıkladığınızdan emin olun
   - GPS sinyali simülasyonu için varsayılan koordinatlar kullanılır

### Log Dosyaları

Log dosyaları `logs/` klasöründe saklanır:
- `map_operations.log`: Harita ve komut operasyonları
- `custom_widgets.log`: Widget işlemleri

## Geliştirici Notları

### Kod Yapısı

- **map_widget.py**: Harita widget'ının tüm fonksiyonalitesi
- **main.py**: Ana uygulama ve widget entegrasyonu
- **sidebar.py**: UI bileşenleri (otomatik oluşturulmuş)

### Genişletme İmkanları

- Yeni komut butonları eklenebilir
- Farklı harita sağlayıcıları entegre edilebilir
- GPS veri kaynakları bağlanabilir
- Mission planlama özellikleri geliştirilebilir

## Lisans

Bu proje eğitim amaçlı geliştirilmiştir.

## İletişim

Proje hakkında sorularınız için:
- GitHub Issues kullanın
- E-posta ile iletişime geçin

---

**Not**: Bu program drone/İHA operasyonları için tasarlanmıştır. Gerçek uçuşlarda kullanmadan önce gerekli güvenlik önlemlerini alın ve yerel yasalara uygun hareket edin.
