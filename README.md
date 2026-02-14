# 🎥 YS Video Downloader v2.0

Çeşitli video barındırma platformlarından medya içeriklerini indirmek için geliştirilmiş, **yt-dlp** kütüphanesini kullanan, açık kaynaklı, akıllı masaüstü uygulaması.

![Lisans](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.x-yellow.svg)
![Status](https://img.shields.io/badge/status-stable-green.svg)

## 🌟 v2.0 Yenilikleri ve Özellikler

* **📂 Playlist Desteği:** Oynatma listelerini otomatik algılar; ister tüm listeyi, ister tek videoyu indirebilirsiniz.
* **⚡ Gömülü Motor:** Harici `yt-dlp.exe` dosyasına ihtiyaç duymaz, Python kütüphanesi olarak doğrudan çalışır (Daha hızlı analiz).
* **🛑 İptal Seçeneği:** İndirme işlemini istediğiniz an durdurabilirsiniz.
* **Kurgu Dostu:** 4K VP9 videoları, Premiere Pro uyumlu H.264 formatına dönüştürme seçeneği sunar.
* **Format Seçenekleri:** MP4 (720p, 1080p, 4K) ve MP3 (Sadece Ses).

## 🚀 Kurulum ve Kullanım

Bu proje taşınabilir (portable) yapıdadır, kurulum gerektirmez.

1.  **Releases** kısmından `ysvdown_v2.0_portable.zip` dosyasını indirin.
2.  ZIP dosyasını bir klasöre çıkartın (Örneğin Masaüstüne).
3.  Klasörün içindeki `YS Video Downloader v2.0.exe` uygulamasını çalıştırın.

*(⚠️ Önemli Not: Bu sürüm, antivirüs hatalarını (False Positive) önlemek amacıyla klasör yapısında paketlenmiştir. Programın çalışması için `ffmpeg.exe` ve `_internal` klasörünün, uygulamanın yanında durması gerekir. Lütfen dosyaları klasörden dışarı çıkarmayın.)*

**Beklenen Klasör Yapısı:**
```text
📂 YS Video Downloader v2.0/
 ┣ 📂 _internal/
 ┣ 📜 YS Video Downloader v2.0.exe  <-- (Buna tıklayıp çalıştırın)
 ┣ ⚙️ ffmpeg.exe
 ┗ 🖼️ logo.ico

### Geliştiriciler İçin (Kaynak Kod)
Kodu incelemek veya geliştirmek isterseniz:
1.  Depoyu klonlayın.
2.  Gerekli kütüphaneleri yükleyin: `pip install -r requirements.txt`
3.  Uygulamayı başlatın: `python main.py`

## ⚠️ Yasal Uyarı
Bu yazılım eğitim ve kişisel arşivleme amaçlıdır. Telif hakkı ile korunan materyallerin izinsiz indirilmesi ilgili platformların kurallarına aykırı olabilir. Sorumluluk kullanıcıya aittir.

## 📄 Lisans

Bu proje [MIT Lisansı](LICENSE) ile lisanslanmıştır.





