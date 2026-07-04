import os
import logging
import asyncio
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

BASE_YDl_OPTS = {
    'format': 'bestaudio/best',
    'outtmpl': 'downloads/%(id)s.%(ext)s',
    'geo_bypass': True,
    'nocheckcertificate': True,
    'quiet': True,
    'no_warnings': True,
    'prefer_ffmpeg': True,
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


def get_stream_url(url: str, is_video: bool = False) -> str:
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'format': 'bestvideo+bestaudio' if is_video else 'bestaudio',
        'extract_flat': False,
        'http_headers': BASE_HEADERS,
        'user_agent': BASE_HEADERS['User-Agent'],
        'cookies_from_browser': ('chrome',),
    }
    if COOKIE_FILE:
        ydl_opts['cookiefile'] = COOKIE_FILE

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if not info:
                return None

            if is_video:
                formats = info.get('formats', [])
                formats = sorted(formats, key=lambda f: (f.get('width', 0) or 0) * (f.get('height', 0) or 0), reverse=True)
                for f in formats:
                    if f.get('vcodec', 'none') != 'none' and f.get('acodec', 'none') != 'none':
                        return f.get('url')
                for f in formats:
                    if f.get('url'):
                        return f.get('url')
            else:
                for f in info.get('formats', []):
                    if f.get('acodec', 'none') != 'none' and f.get('vcodec', 'none') == 'none':
                        return f.get('url')
            return None
    except Exception as e:
        logger.error(f"Get stream URL error: {e}")
        return None


def search_youtube(query: str):
    ydl_opts_search = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': True,
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
