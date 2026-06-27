# 🎥 YS Video Downloader v3.0

![GitHub release](https://img.shields.io/github/v/release/ysonmezer/ysvdown?style=flat-square)
![License](https://img.shields.io/badge/license-MIT-blue.svg?style=flat-square)
![Python](https://img.shields.io/badge/python-3.8+-yellow.svg?style=flat-square)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg?style=flat-square)

Çeşitli video barındırma platformlarından medya içeriklerini kaydetmek için geliştirilmiş, **yt-dlp** tabanlı, açık kaynaklı masaüstü uygulaması.

![Screenshot](https://via.placeholder.com/800x500/0078D7/FFFFFF?text=YS+Video+Downloader+v3.0)
<!-- Yukarıdaki resmi kendi screenshot'ınızla değiştirin -->

---

## 📝 **Değişiklik Geçmişi**

### **v3.0** (2026-06-09)
#### 🔧 Düzeltmeler
- **🐛 Bug Fix:** Windows'ta Masaüstü klasörü farklı bir sürücüye taşınmış kullanıcılarda kayıt yeri artık doğru algılanıyor (registry-based Desktop path)

#### ⬆️ Güncellemeler
- **yt-dlp 2026.03.17** ile güncellendi

---

### **v2.9** (2026-05-21)
#### 🔧 Düzeltmeler
- **🐛 Bug Fix:** `analiz_thread` içindeki çift `except` bloğu düzeltildi (ikinci blok hiç çalışmıyordu, analiz hataları kullanıcıya gösterilmiyordu)
- **🐛 Bug Fix:** `lambda` closure bug'ı düzeltildi (`lambda msg=hata_mesaji:` ile sabitlendi)

#### 🚀 Yeni Özellikler
- **🎵 MP3 Dönüştürme UX:** MP3 indirirken FFmpeg dönüştürme aşaması artık kullanıcıya gösteriliyor. Dönüştürme başlarken turuncu buton + indeterminate progress + log mesajı çıkıyor. Uygulama donmadı, işlem devam ediyor.

---

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
- ✅ MP3 dönüştürme ilerleme bildirimi

---

## 🌐 **Desteklenen Platformlar**

Bu uygulama [yt-dlp](https://github.com/yt-dlp/yt-dlp) kütüphanesini kullanır ve **1000+ video platformunu** destekler.

**Popüler platformlar arasında:** Video paylaşım siteleri, eğitim platformları, sosyal medya, podcast servisleri, canlı yayın platformları ve daha fazlası.

Desteklenen platformların tam listesi için: [yt-dlp siteler listesi](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md)

---

## 📥 **Kurulum ve Kullanım**

### **Son Kullanıcılar İçin (Portable - Kurulum Gerektirmez)**

#### Windows
1. **[Releases](https://github.com/ysonmezer/ysvdown/releases/latest)** sayfasından `ysvdown_v3.0_windows_portable.zip` dosyasını indirin
2. ZIP dosyasını istediğiniz bir klasöre çıkartın
3. `YS Video Downloader v3.0.exe` dosyasını çalıştırın

**⚠️ Önemli:** Tüm dosyaları klasör içinde tutun!
```
📂 YS Video Downloader v3.0/
 ┣ 📜 YS Video Downloader v3.0.exe  ← Bunu çalıştırın
 ┣ ⚙️ ffmpeg.exe                    ← Gerekli
 ┣ 🖼️ logo.ico                      ← Gerekli
 ┗ 📂 _internal/                    ← Gerekli
```

#### macOS
1. **[Releases](https://github.com/ysonmezer/ysvdown/releases/latest)** sayfasından `ysvdown_v3.0_macos.dmg` dosyasını indirin
2. DMG dosyasını açın, `YS Video Downloader.app` dosyasını **Desktop**'a sürükleyin
3. Terminali açın ve şu komutu çalıştırın:
```bash
xattr -dr com.apple.quarantine ~/Desktop/YS\ Video\ Downloader.app
```
4. Uygulamayı çift tıklayarak çalıştırın

> **Not:** Adım 3 yerine System Settings → Privacy & Security → "Open Anyway" seçeneğini de kullanabilirsiniz.

---

### **Geliştiriciler İçin (Kaynak Kod)**

#### Gereksinimler
- Python 3.8 veya üzeri
- pip paket yöneticisi

> **macOS notu:** Homebrew Python kullanmayın. Python.org'dan Python 3.10 indirin:
> https://www.python.org/downloads/release/python-31011/ → "macOS 64-bit universal2 installer"

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
Copy-Item ffmpeg.exe "C:\ysvdown_builds\windows\dist\YS Video Downloader v3.0\"
Copy-Item logo.ico "C:\ysvdown_builds\windows\dist\YS Video Downloader v3.0\"

# 5. ZIP oluştur
cd C:\ysvdown_builds\windows\dist
Compress-Archive -Path "YS Video Downloader v3.0" `
  -DestinationPath "ysvdown_v3.0_windows_portable.zip" -Force

# 6. Hash
Get-FileHash ysvdown_v3.0_windows_portable.zip -Algorithm SHA256

# 7. Temizlik
cd C:\Users\yagiz\OneDrive\CodeProjects\YS Video Downloader\ysvdown_v3.0
Remove-Item windows\main.py -ErrorAction SilentlyContinue
```

#### Build — macOS (Terminal)
```bash
# Önce bir kez yapılacaklar:
# 1. Python.org'dan Python 3.10 indir: https://www.python.org/downloads/release/python-31011/
#    "macOS 64-bit universal2 installer" seç
# 2. Sertifikaları kur:
#    /Applications/Python\ 3.10/Install\ Certificates.command
# 3. Build çıktıları için OneDrive dışında klasör oluştur:
#    mkdir -p ~/ysvdown_builds/macos
# 4. Bağımlılıkları kur:
#    /Library/Frameworks/Python.framework/Versions/3.10/bin/pip3.10 install py2app yt-dlp mutagen pycryptodome websockets brotli
# 5. Static ffmpeg indir: https://evermeet.cx/ffmpeg/ → "Download as ZIP"
#    macos/ffmpeg olarak kaydet, quarantine temizle:
#    xattr -d com.apple.quarantine macos/ffmpeg

cd macos

# 1. Temizlik
rm -rf ~/ysvdown_builds/macos/*
rm -rf build __pycache__

# 2. ffmpeg izinleri (ilk kullanımda zorunlu)
xattr -d com.apple.quarantine ffmpeg 2>/dev/null
chmod +x ffmpeg

# 3. main.py'yi kopyala (symlink değil)
cp ../main.py .

# 4. Build (--no-strip zorunlu!)
/Library/Frameworks/Python.framework/Versions/3.10/bin/python3.10 setup.py py2app --no-strip \
  --dist-dir ~/ysvdown_builds/macos/dist

# 5. ffmpeg kopyala
cp ffmpeg ~/ysvdown_builds/macos/dist/YS\ Video\ Downloader.app/Contents/MacOS/

# 6. build ve main.py temizle
rm -rf build __pycache__
rm main.py

# 7. İmzala (Monterey+ uyumluluğu için zorunlu)
xattr -cr ~/ysvdown_builds/macos/dist/"YS Video Downloader.app"
codesign --force --deep --sign - ~/ysvdown_builds/macos/dist/"YS Video Downloader.app"

# 8. DMG oluştur
hdiutil create -volname "YS Video Downloader v3.0" \
  -srcfolder ~/ysvdown_builds/macos/dist/"YS Video Downloader.app" \
  -ov -format UDZO \
  ~/ysvdown_builds/macos/ysvdown_v3.0_macos.dmg

# 9. Hash
shasum -a 256 ~/ysvdown_builds/macos/ysvdown_v3.0_macos.dmg
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
- **Programlama Dili:** Python 3.11 (Windows), Python 3.10 (macOS)

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

---

# YS Video Downloader Web

This branch also includes an optional web app implementation:

- `backend/`: FastAPI service for metadata analysis, download jobs, progress, cancellation, and authenticated file delivery.
- `frontend/`: React + Vite UI intended for Vercel.
- Downloads are stored temporarily on the OCI server and cleaned up after `FILE_TTL_HOURS`.

## Backend Local Development

Install Python dependencies:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Install `ffmpeg` and make sure it is available on `PATH`. The Docker image does this automatically, but local MP4 merging, MP3 conversion, and H.264 conversion require it.

Create `backend/.env` from `backend/.env.example`:

```env
API_TOKEN=replace-with-a-long-random-token
FRONTEND_ORIGIN=http://localhost:5173
PUBLIC_BASE_URL=http://localhost:8000
DOWNLOAD_DIR=./downloads
FILE_TTL_HOURS=24
MAX_CONCURRENT_JOBS=1
```

Start the API:

```bash
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

Check health:

```bash
curl http://localhost:8000/health
```

All `/api/*` routes require:

```http
Authorization: Bearer <API_TOKEN>
```

## Frontend Local Development

Create `frontend/.env` from `frontend/.env.example`:

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_API_TOKEN=replace-with-the-same-token-as-backend
```

Run the app:

```bash
cd frontend
npm install
npm run dev
```

## Web API

- `POST /api/analyze`
  - Body: `{ "url": "https://..." }`
  - Returns title, playlist status/count, available resolutions, and 4K H.264 availability.
- `POST /api/jobs`
  - Body: `{ "url": "...", "kind": "video", "quality": "1080", "playlist": false, "convertToH264": false }`
  - Returns `{ "jobId": "..." }`.
- `GET /api/jobs/{jobId}`
  - Returns status, progress, phase, logs, errors, and completed file links.
- `POST /api/jobs/{jobId}/cancel`
  - Requests cancellation.
- `GET /api/files/{jobId}/{fileName}`
  - Authenticated completed-file download.

## OCI Deployment

Build and run the backend container:

```bash
docker build -f backend/Dockerfile -t ysvdown-api .
docker run -d \
  --name ysvdown-api \
  -p 8000:8000 \
  --env-file backend/.env \
  -v ysvdown-downloads:/app/downloads \
  ysvdown-api
```

Set `PUBLIC_BASE_URL` to the public HTTPS URL for the OCI backend if file URLs should be absolute.

Put the API behind HTTPS with a reverse proxy such as Nginx or Caddy. Open only the required port in OCI security lists.

## Vercel Deployment

Deploy `frontend/` as the Vercel project root and set:

- `VITE_API_BASE_URL=https://your-oci-api-domain`
- `VITE_API_TOKEN=<same token as API_TOKEN>`

Set backend `FRONTEND_ORIGIN` to the Vercel deployment origin, for example:

```env
FRONTEND_ORIGIN=https://your-project.vercel.app
```

## Web Security Notes

- Use a long random `API_TOKEN`.
- CORS limits browser access, but the bearer token is still the real authorization control.
- This app can consume bandwidth and disk space quickly. Keep `MAX_CONCURRENT_JOBS=1` unless the OCI instance has enough CPU, memory, and network capacity.
- Downloaded files are temporary local server files. They are removed after `FILE_TTL_HOURS` once their job is complete, failed, or cancelled.
