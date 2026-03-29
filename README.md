# 🎥 YS Video Downloader v2.8

![GitHub release](https://img.shields.io/github/v/release/ysonmezer/ysvdown?style=flat-square)
![License](https://img.shields.io/badge/license-MIT-blue.svg?style=flat-square)
![Python](https://img.shields.io/badge/python-3.8+-yellow.svg?style=flat-square)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg?style=flat-square)

Çeşitli video barındırma platformlarından medya içeriklerini kaydetmek için geliştirilmiş, **yt-dlp** tabanlı, açık kaynaklı masaüstü uygulaması.

![Screenshot](https://via.placeholder.com/800x500/0078D7/FFFFFF?text=YS+Video+Downloader+v2.8)
<!-- Yukarıdaki resmi kendi screenshot'ınızla değiştirin -->

---

## 📝 **Değişiklik Geçmişi**

### **v2.8** (2026-03-26)
#### 🚀 Yeni Özellikler
- **🍎 macOS UI İyileştirmesi:** Native buton görünümü, platform renk dili uyumu
- **🔤 Font İyileştirmesi:** macOS'ta okunabilirlik için büyütülmüş font boyutları
- **📁 Yeni Klasör Yapısı:** Platform dosyaları ayrı klasörlerde (`windows/`, `macos/`)

#### 🔧 İyileştirmeler
- `ffmpeg_kontrol()` platform-agnostic hale getirildi
- `dosya_yolu_bul()` yeni klasör yapısını destekliyor
- `ikon_yukle()` frozen/script mod ayrımı eklendi

---

### **v2.7** (2026-03-19)
#### 🚀 Yeni Özellikler
- **🔔 Akıllı Güncelleme Uyarısı:** Tekrarlayan hatalar yt-dlp güncelleme önerisi gösterir
- **📊 Versiyon Kontrolü:** Footer'dan yt-dlp sürüm kontrolü
- **🎯 Hata Tespiti:** Platform değişikliklerini otomatik algılar

#### 🔧 İyileştirmeler
- Daha akıllı hata yönetimi
- Kullanıcı bildirimleri iyileştirildi

---

### **v2.6** (2026-03-14)
#### 🚀 Yeni Özellikler
- Windows Defender optimizasyonu (false positive %70 ↓)
- Dinamik playlist desteği
- Platform bağımsızlığı (Windows/macOS/Linux)
- İçerik oluşturucu adı ile otomatik klasörleme
- Otomatik geçici dosya temizleme
- Gelişmiş iptal mekanizması (custom logger)

#### 🔧 İyileştirmeler
- Thread-safe UI güncellemeleri
- Bağımlılık varlık kontrolü
- Kayıt yeri doğrulama
- Güvenli dosya değiştirme
- Footer'da minimal güncelleme linki

---

### **v2.5** (2026-01-15)
- Turbo Analiz (playlist tarama %300 hız artışı)
- Akıllı arayüz (yeşil playlist bildirimi)
- UI düzenlemeleri (simetrik butonlar)
- Hata düzeltmeleri

---

### 🎯 **Genel Özellikler**
- ✅ Tek video veya tüm playlist indirme
- ✅ Video (MP4) veya sadece ses (MP3) seçeneği
- ✅ 720p, 1080p, 4K kalite seçenekleri
- ✅ 4K VP9 videolar için otomatik H.264 dönüştürme
- ✅ Akıllı playlist analizi (%300 hız artışı)
- ✅ İndirme ilerlemesi takibi
- ✅ Detaylı işlem kayıtları

---

## 🌐 **Desteklenen Platformlar**

Bu uygulama [yt-dlp](https://github.com/yt-dlp/yt-dlp) kütüphanesini kullanır ve **1000+ video platformunu** destekler.

**Popüler platformlar arasında:** Video paylaşım siteleri, eğitim platformları, sosyal medya, podcast servisleri, canlı yayın platformları ve daha fazlası.

Desteklenen platformların tam listesi için: [yt-dlp siteler listesi](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md)

---

## 📥 **Kurulum ve Kullanım**

### **Son Kullanıcılar İçin (Portable - Kurulum Gerektirmez)**

#### Windows
1. **[Releases](https://github.com/ysonmezer/ysvdown/releases/latest)** sayfasından `ysvdown_v2.8_windows_portable.zip` dosyasını indirin
2. ZIP dosyasını istediğiniz bir klasöre çıkartın
3. `YS Video Downloader v2.8.exe` dosyasını çalıştırın

**⚠️ Önemli:** Tüm dosyaları klasör içinde tutun!
```
📂 YS Video Downloader v2.8/
 ┣ 📜 YS Video Downloader v2.8.exe  ← Bunu çalıştırın
 ┣ ⚙️ ffmpeg.exe                    ← Gerekli
 ┣ 🖼️ logo.ico                      ← Gerekli
 ┗ 📂 _internal/                    ← Gerekli
```

#### macOS
1. **[Releases](https://github.com/ysonmezer/ysvdown/releases/latest)** sayfasından `ysvdown_v2.8_macos.dmg` dosyasını indirin
2. DMG dosyasını açın, `YS Video Downloader.app` dosyasını `Applications` klasörüne sürükleyin
3. İlk açılışta: Sağ tıklayın → **Aç** → **Aç** (Gatekeeper uyarısını geçmek için)

---

### **Geliştiriciler İçin (Kaynak Kod)**

#### Gereksinimler
- Python 3.8 veya üzeri
- pip paket yöneticisi

#### Kurulum
```bash
# 1. Depoyu klonlayın
git clone https://github.com/ysonmezer/ysvdown.git
cd ysvdown

# 2. Gerekli kütüphaneleri yükleyin
pip install -r requirements.txt

# 3. Uygulamayı çalıştırın
python main.py
```

#### Build — Windows (PowerShell)
```powershell
# Önce bir kez: build çıktıları için OneDrive dışında klasör oluştur
mkdir C:\ysvdown_builds\windows

cd windows

# 1. Temizlik
Remove-Item -Recurse -Force build, dist -ErrorAction SilentlyContinue

# 2. main.py'yi kopyala (symlink değil)
Copy-Item ..\main.py .

# 3. Build
pyinstaller ysvdown.spec `
  --distpath C:\ysvdown_builds\windows\dist `
  --workpath C:\ysvdown_builds\windows\build

# 4. FFmpeg ve logo kopyala
Copy-Item ffmpeg.exe "C:\ysvdown_builds\windows\dist\YS Video Downloader v2.8\"
Copy-Item logo.ico "C:\ysvdown_builds\windows\dist\YS Video Downloader v2.8\"

# 5. ZIP oluştur
cd C:\ysvdown_builds\windows\dist
Compress-Archive -Path "YS Video Downloader v2.8" `
  -DestinationPath "ysvdown_v2.8_windows_portable.zip" -Force

# 6. Hash
Get-FileHash ysvdown_v2.8_windows_portable.zip -Algorithm SHA256

# 7. Temizlik
cd ..\..\..
Remove-Item windows\main.py
```

#### Build — macOS (Terminal)
```bash
# Önce bir kez: build çıktıları için OneDrive dışında klasör oluştur
mkdir -p ~/ysvdown_builds/macos

cd macos

# 1. Temizlik
rm -rf ~/ysvdown_builds/macos/*
rm -rf build

# 2. ffmpeg izinleri (ilk kullanımda zorunlu)
xattr -d com.apple.quarantine ffmpeg 2>/dev/null
chmod +x ffmpeg

# 3. main.py'yi kopyala (symlink değil)
cp ../main.py .

# 4. Build (--no-strip zorunlu!)
/usr/local/opt/python@3.11/bin/python3.11 setup.py py2app --no-strip \
  --dist-dir ~/ysvdown_builds/macos/dist

# 5. ffmpeg kopyala
cp ffmpeg ~/ysvdown_builds/macos/dist/YS\ Video\ Downloader.app/Contents/MacOS/

# 6. build ve main.py temizle
rm -rf build
rm main.py

# 7. DMG oluştur
hdiutil create -volname "YS Video Downloader v2.8" \
  -srcfolder ~/ysvdown_builds/macos/dist/"YS Video Downloader.app" \
  -ov -format UDZO \
  ~/ysvdown_builds/macos/ysvdown_v2.8_macos.dmg

# 8. Hash
shasum -a 256 ~/ysvdown_builds/macos/ysvdown_v2.8_macos.dmg
```

# 7. Temizlik
rm main.py
```

---

## 🛡️ **Windows Defender Uyarısı**

İlk çalıştırmada Windows Defender uyarı verebilir (False Positive). Bu durum PyInstaller ile paketlenmiş Python uygulamalarında yaygındır.

### **Çözüm Yöntemleri:**

#### **Geçici Çözüm:**
1. Windows Security → Virus & threat protection
2. Protection history → İlgili uyarıyı bulun
3. Actions → **Allow**

#### **Kalıcı Çözüm:**
1. Windows Security → Virus & threat protection
2. Manage settings → Exclusions
3. Add an exclusion → **Folder**
4. Program klasörünü seçin

### **Güvenlik Kontrolü:**
- ✅ **Açık Kaynak:** Tüm kaynak kod [GitHub'da](https://github.com/ysonmezer/ysvdown) incelenebilir
- ✅ **VirusTotal Taraması:** [Sonuçları görüntüle](#) *(Release sonrası eklenecek)*
- ✅ **SHA-256 Hash:** Release notlarında mevcuttur

**Neden oluyor?**
- PyInstaller bootloader imzası bazı antivirüsler tarafından şüpheli görülebilir
- yt-dlp'nin çok sayıda ağ bağlantısı açması
- Bu %100 güvenli, açık kaynak bir projedir

---

## 📖 **Kullanım Kılavuzu**

### **1. Tek Video İndirme**
1. Video linkini kopyalayın (desteklenen herhangi bir platformdan)
2. "Video Linki" alanına yapıştırın
3. Format seçin (Video veya MP3)
4. Kalite seçin (720p, 1080p, 4K)
5. "İNDİRMEYİ BAŞLAT" butonuna tıklayın

### **2. Playlist İndirme**
1. Playlist linkini yapıştırın
2. Program otomatik algılayacak
3. İki seçenek sunulur:
   - **VİDEOYU İNDİR:** Sadece o videoyu indir
   - **TÜM LİSTEYİ İNDİR:** Tüm playlist'i indir

### **3. İptal Etme**
İndirme sırasında "İPTAL ET" butonuna basarak işlemi durdurabilirsiniz. Program geçici dosyaları otomatik temizler.

---

## 🔧 **Teknik Detaylar**

### **Mimari**
- **GUI Framework:** Tkinter
- **Video İndirme:** yt-dlp
- **Video İşleme:** FFmpeg
- **Build Tool:** PyInstaller (Windows) / py2app (macOS)
- **Programlama Dili:** Python 3.11

### **Güvenlik Özellikleri**
- Static import (Defender bypass)
- Bağlantı limitleri (spam önleme)
- Thread-safe UI güncellemeleri
- Güvenli dosya işlemleri (veri kaybı önleme)

### **Performans İyileştirmeleri**
- Turbo playlist analizi (%300 hız artışı)
- Asenkron indirme işlemleri
- Minimal bellek kullanımı

---

## ⚠️ **Yasal Uyarı**

Bu yazılım **eğitim ve kişisel arşivleme** amaçlıdır.

- Telif hakkı ile korunan materyallerin izinsiz indirilmesi yasalara aykırıdır
- İçerik oluşturucuların haklarına saygı gösterin
- Kullandığınız platformların hizmet şartlarına uyun

**Kullanıcı bu yazılımı kullanarak tüm sorumlulukları kabul eder.**

---

## 🐛 **Bilinen Sorunlar ve Çözümler**

### **1. "FFmpeg bulunamadı" hatası**
**Çözüm:** FFmpeg dosyasının program klasöründe olduğundan emin olun.

### **2. "Kayıt klasörüne yazma izni yok"**
**Çözüm:** Farklı bir klasör seçin veya programı yönetici olarak çalıştırın.

### **3. Belirli bir platform çalışmıyor**
**Çözüm:** yt-dlp güncellemesi gerekebilir. Footer'daki "yt-dlp güncelle" linkini kullanın.

### **4. macOS — "Uygulama açılamıyor" uyarısı**
**Çözüm:** Sağ tıklayın → **Aç** → **Aç** (ilk açılışta bir kez yeterli).

---

## 🤝 **Katkıda Bulunma**

1. **Fork** yapın
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Değişikliklerinizi commit edin (`git commit -m 'Add amazing feature'`)
4. Branch'inizi push edin (`git push origin feature/amazing-feature`)
5. **Pull Request** açın

---

## 📄 **Lisans**

Bu proje [MIT Lisansı](LICENSE) ile lisanslanmıştır.

```
MIT License

Copyright (c) 2026 YS

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 💬 **Destek ve İletişim**

- **Sorun Bildirimi:** [Issue açın](https://github.com/ysonmezer/ysvdown/issues/new)
- **Özellik İsteği:** [Feature request](https://github.com/ysonmezer/ysvdown/issues/new?labels=enhancement)
- **GitHub:** [@ysonmezer](https://github.com/ysonmezer)

---

## 🙏 **Teşekkürler**

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - Harika video indirme kütüphanesi
- [FFmpeg](https://ffmpeg.org/) - Güçlü multimedia framework
- [PyInstaller](https://www.pyinstaller.org/) - Python uygulamalarını paketleme (Windows)
- [py2app](https://py2app.readthedocs.io/) - Python uygulamalarını paketleme (macOS)

---

<p align="center">
  <strong>Made with ❤️ by YS</strong><br>
  <sub>© 2026 YS Video Downloader. Tüm hakları saklıdır.</sub>
</p>
