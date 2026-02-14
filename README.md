# 🎥 YS Video Downloader v2.0

Çeşitli video barındırma platformlarından medya içeriklerini kaydetmek için geliştirilmiş, **yt-dlp** kütüphanesini kullanan, açık kaynaklı ve akıllı masaüstü uygulaması.

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

### Seçenek A: Hazır EXE (Windows Kullanıcıları İçin)
Kurulum yapmadan hemen kullanmak için:
1.  Sağ taraftaki **Releases** kısmından **v2.0 Stable** sürümünü indirin.
2.  İndirdiğiniz `YS Video Downloader v2.0.exe` dosyasını çalıştırın.
    * *Not: Programın çalışması için yanına `ffmpeg.exe` dosyasını koymayı unutmayın.*

### Seçenek B: Kaynak Kod (Geliştiriciler İçin)
Kodu incelemek veya geliştirmek isterseniz:
1.  Depoyu klonlayın.
2.  Gerekli kütüphaneleri yükleyin:
    ```bash
    pip install -r requirements.txt
    ```
3.  Uygulamayı başlatın:
    ```bash
    python main.py
    ```

## ⚠️ Yasal Uyarı
Bu yazılım eğitim ve kişisel arşivleme amaçlıdır. Telif hakkı ile korunan materyallerin izinsiz indirilmesi ilgili platformların kurallarına aykırı olabilir. Sorumluluk kullanıcıya aittir.

## 📄 Lisans
Bu proje [MIT Lisansı](LICENSE) ile lisanslanmıştır.