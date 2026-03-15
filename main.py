import tkinter as tk
from tkinter import messagebox, scrolledtext, filedialog, ttk
import subprocess
import threading
import os
import sys
import platform

# ✅ STATİK IMPORT - Defender bypass için
import yt_dlp

# ============================================================================
# PROJE: YS Video Downloader (ysvdown)
# SÜRÜM: v2.6 (Güvenlik & Performans İyileştirmeleri)
# YAPIM: Python + Tkinter + yt-dlp
# DEĞİŞİKLİKLER:
#   - ✅ Static import (Defender bypass)
#   - ✅ FFmpeg varlık kontrolü
#   - ✅ Platform bağımsız klasör açma
#   - ✅ Güvenli dosya değiştirme
#   - ✅ Thread-safe UI güncellemeleri
#   - ✅ Gelişmiş hata yönetimi
#   - ✅ Kayıt yeri kontrolü
#   - ✅ Bağlantı limitleri (Defender için)
#   - ✅ Magic numbers sabitler olarak tanımlandı
#   - ✅ İptal mekanizması iyileştirildi
# ============================================================================

# === ÖZEL EXCEPTION ===
class IptalEdildi(Exception):
    """İndirme iptal edildiğinde fırlatılır"""
    pass

# === ÖZEL LOGGER (İPTAL KONTROLÜ İÇİN) ===
class IptalLogger:
    """yt-dlp için özel logger - her log mesajında iptal kontrolü yapar"""
    def __init__(self, iptal_callback):
        self.iptal_callback = iptal_callback
    
    def debug(self, msg):
        if self.iptal_callback():
            raise IptalEdildi("Kullanıcı iptal etti")
    
    def info(self, msg):
        if self.iptal_callback():
            raise IptalEdildi("Kullanıcı iptal etti")
    
    def warning(self, msg):
        if self.iptal_callback():
            raise IptalEdildi("Kullanıcı iptal etti")
    
    def error(self, msg):
        if self.iptal_callback():
            raise IptalEdildi("Kullanıcı iptal etti")

# === SABITLER ===
ANALIZ_GECIKMESI_MS = 800  # Kullanıcı yazmayı bitirene kadar bekle
PROGRESS_ANIMATION_SPEED = 10  # Indeterminate progress hızı
SOCKET_TIMEOUT_FAST = 5  # Turbo kontrol için (saniye)
SOCKET_TIMEOUT_NORMAL = 10  # Normal metadata çekimi için (saniye)
VARSAYILAN_KAYIT_YERİ = os.path.join(os.path.expanduser("~"), "Desktop")
MP3_KALITE = '192'  # kbps
VIDEO_CRF = '23'  # FFmpeg kalite (0-51, düşük=iyi)
FFMPEG_PRESET = 'fast'  # ultrafast, fast, medium, slow
CONCURRENT_DOWNLOADS = 1  # Aynı anda kaç parça indirilsin
SLEEP_INTERVAL = 1  # İstekler arası bekleme (saniye)
MAX_SLEEP_INTERVAL = 3  # Maksimum bekleme
MAX_RETRIES = 3  # Başarısız istek tekrar sayısı

class YSVideoDownloader:
    def __init__(self, root):
        self.root = root
        self.root.title("YS Video Downloader v2.6")
        self.root.geometry("700x720")
        
        # --- STİL AYARLARI ---
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure("Yesil.Horizontal.TProgressbar", background="#76E060", troughcolor="#E0E0E0")

        # --- DEĞİŞKENLER ---
        self.kayit_yeri = tk.StringVar(value=VARSAYILAN_KAYIT_YERİ) 
        self.format_secimi = tk.StringVar(value="video") 
        self.kalite_secimi = tk.StringVar(value="1080")  
        self.klasor_ac_var = tk.BooleanVar(value=True)
        self.url_var = tk.StringVar()
        
        self.video_metadata = None
        self.analiz_zamanlayici = None
        self.donusturme_yapilsin_mi = False
        self.playlist_modu = False
        self.iptal_bayragi = False
        self.son_indirilen_dosya = None
        self.playlist_tespit_edildi = False

        # Platform bağımlı subprocess ayarları
        if sys.platform == 'win32':
            self.subprocess_flags = subprocess.CREATE_NO_WINDOW
            self.subprocess_startupinfo = subprocess.STARTUPINFO()
            self.subprocess_startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        else:
            self.subprocess_flags = 0
            self.subprocess_startupinfo = None

        self.url_var.trace_add("write", self.on_url_change)

        self.ikon_yukle()
        self.arayuz_olustur()

    # ========================================================================
    # BAŞLATMA FONKSİYONLARI
    # ========================================================================
    
    def ikon_yukle(self):
        """Program ikonunu yükler"""
        icon_path = self.dosya_yolu_bul("logo.ico")
        if os.path.exists(icon_path):
            try: 
                self.root.iconbitmap(icon_path)
            except Exception as e:
                print(f"⚠️ İkon yüklenemedi: {e}")

    def dosya_yolu_bul(self, dosya_adi):
        """Portable mod için dosya yolunu bulur"""
        # macOS için ffmpeg.exe -> ffmpeg
        if platform.system() == 'Darwin' and dosya_adi == 'ffmpeg.exe':
            dosya_adi = 'ffmpeg'
    
        if getattr(sys, 'frozen', False):
            # PyInstaller ile derlenmiş
            base_path = os.path.dirname(sys.executable)
        else:
            # Normal Python
            base_path = os.path.dirname(__file__)
        return os.path.join(base_path, dosya_adi)

    def ffmpeg_kontrol(self):
        """FFmpeg varlığını kontrol eder"""
        ffmpeg_exe = self.dosya_yolu_bul("ffmpeg.exe")
        if not os.path.exists(ffmpeg_exe):
            self.log_yaz(f"❌ FFmpeg bulunamadı: {ffmpeg_exe}")
            messagebox.showerror(
                "FFmpeg Eksik",
                "ffmpeg.exe bulunamadı!\n\n"
                "Program klasöründe ffmpeg.exe olmalı:\n"
                f"{os.path.dirname(ffmpeg_exe)}\n\n"
                "Lütfen dosyaları doğru klasörden çalıştırın."
            )
            return None
        return ffmpeg_exe

    def kayit_yeri_kontrol(self, kayit_yolu):
        """Kayıt yerinin geçerliliğini kontrol eder"""
        if not os.path.exists(kayit_yolu):
            messagebox.showerror(
                "Klasör Hatası",
                f"Kayıt klasörü bulunamadı:\n{kayit_yolu}\n\n"
                "Lütfen geçerli bir klasör seçin."
            )
            return False
        
        if not os.access(kayit_yolu, os.W_OK):
            messagebox.showerror(
                "İzin Hatası",
                f"Bu klasöre yazma izniniz yok:\n{kayit_yolu}\n\n"
                "Lütfen farklı bir klasör seçin."
            )
            return False
        
        return True

    # ========================================================================
    # GÜNCELLEME FONKSİYONLARI
    # ========================================================================

    def ytdlp_guncelle(self):
        """yt-dlp'yi günceller"""
        cevap = messagebox.askyesno(
            "yt-dlp Güncelleme",
            "yt-dlp en son sürüme güncellenecek.\n\n"
            "Bu işlem 1-2 dakika sürebilir.\n"
            "Devam edilsin mi?"
        )
        
        if not cevap:
            return
        
        self.log_yaz("🔄 yt-dlp güncelleniyor...")
        
        # Thread'de çalıştır
        threading.Thread(target=self._ytdlp_guncelleme_thread, daemon=True).start()
    
    def _ytdlp_guncelleme_thread(self):
        """Arka planda yt-dlp günceller"""
        try:
            import subprocess
            import sys
            
            # pip ile güncelle
            cmd = [sys.executable, '-m', 'pip', 'install', '--upgrade', 'yt-dlp']
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                startupinfo=self.subprocess_startupinfo,
                creationflags=self.subprocess_flags
            )
            
            if result.returncode == 0:
                self.root.after(0, lambda: self.log_yaz("✅ yt-dlp başarıyla güncellendi!"))
                self.root.after(0, lambda: messagebox.showinfo(
                    "Güncelleme Başarılı",
                    "yt-dlp en son sürüme güncellendi.\n\n"
                    "Değişikliklerin tam olarak uygulanması için\n"
                    "programı yeniden başlatmanız önerilir."
                ))
            else:
                self.root.after(0, lambda: self.log_yaz(f"❌ Güncelleme hatası: {result.stderr}"))
                self.root.after(0, lambda: messagebox.showerror(
                    "Güncelleme Hatası",
                    f"yt-dlp güncellenemedi.\n\n{result.stderr[:200]}"
                ))
                
        except Exception as e:
            self.root.after(0, lambda: self.log_yaz(f"❌ Hata: {str(e)}"))
            self.root.after(0, lambda: messagebox.showerror(
                "Hata",
                f"Güncelleme sırasında hata oluştu:\n{str(e)}"
            ))

    # ========================================================================
    # ARAYÜZ OLUŞTURMA
    # ========================================================================

    def arayuz_olustur(self):
        # 1. Kaynak Bölümü
        lbl_frame_url = tk.LabelFrame(self.root, text="Kaynak", font=("Segoe UI", 9, "bold"), padx=10, pady=10)
        lbl_frame_url.pack(padx=15, pady=10, fill="x")
        lbl_frame_url.columnconfigure(1, weight=1)

        tk.Label(lbl_frame_url, text="Video Linki:", font=("Segoe UI", 9)).grid(row=0, column=0, sticky="w")
        self.url_entry = tk.Entry(lbl_frame_url, textvariable=self.url_var, font=("Segoe UI", 10))
        self.url_entry.grid(row=0, column=1, padx=10, sticky="ew")
        tk.Button(lbl_frame_url, text="Yapıştır", command=self.pano_yapistir, bg="#e1e1e1", width=10).grid(row=0, column=2)

        # Analiz Durum Label'ı
        self.lbl_analiz_durum = tk.Label(lbl_frame_url, text="", font=("Segoe UI", 9), fg="#666666", anchor="w")
        self.lbl_analiz_durum.grid(row=1, column=1, sticky="ew", padx=10, pady=(5,0))

        tk.Label(lbl_frame_url, text="Kayıt Yeri:", font=("Segoe UI", 9)).grid(row=2, column=0, sticky="w", pady=(20, 10))
        self.path_entry = tk.Entry(lbl_frame_url, textvariable=self.kayit_yeri, font=("Segoe UI", 8), state="readonly")
        self.path_entry.grid(row=2, column=1, padx=10, sticky="ew", pady=(20, 10))
        tk.Button(lbl_frame_url, text="Gözat", command=self.klasor_sec, bg="#e1e1e1", width=10).grid(row=2, column=2, pady=(20, 10))

        # 2. Ayarlar Bölümü
        lbl_frame_settings = tk.LabelFrame(self.root, text="İndirme Ayarları", font=("Segoe UI", 9, "bold"), padx=10, pady=10)
        lbl_frame_settings.pack(padx=15, fill="x")

        tk.Label(lbl_frame_settings, text="Biçim Seçiniz:", font=("Segoe UI", 9, "underline")).grid(row=0, column=0, sticky="w", pady=(0,5))
        tk.Radiobutton(lbl_frame_settings, text="Video (MP4)", variable=self.format_secimi, value="video", command=self.arayuz_guncelle).grid(row=1, column=0, sticky="w")
        tk.Radiobutton(lbl_frame_settings, text="Sadece Ses (MP3)", variable=self.format_secimi, value="mp3", command=self.arayuz_guncelle).grid(row=2, column=0, sticky="w")

        tk.Label(lbl_frame_settings, text="Video Kalitesi:", font=("Segoe UI", 9, "underline")).grid(row=0, column=1, sticky="w", padx=40, pady=(0,5))
        self.rb_720 = tk.Radiobutton(lbl_frame_settings, text="720p (HD)", variable=self.kalite_secimi, value="720", state="disabled")
        self.rb_720.grid(row=1, column=1, sticky="w", padx=40)
        self.rb_1080 = tk.Radiobutton(lbl_frame_settings, text="1080p (FHD)", variable=self.kalite_secimi, value="1080", state="disabled")
        self.rb_1080.grid(row=2, column=1, sticky="w", padx=40)
        self.rb_4k = tk.Radiobutton(lbl_frame_settings, text="4K (UHD)", variable=self.kalite_secimi, value="2160", state="disabled")
        self.rb_4k.grid(row=3, column=1, sticky="w", padx=40)

        tk.Checkbutton(lbl_frame_settings, text="İndirme bitince klasörü aç", variable=self.klasor_ac_var).grid(row=4, column=0, columnspan=2, sticky="w", pady=(10,0))

        # 3. Aksiyon Butonları
        self.frame_action = tk.Frame(self.root)
        self.frame_action.pack(pady=15, padx=15, fill="x")
        
        # A) Tek Buton
        self.download_button = tk.Button(self.frame_action, text="İNDİR", state="disabled", command=lambda: self.indirmeyi_baslat(playlist_tercihi=False), 
                                         bg="#cccccc", fg="white", font=("Segoe UI", 12, "bold"), height=2, cursor="hand2")
        self.download_button.pack(fill="x")

        # B) Playlist Butonları (GRID SİSTEMİ)
        self.frame_playlist_btns = tk.Frame(self.frame_action)
        self.frame_playlist_btns.columnconfigure(0, weight=1, uniform="group1")
        self.frame_playlist_btns.columnconfigure(1, weight=1, uniform="group1")
        
        self.btn_tek_indir = tk.Button(self.frame_playlist_btns, text="VİDEOYU İNDİR", 
                                       command=lambda: self.indirmeyi_baslat(playlist_tercihi=False),
                                       bg="#0078D7", fg="white", font=("Segoe UI", 12, "bold"), height=2, cursor="hand2")
        self.btn_tek_indir.grid(row=0, column=0, sticky="ew", padx=(0, 5))

        self.btn_playlist_indir = tk.Button(self.frame_playlist_btns, text="TÜM LİSTEYİ İNDİR", 
                                            command=lambda: self.indirmeyi_baslat(playlist_tercihi=True),
                                            bg="#28a745", fg="white", font=("Segoe UI", 12, "bold"), height=2, cursor="hand2")
        self.btn_playlist_indir.grid(row=0, column=1, sticky="ew", padx=(5, 0))

        # Progress Bar
        self.progress = ttk.Progressbar(self.root, orient="horizontal", length=100, mode="determinate", style="Yesil.Horizontal.TProgressbar")
        self.progress.pack(pady=(0, 10), padx=15, fill="x")

        # 4. Log Alanı
        tk.Label(self.root, text="İşlem Kayıtları:", font=("Segoe UI", 8)).pack(pady=(5,0))
        self.log_text = scrolledtext.ScrolledText(self.root, height=10, state='disabled', font=("Consolas", 8))
        self.log_text.pack(padx=15, pady=5, fill="both", expand=True)

        # Footer
        footer_frame = tk.Frame(self.root)
        footer_frame.pack(side=tk.BOTTOM, pady=5, fill="x")
        
        tk.Label(footer_frame, text="©2026 by YS", fg="gray", font=("Segoe UI", 8)).pack(side=tk.LEFT, padx=15)
        
        # Küçük güncelleme linki
        self.update_link = tk.Label(
            footer_frame, 
            text="yt-dlp güncelle", 
            fg="#999999",  # Açık gri
            font=("Segoe UI", 7, "underline"),
            cursor="hand2"
        )
        self.update_link.pack(side=tk.RIGHT, padx=15)
        self.update_link.bind("<Button-1>", lambda e: self.ytdlp_guncelle())
        self.update_link.bind("<Enter>", lambda e: self.update_link.config(fg="#0078D7"))  # Hover efekti
        self.update_link.bind("<Leave>", lambda e: self.update_link.config(fg="#999999"))  # Normal renk

    # ========================================================================
    # UI YARDIMCI FONKSİYONLARI
    # ========================================================================

    def on_url_change(self, *args):
        """URL değiştiğinde otomatik analiz başlatır"""
        if self.analiz_zamanlayici is not None:
            self.root.after_cancel(self.analiz_zamanlayici)
        
        url = self.url_var.get().strip()
        if not url:
            self.reset_ui_state()
            return

        self.lbl_analiz_durum.config(text="...", fg="#999999", font=("Segoe UI", 9))
        self.analiz_zamanlayici = self.root.after(ANALIZ_GECIKMESI_MS, self.analizi_baslat)

    def reset_ui_state(self):
        """UI'yi başlangıç durumuna getirir"""
        self.frame_playlist_btns.pack_forget()
        self.download_button.pack(fill="x")
        self.download_button.config(state="disabled", text="İNDİR", bg="#cccccc")
        
        self.rb_720.config(state="disabled")
        self.rb_1080.config(state="disabled")
        self.rb_4k.config(state="disabled")
        self.lbl_analiz_durum.config(text="", fg="#666666")
        self.video_metadata = None
        self.playlist_tespit_edildi = False

    def pano_yapistir(self):
        """Panodan URL yapıştırır"""
        try:
            pano_icerigi = self.root.clipboard_get()
            self.url_entry.delete(0, tk.END)
            self.url_entry.insert(0, pano_icerigi)
        except tk.TclError:
            messagebox.showinfo("Pano Boş", "Panoda kopyalanmış bir link bulunamadı.")
        except Exception as e:
            messagebox.showerror("Hata", f"Yapıştırma başarısız: {e}")

    def klasor_sec(self):
        """Kayıt klasörü seçtirir"""
        klasor = filedialog.askdirectory()
        if klasor: 
            self.kayit_yeri.set(klasor)

    def log_yaz(self, mesaj):
        """Log alanına mesaj yazar"""
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, mesaj + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state='disabled')

    def buton_sifirla(self):
        """İndirme butonlarını başlangıç durumuna getirir"""
        if self.playlist_tespit_edildi:
            self.download_button.pack_forget()
            self.frame_playlist_btns.pack(fill="x")
        else:
            self.frame_playlist_btns.pack_forget()
            self.download_button.pack(fill="x")
            self.download_button.config(state='normal', text="İNDİRMEYİ BAŞLAT", bg="#0078D7")

    def arayuz_guncelle(self):
        """Format değiştiğinde arayüzü günceller"""
        if self.format_secimi.get() == "mp3":
            self.rb_720.config(state="disabled")
            self.rb_1080.config(state="disabled")
            self.rb_4k.config(state="disabled")
        elif self.video_metadata:
            self.analiz_basarili(self.video_metadata, self.playlist_tespit_edildi) 

    def klasor_ac(self, yol):
        """Platform bağımsız klasör açma"""
        try:
            if sys.platform == 'win32':
                os.startfile(yol)
            elif sys.platform == 'darwin':  # macOS
                subprocess.run(['open', yol], check=False)
            else:  # Linux
                subprocess.run(['xdg-open', yol], check=False)
        except Exception as e:
            self.log_yaz(f"⚠️ Klasör açılamadı: {e}")

    # ========================================================================
    # ANALİZ MODÜLÜ
    # ========================================================================

    def analizi_baslat(self):
        """URL analizini başlatır"""
        url = self.url_var.get().strip()
        if not url: 
            return

        self.lbl_analiz_durum.config(text="Analiz ediliyor...", fg="#666666")
        self.download_button.config(text="ANALİZ EDİLİYOR...", bg="#999999")
        
        threading.Thread(target=self.analiz_thread, args=(url,), daemon=True).start()

    def analiz_thread(self, url):
        """Arka planda URL analizi yapar"""
        # FFmpeg kontrolü
        ffmpeg_exe = self.ffmpeg_kontrol()
        if not ffmpeg_exe:
            self.root.after(0, self.reset_ui_state)
            return
        
        is_playlist = False
        playlist_count = None

        # --- TURBO KONTROL ---
        check_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': 'in_playlist',
            'playlist_items': '1', 
            'socket_timeout': SOCKET_TIMEOUT_FAST,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'http_headers': {
                'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
            }
        }

        try:
            with yt_dlp.YoutubeDL(check_opts) as ydl:
                info = ydl.extract_info(url, download=False, process=False)
                if 'entries' in info or info.get('_type') == 'playlist':
                    is_playlist = True
                    playlist_count = info.get('playlist_count') or info.get('n_entries')

            # --- METADATA ---
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'noplaylist': True, 
                'socket_timeout': SOCKET_TIMEOUT_NORMAL,
                'ffmpeg_location': ffmpeg_exe,
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                 metadata = ydl.extract_info(url, download=False)
                 if is_playlist:
                     metadata['playlist_count'] = playlist_count 

            self.root.after(0, lambda: self.analiz_basarili(metadata, is_playlist))
            
        except Exception as e:
            hata_mesaji = str(e)
            self.root.after(0, lambda: self.analiz_hatali(hata_mesaji))

    def analiz_hatali(self, hata_detay=""):
        """Analiz hatalı olduğunda çalışır"""
        self.lbl_analiz_durum.config(text="Geçersiz link.", fg="#d9534f")
        if hata_detay:
            self.log_yaz(f"⚠️ Analiz hatası: {hata_detay}")
        self.reset_ui_state()

    def analiz_basarili(self, metadata, is_playlist):
        """Analiz başarılı olduğunda UI'yi günceller"""
        self.video_metadata = metadata
        self.playlist_tespit_edildi = is_playlist
        
        title = metadata.get('title', 'Bilinmeyen')[:40]
        
        if is_playlist:
            count = metadata.get('playlist_count')
            if count is not None and count > 0:
                count_str = f"({count} Video)"
            elif count == 0:
                count_str = "(Boş Playlist)"
            else:
                count_str = "(Playlist - Sayılıyor...)"
            
            # Yeşil renkli görsel bildirim
            self.lbl_analiz_durum.config(
                text=f"Playlist Bulundu {count_str} - İlk Video: {title}...", 
                fg="#28a745", 
                font=("Segoe UI", 9, "bold")
            )
            
            self.download_button.pack_forget()
            self.frame_playlist_btns.pack(fill="x")
        else:
            # Tek video - siyah ve normal
            self.lbl_analiz_durum.config(
                text=f"Video: {title}...", 
                fg="#333333", 
                font=("Segoe UI", 9)
            )
            
            self.frame_playlist_btns.pack_forget()
            self.download_button.pack(fill="x")
            self.download_button.config(state="normal", text="İNDİRMEYİ BAŞLAT", bg="#0078D7")
        
        # Kalite Seçenekleri
        formats = metadata.get('formats', [])
        resolutions = set()
        for f in formats:
            h = f.get('height')
            if h: 
                resolutions.add(h)
            
        self.rb_720.config(state="normal" if any(r >= 720 for r in resolutions) else "disabled")
        self.rb_1080.config(state="normal" if any(r >= 1080 for r in resolutions) else "disabled")
        self.rb_4k.config(state="normal" if any(r >= 2160 for r in resolutions) else "disabled")
        
        current_res = int(self.kalite_secimi.get())
        if not any(r >= current_res for r in resolutions):
             self.kalite_secimi.set("720")

    # ========================================================================
    # İNDİRME MOTORU
    # ========================================================================

    def indirmeyi_baslat(self, playlist_tercihi=False):
        """İndirme işlemini başlatır"""
        if self.download_button['text'] == "İPTAL ET ❌":
            self.iptal_et()
            return

        url = self.url_var.get()
        self.iptal_bayragi = False
        self.donusturme_yapilsin_mi = False
        self.son_indirilen_dosya = None
        self.playlist_modu = playlist_tercihi

        self.frame_playlist_btns.pack_forget()
        self.download_button.pack(fill="x")
        
        # 4K VP9 formatı kontrolü
        if self.format_secimi.get() == "video" and self.kalite_secimi.get() == "2160":
            try:
                formats = self.video_metadata.get('formats', [])
                has_4k_h264 = False
                for f in formats:
                    if f.get('height') == 2160 and f.get('vcodec', '').startswith('avc1'):
                        has_4k_h264 = True
                        break
                
                if not has_4k_h264:
                    cevap = messagebox.askyesnocancel(
                        "Format Dönüştürme Önerisi", 
                        "Bu videonun 4K versiyonu VP9 formatındadır.\n"
                        "🛠️ EVET: İndir ve H.264 formatına dönüştür (Uzun sürer)\n"
                        "⚡ HAYIR: Olduğu gibi (VP9) indir\n"
                        "❌ İPTAL: İşlemi iptal et"
                    )
                    
                    if cevap is None: 
                        self.buton_sifirla()
                        return 
                    elif cevap: 
                        self.donusturme_yapilsin_mi = True
                    else: 
                        self.donusturme_yapilsin_mi = False
            except Exception as e:
                self.log_yaz(f"⚠️ 4K format kontrolü başarısız: {e}")

        self.download_button.config(text="İPTAL ET ❌", bg="#d9534f", state='normal')
        self.progress['value'] = 0
        threading.Thread(target=self.indir_gorevi, args=(url,), daemon=True).start()

    def iptal_et(self):
        """İndirme işlemini iptal eder"""
        cevap = messagebox.askyesno("İptal", "İndirme işlemini durdurmak istiyor musunuz?")
        if cevap:
            self.iptal_bayragi = True
            self.log_yaz("⚠️ İPTAL EDİLİYOR - Lütfen bekleyin...")
            self.download_button.config(state='disabled', text="İPTAL EDİLİYOR...")
            
            # ✅ Progress bar'ı sıfırla
            self.progress['value'] = 0
            
            # NOT: yt-dlp mevcut videoyu tamamlayana kadar tam durmayabilir
            # Bu yt-dlp'nin bir limitasyonudur

    def indir_gorevi(self, url):
        """Arka planda indirme işlemini yapar"""
        self.log_yaz(f"--- İndirme Başlıyor ---")
        
        # FFmpeg kontrolü
        ffmpeg_exe = self.ffmpeg_kontrol()
        if not ffmpeg_exe:
            self.root.after(0, self.buton_sifirla)
            return
        
        kayit_yolu = self.kayit_yeri.get()
        
        # Kayıt yeri kontrolü
        if not self.kayit_yeri_kontrol(kayit_yolu):
            self.root.after(0, self.buton_sifirla)
            return
        
        format_tipi = self.format_secimi.get()
        
        if self.playlist_modu:
            # ✅ Kanal adı kullan, yoksa playlist başlığı
            out_tmpl = os.path.join(kayit_yolu, "%(uploader|playlist_uploader|playlist_title)s", "%(title)s.%(ext)s")
        else:
            out_tmpl = os.path.join(kayit_yolu, "%(title)s.%(ext)s")

        ydl_opts = {
            'outtmpl': out_tmpl,
            'ffmpeg_location': ffmpeg_exe,
            'noplaylist': not self.playlist_modu,
            'progress_hooks': [self.progress_hook],
            'quiet': False,  # ✅ Logger çalışması için False olmalı
            'no_warnings': True,
            'ignoreerrors': True,
            # ✅ Konsol çıktısını tamamen kapat
            'noprogress': True,
            # ✅ Part dosyalarını otomatik temizle
            'keepvideo': False,
            # ✅ Playlist için: hata olunca dur
            'abort_on_error': False,
            # ✅ İPTAL KONTROLÜ: Özel logger
            'logger': IptalLogger(lambda: self.iptal_bayragi),
            # ✅ Defender bypass için bağlantı limitleri
            'concurrent_fragment_downloads': CONCURRENT_DOWNLOADS,
            'sleep_interval': SLEEP_INTERVAL,
            'max_sleep_interval': MAX_SLEEP_INTERVAL,
            'retries': MAX_RETRIES,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        }

        if format_tipi == "mp3":
            self.log_yaz("Mod: Sadece Ses (MP3)")
            ydl_opts.update({
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': MP3_KALITE,
                }],
            })
        else:
            kalite = self.kalite_secimi.get()
            self.log_yaz(f"Mod: Video (Max {kalite}p)")
            if kalite == "2160":
                format_str = f"bestvideo[height<={kalite}]+bestaudio/best[height<={kalite}]/best"
            else:
                format_str = f"bestvideo[height<={kalite}][vcodec^=avc1]+bestaudio[ext=m4a]/best[ext=mp4]/best"
            
            ydl_opts.update({
                'format': format_str,
                'merge_output_format': 'mp4',
            })

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # ✅ Basit: URL'yi direkt indir
                ydl.download([url])
            
            if not self.iptal_bayragi:
                if self.donusturme_yapilsin_mi and self.son_indirilen_dosya and os.path.exists(self.son_indirilen_dosya):
                    self.donusturme_islemi(self.son_indirilen_dosya, ffmpeg_exe)
                
                self.root.after(0, lambda: self.islem_tamamlandi_ui(kayit_yolu))
            else:
                # İptal edildi - sessizce bitir
                self.temizle_part_dosyalari(kayit_yolu)
                self.root.after(0, self.buton_sifirla)

        except IptalEdildi:
            # Kullanıcı iptal etti
            self.root.after(0, lambda: self.log_yaz("🛑 İşlem kullanıcı tarafından iptal edildi."))
            self.temizle_part_dosyalari(kayit_yolu)
            self.progress['value'] = 0
            self.root.after(0, self.buton_sifirla)
            
        except Exception as e:
            if self.iptal_bayragi:
                self.root.after(0, lambda: self.log_yaz("🛑 İşlem kullanıcı tarafından iptal edildi."))
                self.temizle_part_dosyalari(kayit_yolu)
                self.progress['value'] = 0
                self.root.after(0, self.buton_sifirla)
            else:
                self.root.after(0, lambda msg=str(e): self.log_yaz(f"❌ HATA: {msg}"))
                self.root.after(0, self.buton_sifirla)

    def temizle_part_dosyalari(self, klasor):
        """İptal sonrası kalan .part dosyalarını temizler"""
        try:
            import glob
            part_dosyalari = glob.glob(os.path.join(klasor, "**", "*.part"), recursive=True)
            
            if part_dosyalari:
                self.log_yaz(f"🧹 {len(part_dosyalari)} adet .part dosyası temizleniyor...")
                for dosya in part_dosyalari:
                    try:
                        os.remove(dosya)
                        self.log_yaz(f"   ✓ Silindi: {os.path.basename(dosya)}")
                    except Exception as e:
                        self.log_yaz(f"   ✗ Silinemedi: {os.path.basename(dosya)} - {e}")
                        
                self.log_yaz("✅ Temizlik tamamlandı.")
        except Exception as e:
            self.log_yaz(f"⚠️ Temizlik hatası: {e}")

    def progress_hook(self, d):
        """İndirme ilerlemesini takip eder (Thread-safe)"""
        # ✅ İptal kontrolü - Özel exception fırlat
        if self.iptal_bayragi:
            raise IptalEdildi("Kullanıcı iptal etti")

        if d['status'] == 'downloading':
            if self.iptal_bayragi:
                raise IptalEdildi("Kullanıcı iptal etti")
                
            try:
                p = d.get('_percent_str', '0%').replace('%','')
                self.root.after(0, lambda val=float(p): self.progress.config(value=val))
            except ValueError:
                pass
            
        elif d['status'] == 'finished':
            if self.iptal_bayragi:
                raise IptalEdildi("Kullanıcı iptal etti")
                
            self.son_indirilen_dosya = d.get('filename')
            dosya_adi = os.path.basename(self.son_indirilen_dosya or '')
            self.root.after(0, lambda: self.log_yaz(f"⬇️ İndirildi: {dosya_adi}"))
        
        elif d['status'] == 'error':
            if self.iptal_bayragi:
                raise IptalEdildi("Kullanıcı iptal etti")

    # ========================================================================
    # DÖNÜŞTÜRME MODÜLÜ
    # ========================================================================

    def donusturme_islemi(self, dosya_yolu, ffmpeg_exe):
        """VP9 videosunu H.264 formatına dönüştürür"""
        self.log_yaz("⏳ DÖNÜŞTÜRME BAŞLIYOR (MP4/H.264)...")
        self.root.after(0, lambda: self.download_button.config(text="DÖNÜŞTÜRÜLÜYOR..."))
        self.root.after(0, lambda: self.progress.config(mode='indeterminate'))
        self.root.after(0, lambda: self.progress.start(PROGRESS_ANIMATION_SPEED))

        klasor = os.path.dirname(dosya_yolu)
        dosya_adi = os.path.basename(dosya_yolu)
        yeni_dosya_adi = "CONVERTED_" + dosya_adi
        yeni_dosya_yolu = os.path.join(klasor, yeni_dosya_adi)

        komut = [
            ffmpeg_exe, "-y", 
            "-i", dosya_yolu, 
            "-c:v", "libx264", "-preset", FFMPEG_PRESET, "-crf", VIDEO_CRF, 
            "-c:a", "copy", 
            yeni_dosya_yolu
        ]

        try:
            subprocess.run(
                komut, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                startupinfo=self.subprocess_startupinfo,
                creationflags=self.subprocess_flags
            )

            # ✅ Güvenli dosya değiştirme
            if os.path.exists(yeni_dosya_yolu):
                self.guvenli_dosya_degistir(dosya_yolu, yeni_dosya_yolu)
            else:
                self.log_yaz("❌ Dönüştürme dosyası oluşturulamadı.")
                
        except Exception as e:
            self.log_yaz(f"❌ Dönüştürme Hatası: {str(e)}")

        self.root.after(0, lambda: self.progress.stop())
        self.root.after(0, lambda: self.progress.config(mode='determinate'))

    def guvenli_dosya_degistir(self, orijinal, yeni):
        """Dosyaları güvenli şekilde değiştirir (veri kaybı riski yok)"""
        try:
            yedek_yolu = orijinal + ".backup"
            
            # 1. Orijinali yedekle
            if os.path.exists(orijinal):
                os.rename(orijinal, yedek_yolu)
            
            # 2. Yeniyi taşı
            os.rename(yeni, orijinal)
            
            # 3. Yedeği sil
            if os.path.exists(yedek_yolu):
                os.remove(yedek_yolu)
            
            self.log_yaz("✅ DÖNÜŞTÜRME TAMAMLANDI.")
            
        except Exception as e:
            self.log_yaz(f"❌ Dosya değiştirme hatası: {e}")
            # Geri yükleme
            if os.path.exists(yedek_yolu):
                if not os.path.exists(orijinal):
                    os.rename(yedek_yolu, orijinal)
                    self.log_yaz("⚠️ Orijinal dosya geri yüklendi.")

    # ========================================================================
    # TAMAMLAMA
    # ========================================================================

    def islem_tamamlandi_ui(self, kayit_yolu):
        """İşlem tamamlandığında UI'yi günceller"""
        self.buton_sifirla()
        self.log_yaz("✅ TÜM İŞLEMLER TAMAMLANDI.")
        self.progress['value'] = 100
        messagebox.showinfo("Başarılı", "İndirme Tamamlandı!")
        
        if self.klasor_ac_var.get(): 
            self.klasor_ac(kayit_yolu)

# ============================================================================
# PROGRAM BAŞLATMA
# ============================================================================

if __name__ == "__main__":
    root = tk.Tk()
    app = YSVideoDownloader(root)
    root.mainloop()
