# Changelog

Semua perubahan penting pada **NovaMusicStream** dicatat di sini berdasarkan riwayat commit Git dari awal repository sampai versi terbaru.

> Catatan: tanggal mengikuti metadata commit di repository.

---

## [Unreleased]

Belum ada perubahan setelah commit dokumentasi terakhir.

---

## [0.6.0] — 2026-10-13

### Dokumentasi

- Menambahkan `README.md` baru yang modern dan komprehensif.
- Mendokumentasikan fitur, arsitektur, instalasi, konfigurasi, command, deployment, troubleshooting, development, keamanan, dan kontribusi.
- Menambahkan `CHANGELOG.md`.

### Repository

- Repository berada dalam kondisi bersih setelah eksperimen sementara AI Gen, IPTV, dan UNO dihapus atau di-reset.
- Fitur aktif tetap berfokus pada voice-chat music player NovaMusicStream.

**Commit:** `25b1188 docs: add comprehensive README and changelog`

---

## [0.5.0] — 2026-09-20

### Broadcast channel streaming

- Menambahkan dukungan streaming audio ke broadcast channel melalui `/cplay`.
- Menambahkan dukungan streaming video ke broadcast channel melalui `/cvplay`.
- Menambahkan penanganan playback yang membedakan group voice chat dan broadcast channel.
- Menyesuaikan kontrol playback seperti pause, resume, skip, stop, dan ping agar channel-aware.
- Menambahkan helper untuk mengambil informasi channel.
- Memperbarui daftar bantuan dengan command channel streaming.
- Memperbaiki source link pada tombol source.
- Menambahkan dukungan admin/channel yang dibutuhkan untuk streaming ke channel.

### Command baru

- `/cplay` — memutar audio di broadcast channel.
- `/cvplay` — memutar video di broadcast channel.

**Commit:** `24dd3a9 feat: add /cplay & /cvplay channel streaming, channel-aware controls, fix source link`

---

## [0.4.0] — 2026-08-25

### Administrasi dan akses

- Menambahkan mode hybrid untuk penggunaan bot dengan atau tanpa konfigurasi admin tertentu.
- Memperbarui alur validasi admin dan hak akses command.
- Memperbaiki dukungan evaluasi dan command administratif.

### Network dan performa

- Menambahkan deteksi network otomatis.
- Menyesuaikan konfigurasi dan proses download berdasarkan kondisi network.
- Meningkatkan ketahanan proses media extraction dan download.

### System statistics

- Memperkaya output `/sysstats`.
- Menambahkan informasi sistem dan network yang lebih lengkap.
- Memperbarui tampilan status dan statistik server.

### Konfigurasi dan deployment

- Memperbarui `.env.example`.
- Memperbarui `.gitignore`.
- Menyesuaikan `Dockerfile` untuk kebutuhan runtime terbaru.
- Menyesuaikan startup dan konfigurasi utama.

**Commit:** `2163879 feat: hybrid admin/non-admin mode, network auto-detect, and richer /sysstats`

---

## [0.3.0] — 2026-07-04

### Video streaming

- Menambahkan dukungan video streaming melalui `/vplay`.
- Memperbarui pipeline download agar dapat menangani audio dan video.
- Menyesuaikan queue untuk media video.
- Memperbarui watcher agar lebih sesuai dengan lifecycle video stream.
- Meningkatkan reliability download dan playback.

### Command baru

- `/vplay` — memutar video di video chat.

**Commit:** `f77babd feat: add video streaming support with /vplay and improve download reliability`

---

## [0.2.0] — 2026-07-04

### Perbaikan download

- Memperbaiki masalah HTTP 403 saat mengambil media.
- Memperbarui downloader untuk meningkatkan kompatibilitas terhadap sumber media.
- Menambahkan penanganan error download yang lebih aman.

**Commit:** `e606bb0 fix 403`

---

## [0.1.0] — 2026-07-04

### Initial repository

- Membuat baseline awal NovaMusicStream.
- Menambahkan bot client berbasis Pyrogram.
- Menambahkan assistant client berbasis Telethon.
- Menambahkan integrasi Py-TgCalls untuk voice chat.
- Menambahkan struktur modular di `NovaMusic/Helpers` dan `NovaMusic/Modules`.
- Menambahkan module dasar playback:
  - `/play`
  - `/pause`
  - `/resume`
  - `/skip`
  - `/end`
- Menambahkan pencarian dan download lagu:
  - `/search`
  - `/song`
- Menambahkan command dan utilitas administrasi:
  - `/start`
  - `/ping`
  - `/activevc`
  - `/sudolist`
  - `/sysstats`
  - `/speedtest`
  - `/eval`
  - `/broadcast`
  - `/leaveall`
- Menambahkan queue playback, thumbnail generator, formatter, downloader, error handler, dan helper Telegram.
- Menambahkan konfigurasi environment melalui `.env.example` dan `config.py`.
- Menambahkan `requirements.txt`.
- Menambahkan `Dockerfile`, `Procfile`, `app.json`, dan script startup `nova`.
- Menambahkan generator session assistant melalui `gen_telethon.py`.
- Menambahkan `LICENSE` dan konfigurasi repository dasar.

**Commit:** `2d2adb7 clean repo`

---

## Riwayat eksperimen yang di-reset

Bagian berikut merupakan riwayat pekerjaan selama sesi pengembangan, tetapi tidak menjadi fitur aktif pada commit terbaru.

### UNO — dihapus

- Pernah diintegrasikan dari `jh0ker/mau_mau_bot`.
- Pernah dibuat adapter Pyrogram dan engine game di `NovaMusic/Uno/`.
- Pernah ditambahkan command `/uno`, `/new`, `/join`, `/unostart`, `/leave`, dan `/kill`.
- Pernah ditambahkan inline card selection dan aktivasi per grup.
- Integrasi kemudian dihapus dan file terkait dikembalikan ke versi GitHub sebelum eksperimen.

### AI Gen dan IPTV — dihapus

- Pernah dibuat modul eksperimen AI Gen.
- Pernah dibuat helper dan module IPTV.
- Seluruh file eksperimen tersebut kemudian dihapus agar repository kembali bersih.

---

## Ringkasan fitur versi terbaru

- 🎵 Audio streaming di Telegram voice chat.
- 🎬 Video streaming melalui `/vplay`.
- 📡 Audio channel streaming melalui `/cplay`.
- 📺 Video channel streaming melalui `/cvplay`.
- 🔎 YouTube search dan media download.
- ⏯️ Pause, resume, skip, dan queue management.
- 🛡️ Owner dan sudo access control.
- 📊 System dan network statistics.
- 🤖 Pyrogram bot + Telethon assistant.
- ⚡ Py-TgCalls voice/video chat integration.
- 🧩 Modular command loading.
- 🐳 Docker, Procfile, dan PM2 deployment support.

## Catatan keamanan

Jangan pernah commit data sensitif berikut:

- `BOT_TOKEN`
- `API_ID` atau `API_HASH` private
- `SESSION`
- nomor telepon assistant account
- credentials pada `cookies.txt`
- konfigurasi private atau token deployment

Gunakan `.env` lokal dan pastikan file rahasia tetap diabaikan oleh Git.
