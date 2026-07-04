import os
import re
import textwrap

import aiofiles
import aiohttp
import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter, ImageFont
from youtubesearchpython.__future__ import VideosSearch

from config import FAILED
from NovaMusic import BOT_ID, LOGGER, app

# ===== FALLBACK untuk Resampling =====
try:
    RESAMPLE_FILTER = Image.Resampling.LANCZOS
except AttributeError:
    RESAMPLE_FILTER = Image.LANCZOS


def changeImageSize(maxWidth, maxHeight, image):
    widthRatio = maxWidth / image.size[0]
    heightRatio = maxHeight / image.size[1]
    newWidth = int(widthRatio * image.size[0])
    newHeight = int(heightRatio * image.size[1])
    newImage = image.resize((newWidth, newHeight))
    return newImage


def add_corners(im):
    bigsize = (im.size[0] * 3, im.size[1] * 3)
    mask = Image.new("L", bigsize, 0)
    ImageDraw.Draw(mask).ellipse((0, 0) + bigsize, fill=255)
    mask = mask.resize(im.size, Image.LANCZOS)
    mask = ImageChops.darker(mask, im.split()[-1])
    im.putalpha(mask)


def get_text_size(draw, text, font):
    """Compatibility wrapper for Pillow 10+"""
    try:
        bbox = draw.textbbox((0, 0), text, font=font)
        return bbox[2] - bbox[0], bbox[3] - bbox[1]
    except AttributeError:
        return draw.textsize(text, font=font)


async def download_thumbnail(videoid: str) -> str:
    """Download thumbnail dari YouTube dengan fallback multiple source."""
    thumb_path = f"cache/thumb{videoid}.png"
    
    # Cek apakah sudah ada
    if os.path.exists(thumb_path):
        return thumb_path
    
    # Daftar URL thumbnail (dari kualitas tertinggi ke terendah)
    thumb_urls = [
        f"https://img.youtube.com/vi/{videoid}/maxresdefault.jpg",
        f"https://img.youtube.com/vi/{videoid}/hq720.jpg",
        f"https://img.youtube.com/vi/{videoid}/hqdefault.jpg",
        f"https://img.youtube.com/vi/{videoid}/mqdefault.jpg",
    ]
    
    async with aiohttp.ClientSession() as session:
        for url in thumb_urls:
            try:
                async with session.get(url, timeout=10) as resp:
                    if resp.status == 200:
                        content = await resp.read()
                        if len(content) > 1000:  # Pastikan bukan gambar placeholder
                            f = await aiofiles.open(thumb_path, mode="wb")
                            await f.write(content)
                            await f.close()
                            LOGGER.info(f"Thumbnail downloaded: {url}")
                            return thumb_path
            except Exception as e:
                LOGGER.warning(f"Failed to download thumbnail from {url}: {e}")
                continue
    
    return None


async def gen_thumb(videoid, user_id):
    # Cek cache
    cache_file = f"cache/{videoid}_{user_id}.png"
    if os.path.isfile(cache_file):
        return cache_file
    
    try:
        # Download thumbnail
        thumb_path = await download_thumbnail(videoid)
        if not thumb_path or not os.path.exists(thumb_path):
            LOGGER.error(f"Failed to download thumbnail for {videoid}")
            return FAILED
        
        # Get video info
        title = "Unsupported Title"
        duration = "Unknown"
        try:
            results = await VideosSearch(f"https://www.youtube.com/watch?v={videoid}", limit=1).next()
            result_list = results.get("result", [])
            if result_list:
                result = result_list[0]
                title = result.get("title", "Unsupported Title")
                title = re.sub(r"\W+", " ", title).title()
                duration = result.get("duration", "Unknown")
        except Exception as e:
            LOGGER.warning(f"Failed to get video info: {e}")

        # Download user photo
        try:
            user_photo = (await app.get_users(user_id)).photo
            if user_photo:
                wxy = await app.download_media(user_photo.big_file_id, file_name=f"{user_id}.jpg")
            else:
                wxy = None
        except:
            wxy = None

        if not wxy:
            wxy = await app.download_media(
                (await app.get_users(BOT_ID)).photo.big_file_id,
                file_name=f"{BOT_ID}.jpg",
            )

        # Process images
        xy = Image.open(wxy)
        a = Image.new("L", [640, 640], 0)
        b = ImageDraw.Draw(a)
        b.pieslice([(0, 0), (640, 640)], 0, 360, fill=255, outline="white")
        c = np.array(xy)
        d = np.array(a)
        e = np.dstack((c, d))
        f = Image.fromarray(e)
        x = f.resize((107, 107))

        youtube = Image.open(thumb_path)
        bg = Image.open(f"NovaMusic/Helpers/utils/circle.png")
        image1 = changeImageSize(1280, 720, youtube)
        image2 = image1.convert("RGBA")
        background = image2.filter(filter=ImageFilter.BoxBlur(30))
        enhancer = ImageEnhance.Brightness(background)
        background = enhancer.enhance(0.6)

        image3 = changeImageSize(1280, 720, bg)
        image5 = image3.convert("RGBA")
        Image.alpha_composite(background, image5).save(f"cache/temp{videoid}.png")

        Xcenter = youtube.width / 2
        Ycenter = youtube.height / 2
        x1 = Xcenter - 250
        y1 = Ycenter - 250
        x2 = Xcenter + 250
        y2 = Ycenter + 250
        logo = youtube.crop((x1, y1, x2, y2))
        logo.thumbnail((520, 520), RESAMPLE_FILTER)
        logo.save(f"cache/chop{videoid}.png")
        if not os.path.isfile(f"cache/cropped{videoid}.png"):
            im = Image.open(f"cache/chop{videoid}.png").convert("RGBA")
            add_corners(im)
            im.save(f"cache/cropped{videoid}.png")

        crop_img = Image.open(f"cache/cropped{videoid}.png")
        logo = crop_img.convert("RGBA")
        logo.thumbnail((365, 365), RESAMPLE_FILTER)
        width = int((1280 - 365) / 2)
        background = Image.open(f"cache/temp{videoid}.png")
        background.paste(logo, (width + 2, 138), mask=logo)
        background.paste(x, (710, 427), mask=x)
        background.paste(image3, (0, 0), mask=image3)

        draw = ImageDraw.Draw(background)
        font = ImageFont.truetype("NovaMusic/Helpers/utils/font2.ttf", 45)
        arial = ImageFont.truetype("NovaMusic/Helpers/utils/font2.ttf", 30)
        para = textwrap.wrap(title, width=32)

        try:
            draw.text(
                (450, 25),
                "STARTED PLAYING",
                fill="white",
                stroke_width=3,
                stroke_fill="grey",
                font=font,
            )
            if para:
                text_w, _ = get_text_size(draw, para[0], font)
                draw.text(
                    ((1280 - text_w) / 2, 530),
                    para[0],
                    fill="white",
                    stroke_width=1,
                    stroke_fill="white",
                    font=font,
                )
            if len(para) > 1:
                text_w, _ = get_text_size(draw, para[1], font)
                draw.text(
                    ((1280 - text_w) / 2, 580),
                    para[1],
                    fill="white",
                    stroke_width=1,
                    stroke_fill="white",
                    font=font,
                )
        except:
            pass

        duration_text = f"Duration: {duration} Mins"
        text_w, _ = get_text_size(draw, duration_text, arial)
        draw.text(
            ((1280 - text_w) / 2, 660),
            duration_text,
            fill="white",
            font=arial,
        )

        try:
            os.remove(f"cache/thumb{videoid}.png")
        except:
            pass
        background.save(cache_file)
        return cache_file
    except Exception as e:
        LOGGER.error(f"gen_thumb error: {e}")
        return FAILED


async def gen_qthumb(videoid, user_id):
    cache_file = f"cache/que{videoid}_{user_id}.png"
    if os.path.isfile(cache_file):
        return cache_file
    
    try:
        # Download thumbnail
        thumb_path = await download_thumbnail(videoid)
        if not thumb_path or not os.path.exists(thumb_path):
            LOGGER.error(f"Failed to download thumbnail for {videoid}")
            return FAILED
        
        # Get video info
        title = "Unsupported Title"
        duration = "Unknown"
        try:
            results = await VideosSearch(f"https://www.youtube.com/watch?v={videoid}", limit=1).next()
            result_list = results.get("result", [])
            if result_list:
                result = result_list[0]
                title = result.get("title", "Unsupported Title")
                title = re.sub(r"\W+", " ", title).title()
                duration = result.get("duration", "Unknown")
        except Exception as e:
            LOGGER.warning(f"Failed to get video info: {e}")

        # Download user photo (sama seperti di atas)
        try:
            user_photo = (await app.get_users(user_id)).photo
            if user_photo:
                wxy = await app.download_media(user_photo.big_file_id, file_name=f"{user_id}.jpg")
            else:
                wxy = None
        except:
            wxy = None

        if not wxy:
            wxy = await app.download_media(
                (await app.get_users(BOT_ID)).photo.big_file_id,
                file_name=f"{BOT_ID}.jpg",
            )

        # Proses gambar (sama seperti gen_thumb)
        xy = Image.open(wxy)
        a = Image.new("L", [640, 640], 0)
        b = ImageDraw.Draw(a)
        b.pieslice([(0, 0), (640, 640)], 0, 360, fill=255, outline="white")
        c = np.array(xy)
        d = np.array(a)
        e = np.dstack((c, d))
        f = Image.fromarray(e)
        x = f.resize((107, 107))

        youtube = Image.open(thumb_path)
        bg = Image.open(f"NovaMusic/Helpers/utils/circle.png")
        image1 = changeImageSize(1280, 720, youtube)
        image2 = image1.convert("RGBA")
        background = image2.filter(filter=ImageFilter.BoxBlur(30))
        enhancer = ImageEnhance.Brightness(background)
        background = enhancer.enhance(0.6)

        image3 = changeImageSize(1280, 720, bg)
        image5 = image3.convert("RGBA")
        Image.alpha_composite(background, image5).save(f"cache/temp{videoid}.png")

        Xcenter = youtube.width / 2
        Ycenter = youtube.height / 2
        x1 = Xcenter - 250
        y1 = Ycenter - 250
        x2 = Xcenter + 250
        y2 = Ycenter + 250
        logo = youtube.crop((x1, y1, x2, y2))
        logo.thumbnail((520, 520), RESAMPLE_FILTER)
        logo.save(f"cache/chop{videoid}.png")
        if not os.path.isfile(f"cache/cropped{videoid}.png"):
            im = Image.open(f"cache/chop{videoid}.png").convert("RGBA")
            add_corners(im)
            im.save(f"cache/cropped{videoid}.png")

        crop_img = Image.open(f"cache/cropped{videoid}.png")
        logo = crop_img.convert("RGBA")
        logo.thumbnail((365, 365), RESAMPLE_FILTER)
        width = int((1280 - 365) / 2)
        background = Image.open(f"cache/temp{videoid}.png")
        background.paste(logo, (width + 2, 138), mask=logo)
        background.paste(x, (710, 427), mask=x)
        background.paste(image3, (0, 0), mask=image3)

        draw = ImageDraw.Draw(background)
        font = ImageFont.truetype("NovaMusic/Helpers/utils/font2.ttf", 45)
        arial = ImageFont.truetype("NovaMusic/Helpers/utils/font2.ttf", 30)
        para = textwrap.wrap(title, width=32)

        try:
            draw.text(
                (455, 25),
                "ADDED TO QUEUE",
                fill="white",
                stroke_width=5,
                stroke_fill="black",
                font=font,
            )
            if para:
                text_w, _ = get_text_size(draw, para[0], font)
                draw.text(
                    ((1280 - text_w) / 2, 530),
                    para[0],
                    fill="white",
                    stroke_width=1,
                    stroke_fill="white",
                    font=font,
                )
            if len(para) > 1:
                text_w, _ = get_text_size(draw, para[1], font)
                draw.text(
                    ((1280 - text_w) / 2, 580),
                    para[1],
                    fill="white",
                    stroke_width=1,
                    stroke_fill="white",
                    font=font,
                )
        except:
            pass

        duration_text = f"Duration: {duration} Mins"
        text_w, _ = get_text_size(draw, duration_text, arial)
        draw.text(
            ((1280 - text_w) / 2, 660),
            duration_text,
            fill="white",
            font=arial,
        )

        try:
            os.remove(f"cache/thumb{videoid}.png")
        except:
            pass
        background.save(cache_file)
        return cache_file
    except Exception as e:
        LOGGER.error(f"gen_qthumb error: {e}")
        return FAILED
