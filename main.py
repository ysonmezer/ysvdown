import tkinter as tk
from tkinter import messagebox, scrolledtext, filedialog, ttk
import subprocess
import threading
import os
import sys

# PROJE: YS Video Downloader (ysvdown)
# SÜRÜM: v2.0 Stable
# YAPIM: Python + Tkinter + yt-dlp (Embedded)

class YSVideoDownloader:
    def __init__(self, root):
        self.root = root
        self.root.title("YS Video Downloader v2.0")
        self.root.geometry("700x700")
        
        # --- STİL AYARLARI ---
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure("Yesil.Horizontal.TProgressbar", background="#76E060", troughcolor="#E0E0E0")

        # --- DEĞİŞKENLER ---
        self.kayit_yeri = tk.StringVar(value=os.path.join(os.path.expanduser("~"), "Desktop")) 
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

        # URL İzleyici
        self.url_var.trace_add("write", self.on_url_change)

        self.ikon_yukle()
        self.arayuz_olustur()

    def ikon_yukle(self):
        icon_path = self.dosya_yolu_bul("logo.ico")
        if os.path.exists(icon_path):
            try: self.root.iconbitmap(icon_path)
            except: pass

    def dosya_yolu_bul(self, dosya_adi):
        if getattr(sys, 'frozen', False):
            base_path = os.path.dirname(sys.executable)
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base_path, dosya_adi)

    def arayuz_olustur(self):
        # 1. Kaynak Bölümü
        lbl_frame_url = tk.LabelFrame(self.root, text="Kaynak", font=("Segoe UI", 9, "bold"), padx=10, pady=10)
        lbl_frame_url.pack(padx=15, pady=10, fill="x")
        lbl_frame_url.columnconfigure(1, weight=1)

        tk.Label(lbl_frame_url, text="Video Linki:", font=("Segoe UI", 9)).grid(row=0, column=0, sticky="w")
        self.url_entry = tk.Entry(lbl_frame_url, textvariable=self.url_var, font=("Segoe UI", 10))
        self.url_entry.grid(row=0, column=1, padx=10, sticky="ew")
        tk.Button(lbl_frame_url, text="Yapıştır", command=self.pano_yapistir, bg="#e1e1e1", width=10).grid(row=0, column=2)

        self.lbl_analiz_durum = tk.Label(lbl_frame_url, text="", font=("Segoe UI", 9), fg="#666666")
        self.lbl_analiz_durum.grid(row=1, column=1, sticky="w", padx=10, pady=(5,0))

        tk.Label(lbl_frame_url, text="Kayıt Yeri:", font=("Segoe UI", 9)).grid(row=2, column=0, sticky="w", pady=(20, 10))
        self.path_entry = tk.Entry(lbl_frame_url, textvariable=self.kayit_yeri, font=("Segoe UI", 8), state="readonly")
        self.path_entry.grid(row=2, column=1, padx=10, sticky="ew", pady=(20, 10))
        tk.Button(lbl_frame_url, text="Gözat", command=self.klasor_sec, bg="#e1e1e1", width=10).grid(row=2, column=2, pady=(20, 10))

        # 3. Ayarlar Bölümü
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

        # 4. Aksiyon Butonu
        frame_action = tk.Frame(self.root)
        frame_action.pack(pady=15, padx=15, fill="x")
        
        self.download_button = tk.Button(frame_action, text="İNDİR", state="disabled", command=self.indirmeyi_baslat, 
                                         bg="#cccccc", fg="white", font=("Segoe UI", 12, "bold"), height=2, cursor="hand2")
        self.download_button.pack(fill="x")

        self.progress = ttk.Progressbar(self.root, orient="horizontal", length=100, mode="determinate", style="Yesil.Horizontal.TProgressbar")
        self.progress.pack(pady=(0, 10), padx=15, fill="x")

        # 5. Log Alanı
        tk.Label(self.root, text="İşlem Kayıtları:", font=("Segoe UI", 8)).pack(pady=(5,0))
        self.log_text = scrolledtext.ScrolledText(self.root, height=10, state='disabled', font=("Consolas", 8))
        self.log_text.pack(padx=15, pady=5, fill="both", expand=True)

        # Footer (Güncellendi)
        tk.Label(self.root, text="©2026 by YS", fg="gray", font=("Segoe UI", 8)).pack(side=tk.BOTTOM, pady=5)

    # --- UI YARDIMCILARI ---
    def on_url_change(self, *args):
        if self.analiz_zamanlayici is not None:
            self.root.after_cancel(self.analiz_zamanlayici)
        
        url = self.url_var.get().strip()
        if not url:
            self.reset_ui_state()
            return

        self.lbl_analiz_durum.config(text="...", fg="#999999")
        self.analiz_zamanlayici = self.root.after(800, self.analizi_baslat)

    def reset_ui_state(self):
        self.download_button.config(state="disabled", text="İNDİR", bg="#cccccc")
        self.rb_720.config(state="disabled")
        self.rb_1080.config(state="disabled")
        self.rb_4k.config(state="disabled")
        self.lbl_analiz_durum.config(text="")
        self.video_metadata = None

    def pano_yapistir(self):
        try:
            self.url_entry.delete(0, tk.END)
            self.url_entry.insert(0, self.root.clipboard_get())
        except: pass

    def klasor_sec(self):
        klasor = filedialog.askdirectory()
        if klasor: self.kayit_yeri.set(klasor)

    def log_yaz(self, mesaj):
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, mesaj + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state='disabled')

    def buton_sifirla(self):
        self.download_button.config(state='normal', text="İNDİRMEYİ BAŞLAT", bg="#0078D7")

    def arayuz_guncelle(self):
        if self.format_secimi.get() == "mp3":
            self.rb_720.config(state="disabled")
            self.rb_1080.config(state="disabled")
            self.rb_4k.config(state="disabled")
        elif self.video_metadata:
            self.analiz_basarili(self.video_metadata) 

    # --- ANALİZ MODÜLÜ ---
    def analizi_baslat(self):
        url = self.url_var.get().strip()
        if not url: return

        self.lbl_analiz_durum.config(text="Analiz ediliyor...", fg="#666666")
        self.download_button.config(text="ANALİZ EDİLİYOR...", bg="#999999")
        
        threading.Thread(target=self.analiz_thread, args=(url,)).start()

    def analiz_thread(self, url):
        import yt_dlp 
        ffmpeg_exe = self.dosya_yolu_bul("ffmpeg.exe")
        
        self.playlist_modu = False
        noplaylist_degeri = True 

        # --- HIZLI KONTROL ---
        check_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': 'in_playlist',
            'playlist_items': '1', # Hız için sadece 1. öğeye bak
            'socket_timeout': 5,
        }

        try:
            with yt_dlp.YoutubeDL(check_opts) as ydl:
                info = ydl.extract_info(url, download=False, process=False)
                
                # Playlist Algılama
                if 'entries' in info or info.get('_type') == 'playlist':
                    video_sayisi = info.get('playlist_count')
                    sayi_metni = f" ({video_sayisi} Video)" if video_sayisi else ""
                    
                    msg_text = f"Bu link bir Oynatma Listesi{sayi_metni} içeriyor.\n\n"
                    msg_text += "Sadece şu anki videoyu mu indirmek istersiniz?\n\n"
                    msg_text += "✅ EVET: Sadece Videoyu İndir (Varsayılan)\n"
                    msg_text += "📂 HAYIR: Tüm Listeyi İndir (Uzun sürebilir)\n"
                    msg_text += "❌ İPTAL: Vazgeç"

                    cevap = messagebox.askyesnocancel(
                        "İndirme Tercihi", 
                        msg_text,
                        default=messagebox.YES,
                        icon='question'
                    )
                    
                    if cevap is None: # İptal
                        self.root.after(0, self.reset_ui_state)
                        return 
                    elif cevap: # EVET (Sadece Video)
                        self.playlist_modu = False
                        noplaylist_degeri = True
                    else: # HAYIR (Tüm Liste)
                        self.playlist_modu = True
                        noplaylist_degeri = False

            # --- GERÇEK ANALİZ ---
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'noplaylist': noplaylist_degeri,
                'socket_timeout': 10,
                'ffmpeg_location': ffmpeg_exe,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                if self.playlist_modu:
                     ydl_opts['extract_flat'] = True 
                     with yt_dlp.YoutubeDL(ydl_opts) as ydl_flat:
                        metadata = ydl_flat.extract_info(url, download=False)
                        playlist_title = metadata.get('title', 'Bilinmeyen Liste')
                        metadata['title'] = f"[PLAYLIST] {playlist_title}"
                else:
                    metadata = ydl.extract_info(url, download=False)
            
            self.root.after(0, lambda: self.analiz_basarili(metadata))
            
        except Exception as e:
            print(f"Analiz Hatası: {e}")
            self.root.after(0, self.analiz_hatali)

    def analiz_hatali(self):
        self.lbl_analiz_durum.config(text="Geçersiz link.", fg="#d9534f")
        self.reset_ui_state()

    def analiz_basarili(self, metadata):
        self.video_metadata = metadata
        title = metadata.get('title', 'Bilinmeyen')[:50]
        self.lbl_analiz_durum.config(text=f"Video: {title}...", fg="#333333")
        
        self.download_button.config(state="normal", text="İNDİRMEYİ BAŞLAT", bg="#0078D7")
        
        formats = metadata.get('formats', [])
        resolutions = set()
        for f in formats:
            h = f.get('height')
            if h: resolutions.add(h)
            
        self.rb_720.config(state="normal" if any(r >= 720 for r in resolutions) else "disabled")
        self.rb_1080.config(state="normal" if any(r >= 1080 for r in resolutions) else "disabled")
        self.rb_4k.config(state="normal" if any(r >= 2160 for r in resolutions) else "disabled")
        
        current_res = int(self.kalite_secimi.get())
        if not any(r >= current_res for r in resolutions):
             self.kalite_secimi.set("720")

    # --- İNDİRME MOTORU ---
    def indirmeyi_baslat(self):
        # İptal Modu Kontrolü
        if self.download_button['text'] == "İPTAL ET ❌":
            self.iptal_et()
            return

        url = self.url_var.get()
        self.iptal_bayragi = False
        self.donusturme_yapilsin_mi = False
        self.son_indirilen_dosya = None

        # 4K VP9 Kontrolü
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
                        "(Bazı eski Premiere sürümleri bunu açmayabilir.)\n\n"
                        "🛠️ EVET: İndir ve H.264 formatına dönüştür (Uzun sürer)\n"
                        "⚡ HAYIR: Olduğu gibi (VP9) indir\n"
                        "❌ İPTAL: İşlemi iptal et"
                    )
                    
                    if cevap is None: return 
                    elif cevap: self.donusturme_yapilsin_mi = True
                    else: self.donusturme_yapilsin_mi = False
            except: pass

        self.download_button.config(text="İPTAL ET ❌", bg="#d9534f", state='normal')
        self.progress['value'] = 0
        threading.Thread(target=self.indir_gorevi, args=(url,)).start()

    def iptal_et(self):
        cevap = messagebox.askyesno("İptal", "İndirme işlemini durdurmak istiyor musunuz?")
        if cevap:
            self.iptal_bayragi = True
            self.log_yaz("⚠️ İptal sinyali gönderildi, durduruluyor...")
            self.download_button.config(state='disabled')

    def indir_gorevi(self, url):
        import yt_dlp
        self.log_yaz(f"--- İndirme Başlıyor (v2.0) ---")
        
        ffmpeg_exe = self.dosya_yolu_bul("ffmpeg.exe")
        kayit_yolu = self.kayit_yeri.get()
        format_tipi = self.format_secimi.get()
        out_tmpl = os.path.join(kayit_yolu, "%(title)s.%(ext)s")

        ydl_opts = {
            'outtmpl': out_tmpl,
            'ffmpeg_location': ffmpeg_exe,
            'noplaylist': not self.playlist_modu,
            'progress_hooks': [self.progress_hook],
            'quiet': True,
            'no_warnings': True,
        }

        if format_tipi == "mp3":
            self.log_yaz("Mod: Sadece Ses (MP3)")
            ydl_opts.update({
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            })
        else:
            kalite = self.kalite_secimi.get()
            self.log_yaz(f"Mod: Video ({kalite}p)")
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
                ydl.download([url])
            
            if not self.iptal_bayragi:
                # Dönüştürme Kontrolü
                if self.donusturme_yapilsin_mi and self.son_indirilen_dosya and os.path.exists(self.son_indirilen_dosya):
                    self.donusturme_islemi(self.son_indirilen_dosya, ffmpeg_exe)
                
                # Başarılı Bitiş UI
                self.root.after(0, lambda: self.islem_tamamlandi_ui(kayit_yolu))

        except Exception as e:
            if "İptal Edildi" in str(e):
                self.log_yaz("🛑 İşlem kullanıcı tarafından iptal edildi.")
                self.progress['value'] = 0
                self.root.after(0, self.buton_sifirla)
            else:
                self.log_yaz(f"❌ HATA: {str(e)}")
                self.root.after(0, self.buton_sifirla)

    def progress_hook(self, d):
        if self.iptal_bayragi:
            raise Exception("İptal Edildi")

        if d['status'] == 'downloading':
            try:
                p = d.get('_percent_str', '0%').replace('%','')
                self.progress['value'] = float(p)
                self.root.update_idletasks()
            except: pass
            
        elif d['status'] == 'finished':
            self.son_indirilen_dosya = d.get('filename')
            self.log_yaz("⬇️ İndirme bitti, son işlemler yapılıyor...")

    def donusturme_islemi(self, dosya_yolu, ffmpeg_exe):
        self.log_yaz("⏳ DÖNÜŞTÜRME BAŞLIYOR (MP4/H.264)...")
        # UI Güncellemeleri
        self.root.after(0, lambda: self.download_button.config(text="DÖNÜŞTÜRÜLÜYOR..."))
        self.root.after(0, lambda: self.progress.config(mode='indeterminate'))
        self.root.after(0, lambda: self.progress.start(10))

        klasor = os.path.dirname(dosya_yolu)
        dosya_adi = os.path.basename(dosya_yolu)
        yeni_dosya_adi = "CONVERTED_" + dosya_adi
        yeni_dosya_yolu = os.path.join(klasor, yeni_dosya_adi)

        komut = [
            ffmpeg_exe, "-y", 
            "-i", dosya_yolu, 
            "-c:v", "libx264", "-preset", "fast", "-crf", "23", 
            "-c:a", "copy", 
            yeni_dosya_yolu
        ]

        try:
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            # Thread içinde çalıştır ama konsol penceresi açma
            subprocess.run(komut, stdout=subprocess.PIPE, stderr=subprocess.PIPE, startupinfo=startupinfo, creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0)

            if os.path.exists(yeni_dosya_yolu):
                os.remove(dosya_yolu) 
                os.rename(yeni_dosya_yolu, dosya_yolu) 
                self.log_yaz("✅ DÖNÜŞTÜRME TAMAMLANDI.")
            else:
                self.log_yaz("❌ Dönüştürme dosyası oluşturulamadı.")
        except Exception as e:
            self.log_yaz(f"Dönüştürme Hatası: {str(e)}")

        # Progress bar düzelt
        self.root.after(0, lambda: self.progress.stop())
        self.root.after(0, lambda: self.progress.config(mode='determinate'))

    def islem_tamamlandi_ui(self, kayit_yolu):
        self.buton_sifirla()
        self.log_yaz("✅ İŞLEM BAŞARIYLA TAMAMLANDI.")
        self.progress['value'] = 100
        messagebox.showinfo("Başarılı", "İndirme Tamamlandı!")
        if self.klasor_ac_var.get(): 
            try: os.startfile(kayit_yolu)
            except: pass

if __name__ == "__main__":
    root = tk.Tk()
    app = YSVideoDownloader(root)
    root.mainloop()