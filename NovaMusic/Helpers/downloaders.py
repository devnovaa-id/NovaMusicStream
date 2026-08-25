import os
import logging
import asyncio
import socket
from yt_dlp import YoutubeDL

logger = logging.getLogger("Downloader")

BASE_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-us,en;q=0.5',
    'Sec-Fetch-Mode': 'navigate',
}

COOKIE_FILE = None
if os.path.exists("cookies.txt"):
    COOKIE_FILE = "cookies.txt"


def _ip_family_works(family: int) -> bool:
    """Cek apakah bisa connect ke YouTube via family IP tertentu."""
    try:
        infos = socket.getaddrinfo("www.youtube.com", 443, family, socket.SOCK_STREAM)
        if not infos:
            return False
        s = socket.socket(family, socket.SOCK_STREAM)
        s.settimeout(2)
        s.connect(infos[0][4])
        s.close()
        return True
    except Exception:
        return False


# Cache hasil deteksi agar hanya dijalankan sekali (lazy, saat pemakaian pertama).
_SOURCE_ADDRESS = None
_SOURCE_DETECTED = False


def _get_source_address():
    """Deteksi otomatis stack IP yang berfungsi.

    Hybrid & kompatibel di semua environment:
      - IPv4 jalan, IPv6 rusak  -> '0.0.0.0'  (paksa IPv4)
      - IPv6 jalan, IPv4 rusak  -> '::'       (paksa IPv6)
      - keduanya jalan / tak tentu -> None   (biarkan OS memilih)
    """
    global _SOURCE_ADDRESS, _SOURCE_DETECTED
    if not _SOURCE_DETECTED:
        _SOURCE_DETECTED = True
        try:
            v4 = _ip_family_works(socket.AF_INET)
            v6 = _ip_family_works(socket.AF_INET6)
            if v4 and not v6:
                _SOURCE_ADDRESS = '0.0.0.0'
                logger.info("Network: IPv4 OK, IPv6 broken -> forcing IPv4 (source_address=0.0.0.0)")
            elif v6 and not v4:
                _SOURCE_ADDRESS = '::'
                logger.info("Network: IPv6 OK, IPv4 broken -> forcing IPv6 (source_address=::)")
            else:
                _SOURCE_ADDRESS = None
                logger.info(f"Network: IPv4={v4} IPv6={v6} -> letting OS choose")
        except Exception as e:
            _SOURCE_ADDRESS = None
            logger.warning(f"Source address detection failed: {e} (letting OS choose)")
    return _SOURCE_ADDRESS

BASE_YDl_OPTS = {
    'format': 'bestaudio/best',
    'outtmpl': 'downloads/%(id)s.%(ext)s',
    'geo_bypass': True,
    'nocheckcertificate': True,
    'quiet': True,
    'no_warnings': True,
    'prefer_ffmpeg': True,
    'retries': 10,
    'postprocessors': [
        {
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '128',
        }
    ],
    'http_headers': BASE_HEADERS,
    'user_agent': BASE_HEADERS['User-Agent'],
    'cookies_from_browser': ('chrome',),
    'extractor_args': {
        'youtube': {
            'player_client': ['android', 'web'],
            'skip': ['hls', 'dash'],
            'player_skip': ['configs', 'webpage'],
        }
    }
}

if COOKIE_FILE:
    BASE_YDl_OPTS['cookiefile'] = COOKIE_FILE


def audio_dl_progress(url: str, progress_callback=None):
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

    ydl_opts = BASE_YDl_OPTS.copy()
    src = _get_source_address()
    if src is not None:
        ydl_opts['source_address'] = src

    if progress_callback:
        def hook(d):
            if d['status'] == 'downloading':
                total = d.get('total_bytes')
                if total is None:
                    total = d.get('total_bytes_estimate', 0)
                if total is None:
                    total = 0

                downloaded = d.get('downloaded_bytes', 0)
                if downloaded is None:
                    downloaded = 0

                speed = d.get('speed')
                percent = (downloaded / total * 100) if total > 0 else 0
                speed_str = "N/A"
                if speed is not None and speed > 0:
                    speed_str = f"{speed/1024/1024:.1f} MB/s"

                if loop and loop.is_running():
                    loop.call_soon_threadsafe(progress_callback, percent, speed_str)

            elif d['status'] == 'finished':
                if loop and loop.is_running():
                    loop.call_soon_threadsafe(progress_callback, 100, "Selesai")

        ydl_opts['progress_hooks'] = [hook]

    ydl = YoutubeDL(ydl_opts)

    try:
        sin = ydl.extract_info(url, download=False)
        if not sin:
            raise Exception("Failed to extract video info")

        video_id = sin.get('id')
        if not video_id:
            raise Exception("Video ID not found")

        x_file = os.path.join("downloads", f"{video_id}.mp3")
        if os.path.exists(x_file):
            logger.info(f"File already exists: {x_file}")
            if progress_callback and loop and loop.is_running():
                loop.call_soon_threadsafe(progress_callback, 100, "File sudah ada")
            return x_file

        logger.info(f"Downloading: {sin.get('title', 'Unknown')}")

        # Untuk video multi-bahasa (dubbed): prioritaskan audio bahasa asli.
        orig_lang = sin.get('language')
        if orig_lang:
            ydl.params['format'] = f"bestaudio[language={orig_lang}]/bestaudio/best"

        ydl.download([url])

        if os.path.exists(x_file):
            logger.info(f"Download complete: {x_file}")
            return x_file
        else:
            raise Exception(f"File not found after download: {x_file}")
    except Exception as e:
        logger.error(f"Download error: {e}")
        raise


def audio_dl(url: str) -> str:
    return audio_dl_progress(url, None)


def get_stream_url(url: str, is_video: bool = True):
    """Ambil SATU URL streaming langsung dari YouTube.

    Mengembalikan format muxed (audio+video menyatu dalam satu stream) supaya:
      - tidak perlu memisah audio/video -> tidak ada desinkron (suara kecepatan).
      - suara asli video tetap utuh (muxed progresif = audio original).
    Fallback: format direct apa pun (hindari manifest HLS/DASH).
    """
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': False,
        'http_headers': BASE_HEADERS,
        'user_agent': BASE_HEADERS['User-Agent'],
        'cookies_from_browser': ('chrome',),
        'source_address': _get_source_address(),
        'retries': 10,
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'web'],
                'skip': ['hls', 'dash'],
                'player_skip': ['configs', 'webpage'],
            }
        },
    }
    if COOKIE_FILE:
        ydl_opts['cookiefile'] = COOKIE_FILE

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if not info:
                return None

            if is_video:
                formats = info.get('formats', []) or []

                def _is_direct(f):
                    u = f.get('url') or ''
                    return bool(u) and 'manifest' not in u.lower()

                # 1) Muxed: audio + video menyatu (ideal, 1 URL, tanpa desync).
                muxed = sorted(
                    [f for f in formats if _is_direct(f)
                     and f.get('vcodec', 'none') != 'none'
                     and f.get('acodec', 'none') != 'none'],
                    key=lambda f: (f.get('width') or 0) * (f.get('height') or 0),
                    reverse=True,
                )
                if muxed:
                    return muxed[0].get('url')

                # 2) Fallback: format direct resolusi tertinggi.
                direct = sorted(
                    [f for f in formats if _is_direct(f)],
                    key=lambda f: (f.get('width') or 0) * (f.get('height') or 0),
                    reverse=True,
                )
                return direct[0].get('url') if direct else None
            else:
                for f in info.get('formats', []):
                    if f.get('acodec', 'none') != 'none' and f.get('vcodec', 'none') == 'none':
                        return f.get('url')
                return None
    except Exception as e:
        logger.error(f"Get stream URL error: {e}")
        raise


def search_youtube(query: str):
    ydl_opts_search = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': True,
        'http_headers': BASE_HEADERS,
        'user_agent': BASE_HEADERS['User-Agent'],
        'cookies_from_browser': ('chrome',),
        'source_address': _get_source_address(),
        'retries': 10,
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'web'],
                'skip': ['hls', 'dash'],
                'player_skip': ['configs', 'webpage'],
            }
        }
    }

    if COOKIE_FILE:
        ydl_opts_search['cookiefile'] = COOKIE_FILE

    try:
        with YoutubeDL(ydl_opts_search) as ydl_search:
            if query.startswith(('http://', 'https://')):
                info = ydl_search.extract_info(query, download=False)
                if info:
                    return {
                        'title': info.get('title', 'Unknown'),
                        'duration': info.get('duration', 0),
                        'id': info.get('id', ''),
                        'url': query,
                    }
                return None

            search_query = f"ytsearch1:{query}"
            info = ydl_search.extract_info(search_query, download=False)

            if info and 'entries' in info and info['entries']:
                entry = info['entries'][0]
                return {
                    'title': entry.get('title', 'Unknown'),
                    'duration': entry.get('duration', 0),
                    'id': entry.get('id', ''),
                    'url': f"https://youtube.com/watch?v={entry.get('id', '')}",
                }
            return None
    except Exception as e:
        logger.error(f"Search error: {e}")
        return None


def get_playlist_videos(url: str, limit: int = 10):
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': True,
        'ignoreerrors': True,
        'http_headers': BASE_HEADERS,
        'user_agent': BASE_HEADERS['User-Agent'],
        'cookies_from_browser': ('chrome',),
        'source_address': _get_source_address(),
        'retries': 10,
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'web'],
                'skip': ['hls', 'dash'],
                'player_skip': ['configs', 'webpage'],
            }
        }
    }

    if COOKIE_FILE:
        ydl_opts['cookiefile'] = COOKIE_FILE

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if not info:
                return None

            if 'entries' not in info:
                return None

            videos = []
            count = 0
            for entry in info['entries']:
                if not entry:
                    continue
                if count >= limit:
                    break
                video_id = entry.get('id')
                if not video_id:
                    continue
                videos.append({
                    'title': entry.get('title', f'Video {count+1}'),
                    'duration': entry.get('duration', 0),
                    'id': video_id,
                    'url': f"https://youtube.com/watch?v={video_id}",
                })
                count += 1

            return videos
    except Exception as e:
        logger.error(f"Get playlist error: {e}")
        return None


def is_playlist_url(url: str) -> bool:
    return 'playlist' in url.lower() or 'list=' in url
