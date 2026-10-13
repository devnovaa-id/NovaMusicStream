# Changelog

Semua perubahan penting pada **NovaMusicStream** dicatat di file ini.

Format changelog ini mengikuti pendekatan kronologis dan membedakan antara perubahan yang masih aktif di project dengan eksperimen yang akhirnya di-reset.

---

## [Unreleased] — 2026-10-12

### Dokumentasi

- Menambahkan `README.md` baru dengan dokumentasi yang lebih modern, lengkap, dan terstruktur.
- Menambahkan dokumentasi mengenai:
  - fitur utama NovaMusicStream,
  - arsitektur project,
  - instalasi lokal,
  - konfigurasi environment variable,
  - command user, sudo, dan owner,
  - pembuatan Telethon session,
  - deployment PM2,
  - deployment Docker,
  - troubleshooting,
  - development workflow,
  - keamanan credentials,
  - license dan contribution guide.

### Repository cleanup

- Menghapus file eksperimen AI Gen:
  - `NovaMusic/Modules/aigen.py`
- Menghapus file eksperimen IPTV:
  - `NovaMusic/Helpers/iptv.py`
  - `NovaMusic/Modules/iptv.py`
- Menghapus seluruh integrasi UNO beserta engine dan file pendukungnya dari `NovaMusic/Uno/`.
- Mengembalikan file help, inline keyboard, callback, dan startup ke versi repository sebelum eksperimen UNO:
  - `NovaMusic/Helpers/dossier.py`
  - `NovaMusic/Helpers/inline.py`
  - `NovaMusic/Modules/callback.py`
  - `NovaMusic/__main__.py`
- Working tree dikembalikan bersih setelah proses reset dan cleanup.

---

## [Experimental] UNO Integration — Reverted

> Bagian ini dicatat sebagai riwayat perubahan, bukan fitur aktif pada versi saat ini.

### Penambahan awal

- Mengintegrasikan engine UNO dari repository:
  - `https://github.com/jh0ker/mau_mau_bot.git`
- Menambahkan engine game ke dalam `NovaMusic/Uno/`.
- Membuat adapter Pyrogram agar UNO menggunakan client NovaMusic yang sudah berjalan.
- Menambahkan command permainan UNO seperti:
  - `/uno`
  - `/new`
  - `/join`
  - `/start`
  - `/leave`
  - `/kill`
- Menambahkan inline mode untuk melihat kartu dan memilih kartu permainan.
- Menambahkan command UNO ke help dan menu command Telegram.

### Perbaikan selama eksperimen

- Memperbaiki penggunaan `set.add()` pada daftar owner game.
- Memisahkan state setiap game agar tidak bocor antargrup.
- Memperbaiki masalah async pada `send_message()`.
- Mengubah command mulai UNO menjadi `/unostart` agar tidak bentrok dengan `/start` NovaMusic.
- Membatasi aktivasi UNO agar hanya aktif setelah `/uno` dijalankan di grup.
- Memperbaiki custom filter Pyrogram yang membutuhkan tiga parameter.
- Memperbaiki pembuatan `InlineQueryResultArticle` dengan `InputTextMessageContent` yang benar.
- Memperbaiki error Telegram `MEDIA_CAPTION_TOO_LONG` saat membuka halaman help dari pesan foto.
- Memperbaiki logika draw dan pergantian giliran.
- Menambahkan validasi kartu yang dimainkan melalui inline result.
- Menambahkan pembatasan agar hanya pembuat game atau admin yang dapat memulai game.
- Memperbaiki cleanup game pada `GameManager`.

### Reset

- Integrasi UNO akhirnya dihapus sesuai permintaan agar project kembali ke versi repository sebelum integrasi tersebut.
- Tidak ada command atau modul UNO yang aktif pada versi saat ini.

---

## [Experimental] AI Gen dan IPTV — Reverted

> Eksperimen ini juga sudah dihapus dari project saat ini.

- Pernah menambahkan modul AI Gen:
  - `NovaMusic/Modules/aigen.py`
- Pernah menambahkan modul IPTV:
  - `NovaMusic/Helpers/iptv.py`
  - `NovaMusic/Modules/iptv.py`
- Seluruh file tersebut kemudian dihapus untuk mengembalikan repository ke kondisi bersih.

---

## [Current Base] NovaMusicStream

Perubahan utama yang menjadi fondasi project saat ini mencakup:

- Bot Telegram voice-chat berbasis Pyrogram.
- Assistant account berbasis Telethon.
- Streaming audio dan video menggunakan Py-TgCalls.
- Dukungan command `/play` dan `/vplay`.
- Dukungan streaming ke broadcast channel melalui `/cplay` dan `/cvplay`.
- Queue playback dengan command pause, resume, skip, dan end.
- Pencarian YouTube dan download lagu.
- Thumbnail, cache, dan download management.
- Sistem owner dan sudo user.
- Struktur module otomatis melalui `NovaMusic/Modules/__init__.py`.
- Dukungan deployment melalui Docker, Procfile, dan PM2.
- Perbaikan source link pada tombol source.

### Command utama yang tersedia

- `/play`
- `/vplay`
- `/cplay`
- `/cvplay`
- `/pause`
- `/resume`
- `/skip`
- `/end`
- `/ping`
- `/sudolist`
- `/song`
- `/search`

---

## [0.1.0] — Repository baseline

- Baseline project NovaMusicStream digunakan sebagai dasar pengembangan.
- Struktur awal bot, helper, module, konfigurasi, Dockerfile, Procfile, dan requirements tersedia.
- Commit baseline terakhir yang tercatat pada repository:

```text
24dd3a9 feat: add /cplay & /cvplay channel streaming, channel-aware controls, fix source link
```

---

## Catatan keamanan

Jangan memasukkan data berikut ke dalam commit atau changelog:

- `BOT_TOKEN`
- `API_HASH`
- `SESSION`
- password atau nomor telepon assistant account
- `cookies.txt` yang berisi credentials
- data konfigurasi private

Gunakan `.env` lokal dan pastikan file rahasia tetap masuk `.gitignore`.
