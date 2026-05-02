# Raspberry Pi Docker Kurulum ve Yapılandırma Rehberi
### Versiyon: 2026.05.01 (v18)

## İçindekiler
1. [Sistem Mimarisi](#1-sistem-mimarisi)
2. [Docker CE Kurulumu](#2-docker-ce-kurulumu)
3. [Docker Network ve Cloudflared](#3-docker-network-ve-cloudflared)
4. [Filebrowser](#4-filebrowser)
5. [Firefox Remote Browser](#5-firefox-remote-browser)
6. [Portainer](#6-portainer)
7. [Yedekleme Sistemi](#7-yedekleme-sistemi)
8. [Test ve Sorun Giderme](#8-test-ve-sorun-giderme)
9. [Sistem Monitoring ve Güncelleme](#9-sistem-monitoring-ve-güncelleme)
  - [Uptime Kuma Kurulumu](#91-uptime-kuma-kurulumu)
  - [Monitoring ve Güncelleme Kontrolleri](#93-monitoring-ve-güncelleme-kontrolleri)
10. [İleri Seviye Yapılandırmalar](#10-ileri-seviye-yapılandırmalar)

## 1. Sistem Mimarisi
Bu yapı, Docker servisleri ve sık erişilen veriler için yüksek performanslı bir SSD kullanırken, büyük medya dosyaları ve yedekler için ise yüksek kapasiteli bir HDD kullanır. Bu sayede HDD'nin gereksiz yere çalışması engellenir ve ömrü uzatılır.

### 1.1 Dizin Yapısı
SSD (ext500gb): Docker servisleri, yapılandırmaları ve yedekleri burada tutulur.
HDD (ext4tb): Büyük ve daha az sıklıkla erişilen paylaşılan dosyalar burada tutulur.
```
/mnt/
├── ext4tb/
│   └── _shared/                # Medya ve paylaşılan dosyalar (HDD)
│       ├── _gdrive/
│       ├── _media/
│       ├── _public/
│       └── _software/
└── ext500gb/
    ├── _backup/
    │   └── docker_backup/      # Otomatik Docker yedekleri (SSD)
    └── docker/                 # Tüm Docker servisleri (SSD)
        ├── cloudflared/
        ├── filebrowser/
        ├── firefox/
        ├── portainer/
        └── uptime-kuma/
```

### 1.2 Disk Yapılandırması
```bash
# Disk UUID öğren
sudo blkid

# /etc/fstab yapılandırması
sudo nano /etc/fstab
# Ekle:
UUID=<disk_uuid> /mnt/ext500gb/ ext4 defaults,auto,nofail,noatime,nodiratime 0 0
UUID=<disk_uuid> /mnt/ext4tb/ ext4 defaults,auto,nofail,noatime,nodiratime 0 0

# fstab'deki ayarları uygulamak için diskleri bağla
sudo mount -a

# Dizin oluştur ve izinleri ayarla
sudo mkdir -p /mnt/ext500gb
sudo mkdir -p /mnt/ext4tb
sudo chown -R $USER:$USER /mnt/ext500gb
sudo chown -R $USER:$USER /mnt/ext4tb
sudo chmod -R 755 /mnt/ext500gb
sudo chmod -R 755 /mnt/ext4tb

# Gerekli alt dizin yapısını oluştur
mkdir -p /mnt/ext500gb/docker/{cloudflared,filebrowser,firefox,portainer,uptime-kuma}
mkdir -p /mnt/ext500gb/_backup/docker_backup
mkdir -p /mnt/ext4tb/_shared/{_gdrive,_media,_public,_software}

# İzinlerin tüm alt dizinlere uygulandığından emin ol
sudo chown -R $USER:$USER /mnt/ext500gb
sudo chown -R $USER:$USER /mnt/ext4tb
```

### 1.3 İzin Yönetimi

#### 1.3.1 Temel İzinler
- Dizinler için: 755 (rwxr-xr-x)
- Dosyalar için: 644 (rw-r--r--)
- Hassas dosyalar (.env, token vb.) için: 600 (rw-------)

#### 1.3.2 Özel İzinler
```bash
# Hassas dosyalar için
find /mnt/ext500gb/docker -name ".env" -exec chmod 600 {} \;
find /mnt/ext500gb/docker -name "*.key" -exec chmod 600 {} \;
find /mnt/ext500gb/docker -name "*.pem" -exec chmod 600 {} \;

# Database dosyaları için
find /mnt/ext500gb/docker -name "database.db" -exec chmod 644 {} \;
```

#### 1.3.3 Sahiplik
```bash
# Tüm dizin ve dosyaların sahipliğini ayarla
sudo chown -R $USER:$USER /mnt/ext500gb/docker
sudo chown -R $USER:$USER /mnt/ext4tb/_shared
```

### 1.4 Temizlik ve Bakım
```bash
# Gereksiz dosyaları temizle
find /mnt/ext500gb/docker -name ".DS_Store" -delete
find /mnt/ext500gb/docker -name "._.DS_Store" -delete
```

Not(eski): Bu rehber v12'nin devamı niteliğindedir ve yeni özellikler, optimizasyonlar ve güvenlik önlemleri eklenmiştir. Özellikle memory/swap yönetimi, buffer size optimizasyonları ve hassas bilgi yönetimi konularında önemli güncellemeler içermektedir.

## 2. Docker CE Kurulumu

### 2.1 Repository Hazırlığı
```bash
# Sistem güncellemesi
sudo apt update && sudo apt upgrade -y

# Docker GPG anahtarı ve repo ekle
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

# Docker repository ekle
echo \
"deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian \
"$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | \
sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```

### 2.2 Docker Kurulumu
```bash
# Docker CE ve gerekli paketleri kur
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Kullanıcıyı docker grubuna ekle
sudo usermod -aG docker $USER
newgrp docker

# Docker servisini etkinleştir ve başlat
sudo systemctl enable docker
sudo systemctl start docker
```

### 2.3 Network ve Buffer Optimizasyonları

#### 2.3.1 QUIC/UDP Buffer Size Ayarları
```bash
sudo tee /etc/sysctl.d/99-cloudflared.conf << EOF
# QUIC/UDP Buffer Sizes
net.core.rmem_max=8388608
net.core.wmem_max=8388608
net.core.rmem_default=4194304
net.core.wmem_default=4194304

# TCP Buffer Sizes
net.ipv4.tcp_rmem=4096 87380 8388608
net.ipv4.tcp_wmem=4096 87380 8388608
net.ipv4.udp_mem=8388608 8388608 8388608

# Max Backlog
net.core.netdev_max_backlog=5000

# TCP Optimization
net.ipv4.tcp_fastopen=3
net.ipv4.tcp_slow_start_after_idle=0
EOF

# Ayarları uygula
sudo sysctl -p /etc/sysctl.d/99-cloudflared.conf

# Sistem yeniden başlatıldığında ayarların kalıcı olması için
echo "@reboot sysctl -p /etc/sysctl.d/99-cloudflared.conf" | sudo tee -a /etc/crontab
```

#### 2.3.2 Buffer Size Kontrolü
```bash
# Mevcut buffer size değerlerini kontrol et
sysctl net.core.rmem_max
sysctl net.core.wmem_max
sysctl net.core.rmem_default
sysctl net.core.wmem_default

# Network parametrelerini kontrol et
sysctl -a | grep "net.core"
```

#### 2.3.3 Optimizasyon Notları
- QUIC protokolü için önerilen minimum buffer size: 7168 KiB
- UDP buffer size optimizasyonu Cloudflare tünel performansını artırır
- Buffer size değerleri sistem belleğinden tahsis edilir
- Default değerler ihtiyaç duyulmadıkça kullanılmaz
- Raspberry Pi 4GB RAM için bu değerler uygundur

#### 2.3.4 Sorun Giderme
```bash
# Buffer size yetersizlik kontrolü
docker logs cloudflared | grep "buffer size"

# Memory kullanımı kontrolü
free -h
vmstat 1 5

# Network performans kontrolü
netstat -s | grep "buffer"
```

### 2.4 Memory ve Swap Limitleri

#### 2.4.1 Boot Parametreleri
```bash
# Boot parametrelerini düzenle
sudo nano /boot/firmware/cmdline.txt

# Mevcut satırın sonuna bir boşluk bırakarak ekle:
cgroup_enable=memory cgroup_memory=1 swapaccount=1

# Sistemi yeniden başlat
sudo reboot
```

#### 2.4.2 Buffer Size Optimizasyonu
Buffer size uyarısını çözmek için:
```bash
# Mevcut buffer size limitlerini kontrol et
sysctl net.core.rmem_max
sysctl net.core.wmem_max

# Buffer size limitlerini artır
sudo tee /etc/sysctl.d/99-docker-network.conf << EOF
net.core.rmem_max=2500000
net.core.wmem_max=2500000
EOF

# Değişiklikleri uygula
sudo sysctl -p /etc/sysctl.d/99-docker-network.conf
```

### 2.4 Docker Compose Yapılandırması

#### 2.4.1 Önemli Not: Version Attribute
Docker Compose'un yeni sürümlerinde `version` attribute'u kullanımdan kaldırılmıştır. docker-compose.yml dosyalarında version belirtmeyin:

```yaml
# ESKİ (Kullanmayın):
version: '3'
services:
  ...

# YENİ (Bunu kullanın):
services:
  ...
```

#### 2.4.2 Network Yapılandırması
Docker Compose dosyalarında network tanımlaması:
```yaml
networks:
  raspi_network:
    external: true
    name: raspi_network
```

### 2.5 Test ve Doğrulama
```bash
# Docker versiyonlarını kontrol et
docker --version
docker compose version

# Docker yetki testi
docker info | grep -i "server version"
docker info | grep -i "warning"  # Memory/swap uyarıları olmamalı
groups | grep docker

# Network buffer size kontrolü
sysctl net.core.rmem_max
sysctl net.core.wmem_max

# Sorun varsa:
# 1. docker.io kurulmuşsa:
sudo apt remove docker.io
# 2. Docker CE kurulum adımlarını tekrarla
```

### 2.6 Güvenlik Ayarları

#### 2.6.1 Docker Socket İzinleri
```bash
# Docker socket izinlerini ayarla
sudo chmod 666 /var/run/docker.sock

# Docker grubunu kontrol et
getent group docker
```

#### 2.6.2 Registry Güvenliği
```bash
# Güvenli registry yapılandırması
sudo nano /etc/docker/daemon.json
```

daemon.json içeriği:
```json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  },
  "experimental": false,
  "live-restore": true
}
```

### 2.7 Log Yönetimi

#### 2.7.1 Log Rotasyonu
```bash
# Log yapılandırması
sudo nano /etc/docker/daemon.json
```

Log rotasyonu için daemon.json:
```json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
```

#### 2.7.2 Log Temizliği
```bash
# Eski logları temizle
sudo sh -c 'truncate -s 0 /var/lib/docker/containers/*/*-json.log'
```

### 2.8 Sorun Giderme

#### 2.8.1 Docker Servisi
```bash
# Servis durumunu kontrol et
sudo systemctl status docker

# Logları kontrol et
sudo journalctl -u docker
```

#### 2.8.2 Grup İzinleri
```bash
# Kullanıcı gruplarını kontrol et
groups $USER

# Docker grubuna yeniden ekle
sudo usermod -aG docker $USER
newgrp docker
```

#### 2.8.3 Memory/Swap Sorunları
```bash
# Memory limitleri kontrolü
docker info | grep -i "warning"

# Swap durumu
free -h

# cgroup durumu
grep cgroup /proc/mounts
```

Not: Bu bölümde memory/swap limitleri, buffer size optimizasyonları ve Docker Compose'un yeni versiyon yaklaşımı gibi önemli güncellemeler eklenmiştir. Özellikle buffer size optimizasyonu, network performansını artırmak için kritik bir iyileştirmedir.

## 3. Docker Network ve Cloudflared

### 3.1 Network Oluşturma
```bash
# Merkezi ağı oluştur
docker network create raspi_network

# Network kontrolü
docker network ls | grep raspi_network
docker network inspect raspi_network
```

### 3.2 Cloudflared Yapılandırması

#### 3.2.1 Dizin Yapısı
```bash
cd /mnt/ext500gb/docker/cloudflared
mkdir -p config
chmod 755 config
```

#### 3.2.2 Docker Compose
```bash
nano docker-compose.yml
```

docker-compose.yml:
```yaml
services:
  cloudflared:
    image: cloudflare/cloudflared:latest
    container_name: raspi_cloudflared
    restart: always
    command: tunnel run
    volumes:
      - /mnt/ext500gb/docker/cloudflared/config:/home/nonroot/.cloudflared # <-- GÜNCELLENDİ
    environment:
      - TUNNEL_TOKEN=${TUNNEL_TOKEN}
    networks:
      - raspi_network

networks:
  raspi_network:
    external: true
    name: raspi_network
```

#### 3.2.3 Hassas Bilgi Yönetimi
```bash
# .env dosyası oluştur
cd /mnt/ext500gb/docker/cloudflared
echo "TUNNEL_TOKEN=your_tunnel_token" > .env

# İzinleri ayarla
chmod 600 .env
```

### 3.3 Cloudflare Tunnel Yapılandırması

#### 3.3.1 Tünel Oluşturma
1. Cloudflare Zero Trust Dashboard'a git
2. Networks > Tunnels > Create a tunnel
3. Tunnel name: "raspi"
4. Copy tunnel token

#### 3.3.2 Tünel Konfigürasyonu
- Networks > Tunnels > Public Hostnames
- Her servis için DNS kaydı ve tünel yapılandırması:

| Hostname | Service | TLS |
|----------|---------|-----|
| portainer.domain.com | https://portainer:9443 | No TLS Verify |
| web.domain.com | https://firefox:5800 | No TLS Verify |
| files.domain.com | http://filebrowser:80 | - |
| webdav.domain.com | http://webdav:80 | - |

### 3.4 Network ve Tünel Optimizasyonları

#### 3.4.1 QUIC Buffer Size
```bash
# QUIC buffer size ayarları
sudo tee /etc/sysctl.d/99-cloudflared.conf << EOF
net.core.rmem_max=2500000
net.core.wmem_max=2500000
EOF

# Ayarları uygula
sudo sysctl -p /etc/sysctl.d/99-cloudflared.conf
```

#### 3.4.2 DNS Optimizasyonu
```bash
# DNS çözümlemesi için
sudo tee /etc/docker/daemon.json << EOF
{
  "dns": ["1.1.1.1", "1.0.0.1"],
  "dns-opts": ["use-vc"],
  "dns-search": []
}
EOF

# Docker daemon'ı yeniden başlat
sudo systemctl restart docker
```

### 3.5 Güvenlik Yapılandırması

#### 3.5.1 Zero Trust Politikaları
1. Access > Applications
2. Add Application
3. Self-hosted
4. Configure:
   - App domain: domain.com
   - Subdomain: service
   - Path: /* (tüm yollar)

#### 3.5.2 SSL/TLS Yapılandırması
1. SSL/TLS > Origin Server
2. Create Certificate
3. Origin Certificate seç
4. Sertifikayı indir ve yapılandır

### 3.6 İzleme ve Log Yönetimi

#### 3.6.1 Cloudflared Logları
```bash
# Log kontrolü
docker logs raspi_cloudflared

# Log filtreleme
docker logs raspi_cloudflared | grep "error"
docker logs raspi_cloudflared | grep "Registered tunnel"
```

#### 3.6.2 Network Logları
```bash
# Network kontrolü
docker network inspect raspi_network

# Container bağlantıları
docker inspect cloudflared | grep -A 20 "Networks"
```

### 3.7 Sorun Giderme

#### 3.7.1 Tünel Bağlantı Sorunları
```bash
# Cloudflared durumu
docker ps | grep cloudflared

# Detaylı loglar
docker logs raspi_cloudflared --tail 100

# Tünel yeniden başlatma
docker compose restart cloudflared
```

#### 3.7.2 Network Sorunları
```bash
# Network durumu
docker network ls
docker network inspect raspi_network

# DNS çözümleme
docker exec raspi_cloudflared nslookup portainer
docker exec raspi_cloudflared nslookup firefox
```

#### 3.7.3 Sık Karşılaşılan Hatalar

1. "Unable to reach the origin service"
```bash
# Container erişilebilirliği
docker exec raspi_cloudflared ping -c 1 portainer
docker exec raspi_cloudflared ping -c 1 firefox

# Service DNS kaydı
docker exec raspi_cloudflared dig portainer
```

2. "Connection refused"
```bash
# Port erişilebilirliği
docker exec raspi_cloudflared nc -zv portainer 9443
docker exec raspi_cloudflared nc -zv firefox 5800
```

3. "SSL/TLS error"
```bash
# TLS durumu
docker exec raspi_cloudflared openssl s_client -connect portainer:9443
```

### 3.8 Bakım ve İzleme

#### 3.8.1 Periyodik Kontroller
```bash
# Tünel durumu
docker logs --since 1h raspi_cloudflared

# Network durumu
docker network inspect raspi_network

# Container sağlığı
docker ps -a
```

#### 3.8.2 Performans İzleme
```bash
# Network istatistikleri
docker stats raspi_cloudflared

# Buffer size kontrolü
sysctl net.core.rmem_max
sysctl net.core.wmem_max
```

Not: Bu bölümde tünel yönetimi, network optimizasyonları ve sorun giderme konularında önemli güncellemeler yapılmıştır. Özellikle buffer size ayarları ve DNS optimizasyonları, bağlantı performansını artırmak için kritik öneme sahiptir.##

## 4. Filebrowser
Filebrowser, web arayüzü üzerinden dosya yönetimi yapmamızı sağlayan hafif bir servistir. Yapılandırma dosyaları yeni SSD'de tutulurken, hizmet edeceği büyük dosyalar ana HDD'de kalacaktır.

### 4.1 Dizin Yapısı
Filebrowser'ın yapılandırma dosyalarını barındıracak klasörleri yeni SSD üzerinde oluşturalım.
```bash
cd /mnt/ext500gb/docker/filebrowser
mkdir -p config
sudo chown -R $USER:$USER config
chmod 755 config
```
#### 4.2 Database Oluşturma
Filebrowser'ın ayarlarını ve kullanıcı bilgilerini tutacağı veritabanı dosyasını oluşturalım.
```bash
# Database oluştur (Bu komutu çalıştırmadan önce /mnt/ext500gb/docker/filebrowser dizininde olduğunuzdan emin olun.)
docker run --rm -v $(pwd)/config:/config filebrowser/filebrowser:latest -d /config/database.db
chmod 644 config/database.db
```

### 4.3 Docker Compose
```bash
nano docker-compose.yml
```

docker-compose.yml:
```yaml
services:
  filebrowser:
    image: filebrowser/filebrowser:latest
    container_name: filebrowser
    restart: unless-stopped
    ports:
      - "8334:80"
    volumes:
      # Paylaşılan büyük dosyalar için HDD'deki yolu gösterir.
      - /mnt/ext4tb/_shared:/srv
      # Yapılandırma dosyaları için SSD'deki göreceli yolu kullanır.
      - ./config:/config
    environment:
      - FB_DATABASE=/config/database.db
      - FB_ROOT=/srv
      - PUID=1000
      - PGID=1000
    user: "1000:1000"
    networks:
      - raspi_network

networks:
  raspi_network:
    external: true
    name: raspi_network
```
Not: restart politikası, bu servisi sadece ihtiyaç duyduğunuzda Portainer üzerinden başlatacağınız için unless-stopped olarak güncellenmiştir. Eğer sürekli çalışmasını isterseniz always yapabilirsiniz.

### 4.4 İzin ve Güvenlik Yapılandırması
```bash
# Filebrowser'ın kendi yapılandırma dosyaları için (SSD üzerinde)
chmod 755 /mnt/ext500gb/docker/filebrowser
chmod 755 /mnt/ext500gb/docker/filebrowser/config
chmod 644 /mnt/ext500gb/docker/filebrowser/config/database.db
sudo chown -R $USER:$USER /mnt/ext500gb/docker/filebrowser

# Filebrowser'ın hizmet edeceği paylaşılan klasör için (HDD üzerinde)
chmod 755 /mnt/ext4tb/_shared
sudo chown -R $USER:$USER /mnt/ext4tb/_shared
```

### 4.5 Cloudflare Tunnel Yapılandırması
Networks > Tunnels > Public Hostnames:
- Hostname: files.sonmezer.tr
- Service: http://filebrowser:80

### 4.6 Erişim ve Test

#### 4.6.1 Local Erişim
```bash
# Filebrowser web arayüzü testi
curl -I http://192.168.8.232:8334
```

#### 4.6.2 Cloudflare Tünel Testi
Web tarayıcıdan files.sonmezer.tr adresine erişin

### 4.7 Sorun Giderme

#### 4.7.1 İzin Sorunları
```bash
# Dizin izinlerini düzelt
sudo chown -R $USER:$USER /mnt/ext4tb/docker/filebrowser
find /mnt/ext4tb/docker/filebrowser -type f -exec chmod 644 {} \;
find /mnt/ext4tb/docker/filebrowser -type d -exec chmod 755 {} \;

# Hassas dosya izinlerini düzelt
chmod 600 .env
chmod 644 config/database.db
```
#### 4.7.2 Bağlantı Sorunları
```bash
# Filebrowser log kontrolü
docker logs filebrowser
```

### 4.8 Bakım ve İzleme

#### 4.8.1 Log Yönetimi
```bash
# Son 100 log satırı
docker logs --tail 100 filebrowser > filebrowser_latest.log

# Belirli bir süredeki loglar
docker logs --since 1h filebrowser
```

#### 4.8.2 Performans İzleme
```bash
# Disk kullanımı
du -sh /mnt/ext4tb/_shared/*
```

#### 4.8.3 Periyodik Bakım
Yapılandırmayı Sıfırlama (Dikkatli Kullanın):** Eğer ayarlarınızda bir sorun olursa, aşağıdaki komutla Filebrowser yapılandırmasını ilk haline döndürebilirsiniz.
```bash
# Database bakımı
docker exec filebrowser /filebrowser -d /config/database.db config init

# Önbellek temizleme
docker exec filebrowser rm -rf /tmp/*
```

## 5. Firefox Remote Browser
Bu servis, Docker üzerinde uzak bir web tarayıcısı çalıştırmanıza olanak tanır. Bu yapılandırma, harici diskin sürekli çalışmasını engelleyecek şekilde yapılan optimizasyonları içerir ve sadece ihtiyaç anında çalıştırılması önerilir.

### 5.1 Dizin Hazırlığı
```bash
cd /mnt/ext500gb/docker/firefox
mkdir -p {config,data}
sudo chown -R $USER:$USER {config,data}
chmod 755 config data
```

### 5.2 Docker Compose
docker-compose.yml:
```yaml
services:
  firefox:
    image: jlesage/firefox:latest
    container_name: firefox
    restart: unless-stopped
    ports:
      - "5800:5800"
    volumes:
      # Yollar yeni SSD konumuna göre mutlak olarak güncellendi
      - /mnt/ext500gb/docker/firefox/config:/config
      - /mnt/ext500gb/docker/firefox/data:/data
    environment:
      - PUID=1000
      - PGID=1000
      - TZ=Europe/Istanbul
      - DISPLAY_WIDTH=1920
      - DISPLAY_HEIGHT=1080
      - SECURE_CONNECTION=1
      - KEEP_APP_RUNNING=1
      - ENABLE_CJK_FONT=0
    security_opt:
      - no-new-privileges:true
    shm_size: "2gb"
    mem_limit: 2048m
    mem_reservation: 512m
    networks:
      - raspi_network

networks:
  raspi_network:
    external: true
    name: raspi_network
```

### 5.3 Yapılandırma Parametreleri

#### 5.3.1 Görüntü Ayarları
- DISPLAY_WIDTH: Ekran genişliği (1920)
- DISPLAY_HEIGHT: Ekran yüksekliği (1080)
- VNC_RESIZE_MODE: "scale" (otomatik ölçeklendirme)

#### 5.3.2 Güvenlik Ayarları
- SECURE_CONNECTION: SSL/TLS kullan (1)
- USER_ID: Container kullanıcı ID (1000)
- GROUP_ID: Container grup ID (1000)
- CLEAN_TMP_DIR: Her başlangıçta /tmp temizliği (1)

#### 5.3.3 Performans Ayarları
- shm_size: Paylaşılan bellek boyutu (2gb)
- mem_limit: Maksimum bellek kullanımı (2048m)
- mem_reservation: Minimum bellek rezervasyonu (512m)

### 5.4 İzin ve Güvenlik Yapılandırması

```bash
# Ana Firefox klasörü ve alt klasörlerin sahipliğini ayarla
# Not: chown komutunu en başta çalıştırmak, alttaki chmod komutlarının doğru kullanıcı için uygulanmasını sağlar.
sudo chown -R 1000:1000 /mnt/ext500gb/docker/firefox/config
sudo chown -R 1000:1000 /mnt/ext500gb/docker/firefox/data

# Profil ve veri klasörlerine sadece sahip kullanıcının erişebilmesi için izinleri ayarla (Güvenli)
chmod 700 /mnt/ext500gb/docker/firefox/config
chmod 700 /mnt/ext500gb/docker/firefox/data

# Not: Aşağıdaki komutlar, Firefox ilk kez çalıştırılıp .db dosyaları oluşturulduktan sonra periyodik olarak çalıştırılabilir.
# Hassas veritabanı dosyalarının izinlerini en kısıtlı hale getir (Çok Güvenli)
find /mnt/ext500gb/docker/firefox/config -name "key*.db" -exec chmod 600 {} \;
find /mnt/ext500gb/docker/firefox/config -name "cert*.db" -exec chmod 600 {} \;
```

### 5.5 Cloudflare Tunnel Yapılandırması

#### 5.5.1 Tünel Ayarları
Networks > Tunnels > Public Hostnames:
1. Hostname: web.sonmezer.tr
2. Service:
   - Type: HTTPS
   - URL: https://firefox:5800
3. Additional application settings:
   - TLS > No TLS Verify: Enabled

#### 5.5.2 Güvenlik Politikaları
1. Access > Applications:
   - Policy name: Firefox Remote Access
   - Session duration: 24 hours
   - Additional requirements:
     - Country: TR
     - Authentication: Cloudflare Zero Trust

### 5.6 Firefox Profil Yapılandırması

#### 5.6.1 Performans Ayarları
about:config üzerinden:
```
browser.cache.disk.enable = false
browser.cache.memory.enable = true
browser.cache.memory.capacity = 524288
browser.sessionhistory.max_entries = 50
```

#### 5.6.2 Güvenlik Ayarları
about:config üzerinden:
```
privacy.resistFingerprinting = true
privacy.trackingprotection.enabled = true
network.cookie.cookieBehavior = 1
dom.security.https_only_mode = true
```
#### 5.6.3 Profil Temizliği (Yeni Bölüm)
Eğer kurulum sonrası eski önbellek dosyalarından kurtulmak isterseniz, Firefox konteyneri kapalıyken aşağıdaki komutla eski önbellek dosyalarını güvenle silebilirsiniz.

```bash
# Önce cache2 klasörünün tam yolunu bulalım
find /mnt/ext500gb/docker/firefox/ -name "cache2" -type d

# Yukarıdaki komutun verdiği yolu kullanarak cache2 klasörünü silelim
# Örnek: sudo rm -rf /mnt/ext500gb/docker/firefox/config/cache2
```
### 5.7 Test ve Doğrulama

#### 5.7.1 Servis Kontrolü
```bash
# Container durumu
docker ps | grep firefox

# Log kontrolü
docker logs firefox

# Port kontrolü
netstat -tuln | grep 5800
```

#### 5.7.2 Erişim Testleri
```bash
# Local erişim
curl -I http://192.168.8.232:5800

# SSL bağlantı testi
openssl s_client -connect 192.168.8.232:5800
```

### 5.8 Sorun Giderme
Uptime Kuma Monitörünün "Sahte Sağlıklı" Göstermesi: Eğer bu servisi Uptime Kuma ile izliyorsanız ve servis kapalıyken bile "sağlıklı" görünüyorsa, bunun nedeni Cloudflare'in döndürdüğü hata sayfasının Uptime Kuma'yı yanıltmasıdır. En güvenilir çözüm, monitör tipini "Push" olarak değiştirip, durumu yerel olarak (nc -z 127.0.0.1 5800 komutuyla) kontrol eden bir script ile Uptime Kuma'ya sinyal göndermektir.

#### 5.8.1 Performans Sorunları
```bash
# Bellek kullanımı
docker stats firefox

# CPU kullanımı
top -p $(docker inspect -f '{{.State.Pid}}' firefox)

# Disk I/O
docker exec firefox iostat
```

#### 5.8.2 Bağlantı Sorunları
```bash
# VNC log kontrolü
docker exec firefox cat /var/log/guacd.log

# SSL sertifika kontrolü
docker exec firefox openssl verify /config/ssl/firefox.crt

# Network bağlantı testi
docker exec firefox ping -c 4 google.com
```

#### 5.8.3 Profil Sorunları
```bash
# Firefox profilini sıfırla
docker exec firefox rm -rf /config/.mozilla/firefox/*.default

# Cache temizleme
docker exec firefox rm -rf /config/.cache/*
```

### 5.9 Bakım ve İzleme

#### 5.9.1 Rutin Bakım
```bash
# Container yeniden başlatma
docker compose restart firefox

# Log temizleme
> $(docker inspect --format='{{.LogPath}}' firefox)

# Önbellek temizleme
docker exec firefox rm -rf /tmp/*
```

#### 5.9.2 Performans İzleme
```bash
# Kaynak kullanımı izleme
docker stats firefox --no-stream

# Disk kullanımı
du -sh config/* data/*

# Network trafiği
iftop -i docker0
```

#### 5.9.3 Güvenlik Kontrolleri
```bash
# SSL sertifika geçerliliği
docker exec firefox openssl x509 -in /config/ssl/firefox.crt -noout -dates

# İzin kontrolü
find config data -type f -perm /o+w

# Network izolasyonu
docker inspect firefox --format '{{.NetworkSettings.Networks}}'
```

### 5.10 Özelleştirme ve İpuçları

#### 5.10.1 Klavye Kısayolları
- Ctrl+Alt+Shift+S: Ekran ayarları
- Ctrl+Alt+Shift+F: Tam ekran
- Ctrl+Alt+Shift+M: Fare göstergesini gizle/göster

#### 5.10.2 Performans İyileştirmeleri
1. Firefox önbellek ayarları:
   - about:config > browser.cache.memory.capacity
   - about:config > network.http.max-connections
2. Container kaynak limitleri:
   - mem_limit ve shm_size optimizasyonu
   - CPU paylaşımı ayarları

Not: Bu bölümde güvenlik yapılandırması, performans optimizasyonları ve sorun giderme konularında önemli güncellemeler yapılmıştır. Özellikle Firefox profil yönetimi ve sistem kaynak kullanımı detaylı şekilde ele alınmıştır.

## 6. Portainer

### 6.1 Dizin Yapısı
```bash
cd /mnt/ext500gb/docker/portainer
mkdir -p data
chmod 770 data
```

### 6.2 Docker Compose
```bash
nano docker-compose.yml
```

docker-compose.yml:
```yaml
services:
  portainer:
    image: portainer/portainer-ce:latest
    container_name: portainer
    restart: always
    security_opt:
      - no-new-privileges:true
    volumes:
      - /etc/localtime:/etc/localtime:ro
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - /mnt/ext500gb/docker/portainer/data:/data
    ports:
      - "9443:9443"
    networks:
      - raspi_network
    environment:
      - TZ=Europe/Istanbul
    healthcheck:
      test: ["CMD", "wget", "--no-verbose", "--tries=1", "--spider", "http://localhost:9000"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 30s

networks:
  raspi_network:
    external: true
    name: raspi_network
```

### 6.3 SSL/TLS Yapılandırması

#### 6.3.1 Sertifika Oluşturma
```bash
# Ana Portainer config dizinine gidin
cd /mnt/ext500gb/docker/portainer
# SSL dizini oluştur
mkdir -p data/certs
cd data/certs

# Özel anahtar oluştur
openssl genrsa -out portainer.key 2048
chmod 600 portainer.key

# CSR oluştur
openssl req -new -key portainer.key -out portainer.csr -subj "/C=TR/ST=Istanbul/L=Istanbul/O=Home/CN=portainer.sonmezer.tr"

# Sertifika oluştur
openssl x509 -req -days 365 -in portainer.csr -signkey portainer.key -out portainer.crt

# İzinleri ayarla
chmod 644 portainer.crt
```

### 6.4 Güvenlik Yapılandırması

#### 6.4.1 Docker Socket İzinleri
```bash
# Docker socket izinlerini kontrol et
ls -la /var/run/docker.sock

# Gerekirse düzelt
sudo chmod 660 /var/run/docker.sock
sudo chown root:docker /var/run/docker.sock
```

#### 6.4.2 Container Güvenliği
```bash
# No-new-privileges kontrolü
docker inspect portainer | grep -A 5 SecurityOpt

# Volume izinleri
ls -la data/
chmod 700 data/portainer.key
chmod 644 data/portainer.db
```

### 6.5 Cloudflare Tunnel Yapılandırması

#### 6.5.1 Tünel Ayarları
Networks > Tunnels > Public Hostnames:
- Hostname: portainer.sonmezer.tr
- Service: https://portainer:9443
- No TLS Verify: Enabled

#### 6.5.2 Zero Trust Politikaları
1. Access > Applications:
   - Policy name: Portainer Admin Access
   - Session duration: 12 hours
   - Additional requirements:
     - Country: TR
     - Device Posture: Up-to-date OS
     - Authentication: Cloudflare Zero Trust

### 6.6 İlk Yapılandırma

#### 6.6.1 Admin Hesabı
1. https://portainer.sonmezer.tr adresine git
2. Güçlü bir admin şifresi belirle
3. İki faktörlü doğrulamayı etkinleştir

#### 6.6.2 Güvenlik Ayarları
Settings > Security:
- Enable host management features: No
- Hide containers with specific labels: Yes
- Enable user management: Yes
- Use internal authentication: Yes

### 6.7 Test ve Doğrulama

#### 6.7.1 Servis Kontrolü
```bash
# Container durumu
docker ps | grep portainer

# Log kontrolü
docker logs portainer

# Port kontrolü
netstat -tuln | grep 9443
```

#### 6.7.2 SSL Testi
```bash
# SSL bağlantı testi
openssl s_client -connect localhost:9443

# Sertifika bilgileri
openssl x509 -in data/certs/portainer.crt -text -noout
```

### 6.8 Sorun Giderme

#### 6.8.1 Bağlantı Sorunları
```bash
# SSL hatası durumunda
docker exec portainer ls -la /data/certs
docker exec portainer openssl verify /data/certs/portainer.crt

# Port çakışması
netstat -tuln | grep 9443
sudo lsof -i :9443
```

#### 6.8.2 İzin Sorunları
```bash
# Docker socket
ls -la /var/run/docker.sock
sudo usermod -aG docker $(whoami)

# Data dizini
ls -la data/
sudo chown -R 1000:1000 data/
```

#### 6.8.3 Database Sorunları
```bash
# Database yedekleme
cp data/portainer.db data/portainer.db.bak

# Database onarımı (gerekirse)
docker stop portainer
rm data/portainer.db
docker start portainer
```

#### 6.8.4 Parola Sıfırlama (Yeni Ekleme)
Eğer Portainer admin parolanızı unutursanız, aşağıdaki adımlarla güvenli bir şekilde sıfırlayabilirsiniz:

Portainer konteynerini durdurun
```bash
cd /mnt/ext500gb/docker/portainer && sudo docker compose down
```
Parola sıfırlama aracını çalıştırın:
```bash
sudo docker run --rm -v /mnt/ext500gb/docker/portainer/data:/data portainer/portainer-ce:latest --reset-password
```
Portainer'ı yeniden başlatın
```bash
sudo docker compose up -d
```
Web arayüzüne gidip admin kullanıcısı için yeni bir şifre belirleyin.

### 6.9 Bakım ve İzleme

#### 6.9.1 Rutin Bakım
```bash
# Log temizleme
> $(docker inspect --format='{{.LogPath}}' portainer)

# SSL sertifika yenileme (yıllık)
cd data/certs
openssl x509 -req -days 365 -in portainer.csr -signkey portainer.key -out portainer.crt

# Container yeniden başlatma
docker compose restart portainer
```

#### 6.9.2 Performans İzleme
```bash
# Kaynak kullanımı
docker stats portainer

# Disk kullanımı
du -sh data/*

# Container sağlığı
docker inspect portainer | grep -A 10 Health
```

#### 6.9.3 Güvenlik Kontrolleri
```bash
# Sertifika geçerliliği
openssl x509 -in data/certs/portainer.crt -noout -dates

# İzin kontrolü
find data -type f -perm /o+w

# Log analizi
docker logs portainer --since 1h | grep -i error
```

### 6.10 İyi Uygulama Önerileri

#### 6.10.1 Güvenlik
1. Düzenli şifre değişimi
2. İki faktörlü doğrulama kullanımı
3. SSH anahtar tabanlı erişim
4. SSL sertifikalarının düzenli yenilenmesi

#### 6.10.2 Yedekleme
1. Düzenli database yedekleme
2. SSL sertifikalarının yedeklenmesi
3. Container yapılandırmalarının yedeklenmesi

#### 6.10.3 İzleme
1. Resource limitleri ayarlama
2. Log rotasyonu yapılandırma
3. Alarm ve bildirim ayarları

Not: Bu bölümde SSL/TLS yapılandırması, güvenlik ayarları ve bakım rutinleri detaylı şekilde ele alınmıştır. Özellikle Portainer'ın güvenli kullanımı ve düzenli bakımı için önemli güncellemeler eklenmiştir.

#### 6.11 Disk Uyku Modu Notu (Yeni Bölüm)
Portainer, veritabanına (portainer.db) düzenli olarak küçük yazma işlemleri yapar. Bu aktivite, mekanik bir HDD üzerinde çalışırken diskin uyku moduna geçmesini engelleyebilir. Bu sorunu çözmek için Portainer'ın veri dosyalarını SSD üzerinde barındırmak en etkili yöntemdir. Bu rehberdeki mimari, bu prensibe göre tasarlanmıştır.

## 7. Yedekleme Sistemi
Bu bölümde, hem Docker yapılandırma dosyalarının SSD üzerine düzenli olarak yedeğini alan, hem de bu yedeği isteğe bağlı olarak e-posta ile gönderen script'leri yapılandıracağız. Script'ler, yeni çift diskli mimariye ve Uptime Kuma ile verimli entegrasyona göre güncellenmiştir.

### 7.1 Yedekleme Script'i
Bu ana script, yedekleme işlemini gerçekleştirir ve sonucunu Uptime Kuma'ya bildirir.
```bash
sudo nano /usr/local/bin/docker-backup
```
Script içeriği:
```bash
#!/bin/bash
# Yedekleme dizinlerini ve değişkenleri tanımla
BASE_DIR="/mnt/ext500gb/docker"
BACKUP_DIR="/mnt/ext500gb/_backup/docker_backup"
PUSH_URL="https://status.sonmezer.tr/api/push/LOKAL_YEDEK_TOKEN_BURAYA"
DATE=$(date +%Y%m%d_%H%M%S)

# Dizinlerin varlığını kontrol et
if [ ! -d "$BASE_DIR" ]; then
    echo "Hata: $BASE_DIR dizini bulunamadı"
    curl -fsS --retry 3 "${PUSH_URL}?status=down&msg=Base-Dir-Not-Found&ping=" > /dev/null
    exit 1
fi

# Backup dizinini oluştur
mkdir -p "$BACKUP_DIR"

# Çalışma dizinine geç
cd "$BASE_DIR" || exit 1

# Kritik işletim sistemi ayarlarını ve özel script'leri geçici olarak kopyala (Arşivde temiz durması için)
sudo cp /etc/msmtprc /tmp/msmtprc_backup
sudo cp /usr/local/bin/docker-backup /tmp/docker-backup_script
sudo cp /usr/local/bin/docker-backup-email /tmp/docker-backup-email_script
sudo cp /etc/fstab /tmp/fstab_backup
crontab -l > /tmp/crontab_backup

# Veri tutarlılığı için Portainer'ı durdur
echo "Portainer durduruluyor..."
docker compose -f portainer/docker-compose.yml stop

# Yedekleme işlemini başlat (uptime-kuma veritabanı hariç tutulur)
echo "Yedekleme işlemi başlıyor..."
tar --exclude="./uptime-kuma/data" -czf "$BACKUP_DIR/docker_backup_$DATE.tar.gz" \
    ./cloudflared/config \
    ./firefox/data \
    ./filebrowser/config \
    ./portainer/data \
    ./*/.env \
    ./*/docker-compose.yml \
    /tmp/msmtprc_backup \
    /tmp/docker-backup_script \
    /tmp/docker-backup-email_script \
    /tmp/fstab_backup \
    /tmp/crontab_backup

# Yedeklemenin başarı durumunu kontrol et ve Uptime Kuma'ya sinyal gönder
if [ -f "$BACKUP_DIR/docker_backup_$DATE.tar.gz" ]; then
    echo "Yedekleme başarılı. Uptime Kuma'ya UP sinyali gönderiliyor."
    curl -fsS --retry 3 "${PUSH_URL}?status=up&msg=OK&ping=" > /dev/null
else
    echo "Hata: Yedekleme dosyası oluşturulamadı."
    curl -fsS --retry 3 "${PUSH_URL}?status=down&msg=Backup-Failed&ping=" > /dev/null
fi

# Arşive eklenen geçici dosyaları temizle
sudo rm /tmp/msmtprc_backup /tmp/docker-backup_script /tmp/docker-backup-email_script /tmp/fstab_backup /tmp/crontab_backup

# Portainer'ı yeniden başlat
echo "Portainer başlatılıyor..."
docker compose -f portainer/docker-compose.yml start

# 30 günden eski yerel yedekleri temizle (Disk dolmasını önlemek için)
echo "Eski yedekler temizleniyor..."
find "$BACKUP_DIR" -name "docker_backup_*.tar.gz" -mtime +30 -delete

echo "Yedekleme script'i tamamlandı."
```

### 7.2 Mail ile Yedekleme Sistemi

#### 7.2.1 MSMTP Kurulumu
```bash
# MSMTP kurulumu
sudo apt-get install msmtp msmtp-mta mailutils -y

# Log dosyası oluştur
touch ~/.msmtp.log
chmod 600 ~/.msmtp.log
```

#### 7.2.2 MSMTP Yapılandırması
```bash
sudo nano /etc/msmtprc
```

Not: Gmail için "Uygulama Şifresi" almanız gerekir:
1. Google Hesabı → Güvenlik → 2 Adımlı Doğrulama → Uygulama Şifreleri
2. "Diğer" seçeneğini seçin ve "Raspi Backup" gibi bir isim verin
3. Oluşturulan 16 karakterlik şifreyi msmtprc dosyasına ekleyin

msmtprc içeriği:
```
defaults
auth           on
tls            on
tls_trust_file /etc/ssl/certs/ca-certificates.crt
logfile        ~/.msmtp.log

account        gmail
host           smtp.gmail.com
port           587
from           your-email@gmail.com
user           your-email@gmail.com
password       your-app-specific-password

account default : gmail
```
Dosyayı kaydettikten sonra izinlerini ayarlayın:
```
# Güvenlik için sadece root'un yazabilmesi, herkesin okuyabilmesi yeterlidir.
sudo chmod 644 /etc/msmtprc
```

#### 7.2.3 Mail Backup Script'i
```bash
sudo nano /usr/local/bin/docker-backup-email
```

Script içeriği:
```bash
#!/bin/bash
# Bu script, ana yedekleme script'ini çalıştırır ve sonucunu e-posta ile gönderir.

# --- YAPILANDIRMA ---
BACKUP_DIR="/mnt/ext500gb/_backup/docker_backup"
EMAIL="your-email@gmail.com" # ÖNEMLİ: Kendi e-posta adresinizle değiştirin

# --- SCRIPT MANTIĞI ---
DATE=$(date +%Y%m%d_%H%M%S)
LATEST_BACKUP=""

# 1. Önce ana yedekleme script'ini çalıştır.
# Bu script, yedekleme işleminin kendi başarısı/başarısızlığı için Uptime Kuma'ya zaten sinyal gönderiyor.
sudo /usr/local/bin/docker-backup

# 2. Ana script'in oluşturduğu en son yedek dosyasını bul.
LATEST_BACKUP=$(ls -t "$BACKUP_DIR"/docker_backup_*.tar.gz | head -n1)

# 3. Yedek dosyasının varlığını kontrol et ve e-posta ile gönder.
if [ -f "$LATEST_BACKUP" ]; then
    # Yedek dosyasının boyutunu kontrol et (Gmail limiti ~25MB).
    BACKUP_SIZE=$(stat -c%s "$LATEST_BACKUP")
    
    if [ "$BACKUP_SIZE" -gt 26214400 ]; then
        # Dosya çok büyük, ek olmadan sadece uyarı e-postası gönder.
        echo "Uyarı: Yedek dosyası ($LATEST_BACKUP) 25MB'tan büyük ve e-posta ile gönderilemiyor." | \
        mail -s "Raspberry Pi Backup Boyut Uyarısı" "$EMAIL"
        exit 1
    fi

    # Dosya boyutu uygun, ek olarak gönder.
    BACKUP_SIZE_MB=$((BACKUP_SIZE / 1024 / 1024))
    echo "Docker backup dosyası ektedir.
    
Tarih: $(date)
Dosya: $(basename "$LATEST_BACKUP")
Boyut: ${BACKUP_SIZE_MB}MB" | mail -s "Raspberry Pi Docker Backup - $DATE" -A "$LATEST_BACKUP" "$EMAIL"

else
    # Bu bölüm, ana script çalışmasına rağmen bir sebepten dosya oluşturamazsa bir hata e-postası gönderir.
    # Not: Ana script'in Uptime Kuma'ya gönderdiği 'down' sinyaline ek bir bildirim katmanıdır.
    echo "Hata: Yedekleme script'i çalıştırıldıktan sonra yedek dosyası bulunamadı." | \
    mail -s "Raspberry Pi Backup Hatası" "$EMAIL"
fi
```

### 7.3 Scriptleri Yapılandırma

#### 7.3.1 İzinleri Ayarla
```bash
# Scriptleri çalıştırılabilir yap
sudo chmod +x /usr/local/bin/docker-backup
sudo chmod +x /usr/local/bin/docker-backup-email

# Yedekleme dizin izinlerini doğrula (Bu ayarlar Bölüm 1.2'de yapıldı)
sudo chmod 750 /mnt/ext500gb/_backup
sudo chmod 755 /mnt/ext500gb/_backup/docker_backup
```

#### 7.3.2 Test
```bash
# Normal backup test
sudo docker-backup

# Mail backup test
sudo docker-backup-email
```

### 7.4 Cron Görevleri
```bash
sudo crontab -e

# Eklenecek satırlar:
# Her gece 03:00'te normal backup
0 3 * * * /usr/bin/sudo /usr/local/bin/docker-backup

# Ayın 1'i ve 15'inde saat 04:00'te mail backup
0 4 1,15 * * /usr/bin/sudo /usr/local/bin/docker-backup-email
```

### 7.5 Yedek Doğrulama ve Kontrol

#### 7.5.1 Backup Kontrolü
```bash
# Son backup'ı kontrol et
cd /mnt/ext500gb/_backup/docker_backup
ls -lah $(ls -t | head -n1)

# Backup içeriğini kontrol et
tar tvf $(ls -t | head -n1)
```

#### 7.5.2 Mail Kontrolü
```bash
# Mail log kontrolü
tail ~/.msmtp.log

# Mail gönderim testi
echo "Test mesajı" | mail -s "Backup Test" your-email@gmail.com
```

### 7.6 Hassas Bilgi Yönetimi

#### 7.6.1 .env Dosyaları
```bash
# .env dosyalarının izinlerini kontrol et
find /mnt/ext4tb/docker -name ".env" -ls

# İzinleri düzelt
find /mnt/ext4tb/docker -name ".env" -exec chmod 600 {} \;
```

#### 7.6.2 Sertifikalar ve Anahtarlar
```bash
# Sertifika ve anahtar izinleri
find /mnt/ext500gb/docker -name "*.key" -exec chmod 600 {} \;
find /mnt/ext500gb/docker -name "*.pem" -exec chmod 600 {} \;
```

### 7.7 Sorun Giderme

#### 7.7.1 Yedekleme Sorunları
```bash
# Disk alanı kontrolü
df -h /mnt/ext500gb
df -h /mnt/ext4tb

# İzin sorunları
ls -la /usr/local/bin/docker-backup*
ls -la /mnt/ext500gb/_backup/docker_backup/

# Log kontrolü
tail -f ~/.msmtp.log
```

#### 7.7.2 Mail Sorunları ve Hata Ayıklama (Güncellendi)
```bash
#### 7.7.2 Mail Sorunları ve Hata Ayıklama (Güncellendi)

Eğer `docker-backup-email` script'i "Process exited with a non-zero status" hatası veriyorsa, sorunun kaynağını bulmak için `mail` komutu yerine `msmtp`'nin kendi debug modunu kullanın:

# 1. Detaylı Mail Testi (Hata Ayıklama)
echo -e "Subject: Test\n\nBu bir test mesajidir." | sudo msmtp --debug your-email@gmail.com

# 2. Sık Karşılaşılan Hata: "535-5.7.8 Username and Password not accepted"
Bu hatayı alıyorsanız, Google Uygulama Şifrenizin süresi dolmuş veya iptal edilmiş demektir.
Çözüm:
- Google Hesabı > Güvenlik > 2 Adımlı Doğrulama > Uygulama Şifreleri'ne gidin.
- Yeni bir 16 haneli şifre oluşturun.
- sudo nano /etc/msmtprc dosyasını açın.
- password satırındaki eski şifreyi yeni 16 haneli şifreyle değiştirin.

# 3. SMTP ve SSL/TLS Bağlantı Kontrolleri (Şifre sorunu yoksa)
telnet smtp.gmail.com 587
openssl s_client -starttls smtp -connect smtp.gmail.com:587
```

### 7.8 İyi Uygulama Önerileri

#### 7.8.1 Backup Güvenliği
1. Yedekleri şifreleme (gpg)
2. Farklı lokasyonlarda saklama
3. Düzenli test restore işlemi

#### 7.8.2 Mail Güvenliği
1. Güçlü uygulama şifreleri
2. Düzenli şifre yenileme
3. Backup boyut kontrolü

#### 7.8.3 Hassas Bilgi Yönetimi
1. Minimum izin prensipleri
2. Düzenli güvenlik denetimi
3. Şifre ve token rotasyonu

Not: Bu bölümde yedekleme sistemi, mail entegrasyonu ve hassas bilgi yönetimi detaylı şekilde ele alınmıştır. Özellikle backup güvenliği ve doğrulama süreçleri için önemli güncellemeler eklenmiştir.

## 8. Test ve Sorun Giderme

### 8.1 Docker Sorunları

#### 8.1.1 İzin Sorunları
```bash
# Docker socket izinleri
sudo chmod 666 /var/run/docker.sock

# Grup yetkileri
sudo usermod -aG docker $USER
newgrp docker

# İzinleri kontrol et
ls -la /var/run/docker.sock
groups | grep docker
```

#### 8.1.2 Memory/Swap Limitleri
```bash
# Memory/swap uyarılarını kontrol et
docker info | grep -i "warning"

# Boot parametrelerini kontrol et
cat /boot/firmware/cmdline.txt

# cgroup durumu
grep cgroup /proc/mounts
```

#### 8.1.3 Buffer Size
```bash
# Buffer size ayarlarını kontrol et
sysctl net.core.rmem_max
sysctl net.core.wmem_max

# Gerekirse ayarla
sudo tee /etc/sysctl.d/99-docker-network.conf << EOF
net.core.rmem_max=2500000
net.core.wmem_max=2500000
EOF
sudo sysctl -p /etc/sysctl.d/99-docker-network.conf
```

### 8.2 Network Sorunları

#### 8.2.1 Docker Network
```bash
# Network kontrolü
docker network ls
docker network inspect raspi_network

# Container bağlantıları
for container in $(docker ps -q); do
    echo "Container: $(docker inspect -f '{{.Name}}' $container)"
    docker inspect $container | grep -A 20 "Networks"
done
```

#### 8.2.2 DNS Sorunları
```bash
# DNS çözümlemesi
for domain in portainer.sonmezer.tr files.sonmezer.tr web.sonmezer.tr; do
    echo "Testing $domain:"
    nslookup $domain
done

# Container DNS testi
for container in $(docker ps -q); do
    echo "Container: $(docker inspect -f '{{.Name}}' $container)"
    docker exec $container ping -c 1 google.com
done
```

### 8.3 Servis Sorunları

#### 8.3.1 Cloudflared
```bash
# Tünel durumu
docker logs raspi_cloudflared | grep "Registered tunnel"

# Bağlantı testi
curl -I https://portainer.sonmezer.tr
```

#### 8.3.2 Filebrowser
```bash
# İzin kontrolü
ls -la /mnt/ext4tb/docker/filebrowser/config/database.db
```

#### 8.3.3 Firefox
```bash
# Container sağlığı
docker inspect --format='{{json .State.Health}}' firefox

# Port kontrolü
netstat -tuln | grep 5800
```

#### 8.3.4 Portainer
```bash
# SSL kontrolü
openssl s_client -connect localhost:9443

# API testi
curl -k https://localhost:9443/api/system/version
```

### 8.4 İzin Sorunları

#### 8.4.1 Dizin İzinleri
```bash
# Ana dizin kontrolleri
sudo chown -R $USER:$USER /mnt/ext500gb/docker
find /mnt/ext500gb/docker -type f -exec chmod 644 {} \;
find /mnt/ext500gb/docker -type d -exec chmod 755 {} \;

# Hassas dosyalar
find /mnt/ext500gb/docker -name ".env" -exec chmod 600 {} \;
find /mnt/ext500gb/docker -name "*.key" -exec chmod 600 {} \;
```

#### 8.4.2 Container İzinleri
```bash
# PUID/PGID kontrolü
for container in $(docker ps -q); do
    echo "Container: $(docker inspect -f '{{.Name}}' $container)"
    docker inspect $container | grep -A 5 "User"
done
```

### 8.5 Backup Sorunları

#### 8.5.1 Normal Backup
```bash
# Backup script kontrolü
ls -la /usr/local/bin/docker-backup
sudo docker-backup
#ya da çalışmazsa
sudo /usr/local/bin/docker-backup

# Backup dosya kontrolü (yeni SSD yolu ile)
cd /mnt/ext500gb/_backup/docker_backup
ls -lah $(ls -t | head -n1)
```

#### 8.5.2 Mail Backup
```bash
# MSMTP yapılandırması
cat /etc/msmtprc
ls -la ~/.msmtp.log

# Mail gönderim testi
echo "test" | mail -s "test" your-email@gmail.com
```

### 8.6 Log Analizi

#### 8.6.1 Docker Logları
```bash
# Tüm container logları
for container in $(docker ps -q); do
    echo "=== Logs for $(docker inspect -f '{{.Name}}' $container) ==="
    docker logs --tail 50 $container
done

# Hata logları
for container in $(docker ps -q); do
    echo "=== Errors for $(docker inspect -f '{{.Name}}' $container) ==="
    docker logs $container 2>&1 | grep -i error
done
```

#### 8.6.2 Sistem Logları
```bash
# Docker servis logları
journalctl -u docker

# Mail logları
tail -f ~/.msmtp.log
```

### 8.7 Performans Sorunları

#### 8.7.1 Sistem Kaynakları
```bash
# Container kaynak kullanımı
docker stats

# Disk kullanımı (her iki disk için ayrı ayrı)
du -sh /mnt/ext500gb/docker/*
du -sh /mnt/ext4tb/_shared/*

# I/O performansı
iostat 1 10
```

#### 8.7.2 Network Performansı
```bash
# Network trafiği
iftop -i docker0

# Container network istatistikleri
docker stats --format "table {{.Name}}\t{{.NetIO}}"
```

### 8.8 SSL/TLS Sorunları

#### 8.8.1 Sertifika Kontrolü
```bash
# Portainer sertifikası
openssl x509 -in /mnt/ext500gb/docker/portainer/data/certs/portainer.crt -text -noout

# Cloudflare tünel SSL
curl -vI https://portainer.sonmezer.tr
```

#### 8.8.2 Sertifika Yenileme
```bash
# Sertifika geçerlilik kontrolü
for cert in $(find /mnt/ext500gb/docker -name "*.crt"); do
    echo "=== Checking $cert ==="
    openssl x509 -in $cert -noout -dates
done
```

### 8.9 Genel Sorun Giderme Adımları

1. Log kontrolü:
   ```bash
   docker logs <container_name>
   ```

2. Container durumu:
   ```bash
   docker inspect <container_name>
   ```

3. İzin kontrolü:
   ```bash
   ls -la /path/to/check
   ```

4. Network testi:
   ```bash
   docker exec <container_name> ping -c 1 google.com
   ```

5. Servis restart:
   ```bash
   docker compose restart <service_name>
   ```

### 8.10 İyi Uygulama Önerileri

#### 8.10.1 Proaktif İzleme
1. Düzenli log kontrolü
2. Kaynak kullanım takibi
3. Sertifika geçerlilik kontrolü

#### 8.10.2 Güvenlik Kontrolleri
1. İzin denetimi
2. Hassas dosya kontrolü
3. Network güvenliği

#### 8.10.3 Bakım Rutinleri
1. Log rotasyonu
2. Disk temizliği
3. Container güncelleme

Not: Bu bölümde tüm servislerin test ve sorun giderme adımları detaylı şekilde ele alınmıştır. Özellikle yeni eklenen memory/swap limitleri ve buffer size optimizasyonları için kontrol noktaları eklenmiştir.## 9. İleri Seviye Yapılandırmalar

## 9. Sistem Monitoring ve Güncelleme

### 9.1 Uptime Kuma Kurulumu

KRİTİK UYARI ("Sahte Yeşil" Önlemi): Servisleri (Portainer, Filebrowser vb.) izlerken Cloudflare domain adreslerini KULLANMAYIN. Aksi takdirde servis çökse bile Cloudflare ayakta olduğu için Uptime Kuma "Sahte Yeşil" (False Positive) sinyal verir.

Servisler daima Raspberry Pi yerel IP'si (192.168.8.232) ve konteynerin yerel portu üzerinden izlenmelidir. (Örn: http://192.168.8.232:8334)

Yerel IP kullanıldığında oluşacak sertifika hatasını aşmak için monitör ayarlarından "TLS/SSL hatasını yoksay" seçeneği İŞARETLENMELİDİR.

Bilinçli kapatılan konteynerler (Firefox vb.) "Uyarı Yorgunluğu" (Alert Fatigue) yaratmamak için Uptime Kuma'ya eklenmemelidir.

Çift Yönlü Push Monitörleri:
Docker Local Backup (Push): Heartbeat aralığı 25 Saat (90000 sn).
Docker Mail Backup (Push): Heartbeat aralığı 16 Gün (1382400 sn).

#### 9.1.1 Dizin Yapısı
```bash
# Ana dizini oluştur
cd /mnt/ext500gb/docker
mkdir -p uptime-kuma/data
sudo chown -R $USER:$USER uptime-kuma
chmod 755 uptime-kuma
```

#### 9.1.2 Docker Compose
```yaml
services:
  uptime-kuma:
    image: louislam/uptime-kuma:latest
    container_name: uptime-kuma
    volumes:
      - /mnt/ext500gb/docker/uptime-kuma/data:/app/data
    ports:
      - "3001:3001"
    restart: always
    security_opt:
      - no-new-privileges:true
    networks:
      - raspi_network
    healthcheck:
      test: ["CMD", "wget", "--no-verbose", "--tries=1", "--spider", "http://localhost:3001"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 30s

networks:
  raspi_network:
    external: true
    name: raspi_network
```

#### 9.1.3 Cloudflare Tunnel Yapılandırması
1. Cloudflare Zero Trust Dashboard'a gidin
2. Networks > Tunnels > Public Hostnames
3. Yeni hostname ekleyin:
   - Hostname: status.domain.com
   - Service: http://uptime-kuma:3001
   - No TLS Verify: Hayır (gerekli değil)

#### 9.1.4 Servis Monitörleri
Temel servisler için önerilen monitör ayarları:

1. Portainer:
   - Type: HTTP(s)
   - URL: https://192.168.8.232:9443
   - Method: GET
   - Accept Invalid SSL: 
   Önemli Ayar: Eğer kendinden imzalı bir SSL sertifikası kullanıyorsanız, "Gelişmiş Seçenekler" altından "Geçersiz SSL'i Yoksay" (Ignore TLS/SSL error) seçeneğini aktifleştirmeniz gerekebilir.

2. Filebrowser:
   - Type: HTTP(s)
   - URL: http://192.168.8.232:8334

3. Remote Firefox:
    Kurulum: Uptime Kuma'da "Push" tipinde yeni bir monitör oluşturulur.
    Heartbeat Interval: Kontrol script'i her 5 dakikada bir çalışacağı için, bu değer 330 saniye (5.5 dakika) gibi bir değere ayarlanır.
    Entegrasyon: Firefox'un yerel portunun (5800) açık olup olmadığını kontrol eden (nc -z 127.0.0.1 5800) ve sonucuna göre Uptime Kuma'ya "up" veya "down" sinyali gönderen /usr/local/bin/check-firefox adında bir script oluşturulur. Bu script, crontab ile her 5 dakikada bir otomatik olarak çalıştırılır. Bu yöntem, Cloudflare'in neden olduğu "sahte sağlıklı" durumunu %100 oranında çözer.

4. SSH:
   - Type: PING
   - Hostname: 192.168.8.232 (Raspberry Pi'nizin yerel IP'si)

5. Docker Backup:
    Kurulum: Uptime Kuma'da "Push" tipinde yeni bir monitör oluşturulur.
    Heartbeat Interval: Yedekleme 24 saatte bir çalıştığı için, bu değer 90000 saniye (25 saat) gibi daha uzun bir değere ayarlanır.
    Entegrasyon: Monitörün verdiği "Push URL"si, /usr/local/bin/docker-backup script'inin sonuna curl komutu ile eklenir. Script, yedekleme başarılı olursa "up", başarısız olursa "down" sinyali gönderir.
   
   Not: Docker Backup monitörü için:
   - Filebrowser'da _public/backup_status.json dosyası için Share oluşturun
   - "No authentication required" seçeneğini işaretleyin
   - Oluşturulan share link'i monitör URL'sinde kullanın


6. Transmission:
   - Type: HTTP(s)
   - URL: http://192.168.8.232:9091
   - Method: GET
   - Authentication: Basic Auth
   - Username: [transmission kullanıcı adı]
   - Password: [transmission şifresi]

   Not: Transmission'ın düzgün çalışması için gerekli izin ayarları:
   - Transmission kullanıcısı (debian-transmission) ana kullanıcı grubuna eklenmelidir
   - İndirme dizinleri için grup yazma izinleri (775) ve setgid biti ayarlanmalıdır


#### 9.1.5 Telegram Bildirim Yapılandırması
1. @BotFather ile yeni bot oluşturma:
   - /newbot komutunu gönderin
   - Bot için isim ve kullanıcı adı belirleyin
   - API token'ı kaydedin

2. Chat ID alma:
   - Bot ile sohbet başlatın ("/start")
   - Bot'a herhangi bir mesaj gönderin
   - https://api.telegram.org/bot<TOKEN>/getUpdates
   - JSON çıktısından chat ID'yi alın

3. Uptime Kuma ayarları:
   - Settings > Notification
   - Add Notification > Telegram
   - Bot Token ve Chat ID girin
   - Test notification gönderin

4. Bildirim kuralları:
   - Notify when down: Enable
   - Notify when up: Enable
   - Notify when paused: Disable

#### 9.1.6 Status Page Yapılandırması
1. Settings > Status Page
2. Create Status Page:
   - Title: Sistem Durumu
   - Slug: yspi (status.domain.com/status/yspi)
   - Theme: Dark/Light
   - Show Tags: Yes
   - Show Response Time Chart: Yes

3. Servis grupları:
   - "Storage Services": WebDAV, Filebrowser, Docker Backup
   - "System Services": Portainer, SSH
   - "Web Services": Remote Firefox
   - "Download Services": Transmission

#### 9.1.7 İzin ve Güvenlik Yapılandırması
```bash
# Dizin izinleri
chmod 755 /mnt/ext4tb/docker/uptime-kuma
chmod 755 /mnt/ext4tb/docker/uptime-kuma/data

# Sahiplik
sudo chown -R $USER:$USER /mnt/ext4tb/docker/uptime-kuma
```

#### 9.1.8 Sorun Giderme
```bash
# Container durumu
docker ps | grep uptime-kuma

# Log kontrolü
docker logs uptime-kuma

# Port kontrolü
netstat -tuln | grep 3001

# İzin sorunları
ls -la /mnt/ext4tb/docker/uptime-kuma/data

# Backup izleme sorunları
# Status dosyasını kontrol et
cat /mnt/ext4tb/_shared/_public/backup_status.json

# Filebrowser share link erişimini test et
curl -I [share_link_url]

# JSON formatını doğrula
cat /mnt/ext4tb/_shared/_public/backup_status.json | json_pp
```

#### 9.3.3 Genel Sistem Kontrolleri
```bash
# Buffer size ayarları
sysctl net.core.rmem_max
sysctl net.core.wmem_max
sysctl net.core.rmem_default
sysctl net.core.wmem_default

# Docker network
docker network inspect raspi_network

# Cloudflare tünel durumu
docker logs cloudflared | grep "Registered tunnel"

# Backup kontrolleri
ls -la /mnt/ext500gb/_backup/docker_backup/
```

#### 9.3.4 Final Checklist
1. [ ] Buffer size optimizasyonları uygulandı
2. [ ] Uptime Kuma tüm servisleri izliyor
3. [ ] Status page erişilebilir
4. [ ] Telegram bildirimleri çalışıyor
5. [ ] Backup sistemi yeni servisleri içeriyor
6. [ ] Tüm servisler raspi_network'e bağlı
7. [ ] Cloudflare tünelleri stabil çalışıyor
8. [ ] İzinler ve güvenlik ayarları doğru
9. [ ] Sistem performansı stabil

## 10. İleri Seviye Yapılandırmalar

### 10.2 Network Optimizasyonları

#### 10.2.1 Network Stack Ayarları
```bash
# Network parametreleri
sudo nano /etc/sysctl.conf

# Ekle veya düzenle:
net.core.rmem_max=2500000
net.core.wmem_max=2500000
net.ipv4.tcp_rmem=4096 87380 2500000
net.ipv4.tcp_wmem=4096 87380 2500000
net.ipv4.tcp_mem=50576 64768 98152
net.core.netdev_max_backlog=2500
net.ipv4.tcp_fastopen=3

# Uygula
sudo sysctl -p
```

#### 10.2.2 Container Network Ayarları
```bash
# DNS ayarları
sudo nano /etc/docker/daemon.json

{
  "dns": ["1.1.1.1", "1.0.0.1"],
  "dns-opts": ["use-vc"],
  "dns-search": [],
  "mtu": 1500,
  "max-concurrent-downloads": 10,
  "max-concurrent-uploads": 10
}

# Docker daemon'ı yeniden başlat
sudo systemctl restart docker
```

### 10.3 Storage Optimizasyonları

#### 10.3.1 Container Storage
```bash
# Container log limitleri
sudo nano /etc/docker/daemon.json

{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
```

#### 10.3.2 Disk I/O Ayarları
```bash
# I/O scheduler
echo deadline | sudo tee /sys/block/mmcblk0/queue/scheduler

# Mount parametreleri
sudo nano /etc/fstab

# Ekle veya düzenle:
UUID=<disk_uuid> /mnt/ext500gb/ ext4 defaults,noatime,nodiratime,commit=60 0 0
```

### 10.4 Güvenlik Yapılandırmaları

#### 10.4.1 Container Güvenliği
```bash
# Default security-opt
sudo nano /etc/docker/daemon.json

{
  "default-ulimits": {
    "nofile": {
      "Name": "nofile",
      "Hard": 64000,
      "Soft": 64000
    }
  },
  "no-new-privileges": true,
  "selinux-enabled": false,
  "userns-remap": "default"
}
```

#### 10.4.2 Network Güvenliği
```bash
# UFW yapılandırması
sudo apt install ufw
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### 10.5 SSL/TLS Optimizasyonları

#### 10.5.1 SSL Parametreleri
```bash
# OpenSSL yapılandırması
sudo nano /etc/ssl/openssl.cnf

[system_default_sect]
MinProtocol = TLSv1.2
CipherString = HIGH:!aNULL:!MD5:!RC4
```

#### 10.5.2 Sertifika Yönetimi
```bash
# Sertifika izleme script'i
sudo nano /usr/local/bin/cert-monitor

#!/bin/bash
for cert in $(find /mnt/ext500gb/docker -name "*.crt"); do
    expiry=$(openssl x509 -in $cert -noout -enddate | cut -d= -f2)
    echo "$cert expires on $expiry"
done

chmod +x /usr/local/bin/cert-monitor
```

### 10.6 Performans İzleme

#### 10.6.1 Container Metrics
```bash
# Prometheus node-exporter
docker run -d \
  --name node-exporter \
  --restart always \
  --network raspi_network \
  -v "/:/host:ro,rslave" \
  quay.io/prometheus/node-exporter \
  --path.rootfs=/host
```

#### 10.6.2 Log Aggregation
```bash
# Vector log toplayıcı
docker run -d \
  --name vector \
  --network raspi_network \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v /var/lib/docker/containers:/var/lib/docker/containers:ro \
  timberio/vector:latest-alpine
```

### 10.8 Sorun Giderme ve İzleme

#### 10.8.1 Performans İzleme
```bash
# Container kaynak kullanımı
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"

# Disk I/O
iostat -x 1 5

# Network trafiği
iftop -i docker0
```

#### 10.8.2 Log Analizi
```bash
# Container log analizi
for container in $(docker ps -q); do
    name=$(docker inspect -f '{{.Name}}' $container)
    echo "=== $name logs ==="
    docker logs --since 1h $container | grep -i error
done
```

### 10.9 Yedekleme ve Kurtarma
Sistem iki farklı yedekleme rutini (Günlük Lokal ve 15 Günlük E-Posta) çalıştırdığı için, Uptime Kuma'da iki ayrı "Push" monitörü oluşturulmalıdır:

Docker Local Backup (Push): Heartbeat (Kalp Atışı) aralığı 25 Saat (90000 sn).

Docker Mail Backup (Push): Heartbeat aralığı 16 Gün (1382400 sn).
