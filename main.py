import tkinter as tk
from tkinter import messagebox, scrolledtext, filedialog, ttk
import subprocess
import threading
import os
import sys
import re
import json
import time

# PROJE: Video Downloader v1.0 (Final Optimized)
# YENİLİK: Playlist analizi engellendi (--no-playlist), analiz hızı artırıldı.

class VideoIndiriciV3:
    def __init__(self, root):
        self.root = root
        self.root.title("YS Video Downloader v1.0")
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

        # URL İzleyici
        self.url_var.trace_add("write", self.on_url_change)

        self.ikon_yukle()
        self.arayuz_olustur()

    def ikon_yukle(self):
        icon_path = self.dosya_yolu_bul("logo.ico")
        if os.path.exists(icon_path):
            try: self.root.iconbitmap(icon_path)
            except: pass

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

        tk.Label(self.root, text="©YS v1.0 - 2026", fg="gray", font=("Segoe UI", 8)).pack(side=tk.BOTTOM, pady=5)

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

    def analizi_baslat(self):
        url = self.url_var.get().strip()
        if not url: return

        self.lbl_analiz_durum.config(text="Analiz ediliyor...", fg="#666666")
        self.download_button.config(text="ANALİZ EDİLİYOR...", bg="#999999")
        
        threading.Thread(target=self.analiz_thread, args=(url,)).start()

    def analiz_thread(self, url):
        yt_dlp_exe = self.dosya_yolu_bul("yt-dlp.exe")
        
        # HIZLANDIRMA GÜNCELLEMESİ YAPILDI
        komut = [
            yt_dlp_exe, 
            "--dump-json", 
            "--no-warnings", 
            "--no-playlist",      # Playlist kontrolünü kapat (Hızlandırır)
            "--socket-timeout", "10", # 10sn zaman aşımı
            url
        ]
        
        try:
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            result = subprocess.run(komut, capture_output=True, text=True, encoding='utf-8', startupinfo=startupinfo, creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0)
            
            if result.returncode == 0:
                metadata = json.loads(result.stdout)
                self.root.after(0, lambda: self.analiz_basarili(metadata))
            else:
                self.root.after(0, self.analiz_hatali)
        except Exception:
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

    def arayuz_guncelle(self):
        if self.format_secimi.get() == "mp3":
            self.rb_720.config(state="disabled")
            self.rb_1080.config(state="disabled")
            self.rb_4k.config(state="disabled")
        elif self.video_metadata:
            self.analiz_basarili(self.video_metadata) 

    def klasor_sec(self):
        klasor = filedialog.askdirectory()
        if klasor: self.kayit_yeri.set(klasor)

    def pano_yapistir(self):
        try:
            self.url_entry.delete(0, tk.END)
            self.url_entry.insert(0, self.root.clipboard_get())
        except: pass

    def log_yaz(self, mesaj):
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, mesaj + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state='disabled')

    def dosya_yolu_bul(self, dosya_adi):
        if getattr(sys, 'frozen', False):
            base_path = os.path.dirname(sys.executable)
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base_path, dosya_adi)

    def indirmeyi_baslat(self):
        url = self.url_var.get()
        self.donusturme_yapilsin_mi = False 

        # 4K VP9 KONTROLÜ
        if self.format_secimi.get() == "video" and self.kalite_secimi.get() == "2160":
            formats = self.video_metadata.get('formats', [])
            has_4k_h264 = False
            for f in formats:
                if f.get('height') == 2160 and f.get('vcodec', '').startswith('avc1'):
                    has_4k_h264 = True
                    break
            
            if not has_4k_h264:
                cevap = messagebox.askyesnocancel(
                    "Format Dönüştürme", 
                    "Bu 4K video VP9 formatındadır (Bazı Premiere sürümleri açmayabilir).\n\n"
                    "EVET: İndir ve Premiere uyumlu formata dönüştür (Uzun sürebilir)\n"
                    "HAYIR: Olduğu gibi indir (Dönüştürme yapma)\n"
                    "İPTAL: İşlemi iptal et"
                )
                
                if cevap is None: return
                elif cevap: self.donusturme_yapilsin_mi = True
                else: self.donusturme_yapilsin_mi = False

        self.download_button.config(state='disabled', text="İşlem Sürüyor...", bg="#999999")
        self.progress['value'] = 0
        threading.Thread(target=self.indir_gorevi, args=(url,)).start()

    def indir_gorevi(self, url):
        self.log_yaz(f"--- İndirme Başlıyor ---")
        yt_dlp_exe = self.dosya_yolu_bul("yt-dlp.exe")
        ffmpeg_exe = self.dosya_yolu_bul("ffmpeg.exe")
        kayit_yolu = self.kayit_yeri.get()

        komut = [yt_dlp_exe, url, "--ffmpeg-location", ffmpeg_exe, "--no-mtime"]
        komut.extend(["-o", os.path.join(kayit_yolu, "%(title)s.%(ext)s")])

        if self.format_secimi.get() == "mp3":
            self.log_yaz("Mod: Sadece Ses (MP3)")
            komut.extend(["-x", "--audio-format", "mp3"])
        else:
            kalite = self.kalite_secimi.get()
            self.log_yaz(f"Mod: Video ({kalite}p)")
            if kalite == "2160":
                komut.extend(["-f", f"bestvideo[height<={kalite}]+bestaudio/best[height<={kalite}]/best", "--merge-output-format", "mp4"])
            else:
                komut.extend(["-f", f"bestvideo[height<={kalite}][vcodec^=avc1]+bestaudio[ext=m4a]/best[ext=mp4]/best", "--merge-output-format", "mp4"])

        indirilen_dosya_yolu = None

        try:
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            process = subprocess.Popen(komut, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, startupinfo=startupinfo, creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0)

            while True:
                line = process.stdout.readline()
                if not line and process.poll() is not None: break
                
                if line:
                    line = line.strip()
                    match = re.search(r"(\d+\.\d+)%", line)
                    if match:
                        self.progress['value'] = float(match.group(1))
                        self.root.update_idletasks()
                    
                    if "Merger] Merging formats into" in line:
                         parts = line.split('"')
                         if len(parts) >= 2: indirilen_dosya_yolu = parts[1]

                    if "Destination" in line and not "Merger" in line:
                         parts = line.split(': ', 1)
                         if len(parts) >= 2: indirilen_dosya_yolu = parts[1].strip()

                    if "[download]" in line and "%" not in line: self.log_yaz(line)
                    elif "Destination" in line: self.log_yaz(line)

            if process.returncode == 0:
                self.progress['value'] = 100
                self.log_yaz("✅ İndirme Tamamlandı.")

                if self.donusturme_yapilsin_mi and indirilen_dosya_yolu and os.path.exists(indirilen_dosya_yolu):
                    self.donusturme_islemi(indirilen_dosya_yolu, ffmpeg_exe)
                else:
                    self.log_yaz("✅ İŞLEM BAŞARILI.")
                    if self.klasor_ac_var.get(): os.startfile(kayit_yolu)
                    messagebox.showinfo("Başarılı", "İşlem Tamamlandı!")
            else:
                self.log_yaz("❌ HATA OLUŞTU.")
        except Exception as e: self.log_yaz(f"Hata: {str(e)}")
        
        self.download_button.config(state='normal', text="İNDİRMEYİ BAŞLAT", bg="#0078D7")

    def donusturme_islemi(self, dosya_yolu, ffmpeg_exe):
        self.log_yaz("⏳ DÖNÜŞTÜRME BAŞLIYOR (Bu işlem uzun sürebilir)...")
        self.download_button.config(text="DÖNÜŞTÜRÜLÜYOR...")
        self.progress.config(mode='indeterminate')
        self.progress.start(10)

        klasor = os.path.dirname(dosya_yolu)
        dosya_adi = os.path.basename(dosya_yolu)
        yeni_dosya_adi = "CONVERTED_" + dosya_adi
        yeni_dosya_yolu = os.path.join(klasor, yeni_dosya_adi)

        komut = [ffmpeg_exe, "-y", "-i", dosya_yolu, "-c:v", "libx264", "-preset", "fast", "-crf", "23", "-c:a", "copy", yeni_dosya_yolu]

        try:
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            subprocess.run(komut, stdout=subprocess.PIPE, stderr=subprocess.PIPE, startupinfo=startupinfo, creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0)

            if os.path.exists(yeni_dosya_yolu):
                os.remove(dosya_yolu) 
                os.rename(yeni_dosya_yolu, dosya_yolu) 
                self.log_yaz("✅ DÖNÜŞTÜRME TAMAMLANDI (Premiere Uyumlu).")
            else: self.log_yaz("❌ Dönüştürme dosyası oluşturulamadı.")
        except Exception as e: self.log_yaz(f"Dönüştürme Hatası: {str(e)}")

        self.progress.stop()
        self.progress.config(mode='determinate')
        self.progress['value'] = 100
        if self.klasor_ac_var.get(): os.startfile(klasor)
        messagebox.showinfo("Başarılı", "İndirme ve Dönüştürme Tamamlandı!")

if __name__ == "__main__":
    root = tk.Tk()
    app = VideoIndiriciV3(root)
    root.mainloop()