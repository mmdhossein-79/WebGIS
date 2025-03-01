from django.http import HttpResponse, FileResponse
import os
import requests
import logging

# تنظیم لاگ برای دیباگ
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# یه پوشه برای ذخیره Tileها
TILE_DIR = "tiles"

# اگه پوشه tiles وجود نداره، بسازش
if not os.path.exists(TILE_DIR):
    os.makedirs(TILE_DIR)

def get_tile(request):
    # گرفتن زوم و مختصات از کاربر
    zoom = request.GET.get('zoom')
    x = request.GET.get('x')
    y = request.GET.get('y')

    # چک کردن وجود پارامترها
    if not all([zoom, x, y]):
        return HttpResponse("لطفاً همه پارامترها رو وارد کنید", status=400)

    # تبدیل ورودی‌ها به عدد
    try:
        zoom, x, y = int(zoom), int(x), int(y)
    except ValueError:
        return HttpResponse("پارامترها باید عدد باشن", status=400)

    # بررسی محدوده زوم و مختصات (برای جلوگیری از خطا)
    if not (0 <= zoom <= 19):
        return HttpResponse("سطح زوم باید بین 0 تا 19 باشه", status=400)

    # مسیر فایل محلی
    tile_path = os.path.join(TILE_DIR, f"{zoom}_{x}_{y}.png")
    logger.debug(f"Checking tile at path: {tile_path}")

    # اگه Tile قبلاً دانلود شده، همونو بفرست
    if os.path.exists(tile_path):
        logger.debug("Tile found locally, sending file")
        try:
            return FileResponse(open(tile_path, 'rb'), content_type='image/png')
        except Exception as e:
            logger.error(f"Error opening file: {e}")
            return HttpResponse(f"خطا در باز کردن فایل: {e}", status=500)

    # دانلود Tile از OpenStreetMap (استفاده از سرور آینه‌ای)
    osm_url = f"https://a.tile.openstreetmap.org/{zoom}/{x}/{y}.png"
    headers = {'User-Agent': 'TileAPI/1.0 (https://yourwebsite.com; arshad@example.com)'}  # یه User-Agent ساده و مشخص
    logger.debug(f"Downloading tile from: {osm_url}")

    try:
        response = requests.get(osm_url, headers=headers, stream=True, timeout=10)

        if response.status_code == 200:
            logger.debug("Tile downloaded successfully, saving to disk")
            with open(tile_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
            return FileResponse(open(tile_path, 'rb'), content_type='image/png')
        else:
            logger.error(f"Error downloading tile - Status code: {response.status_code}")
            return HttpResponse(f"خطا در دانلود Tile - کد خطا: {response.status_code}", status=500)
    except requests.RequestException as e:
        logger.error(f"Network error downloading tile: {e}")
        return HttpResponse(f"خطا در اتصال به سرور OSM: {e}", status=500)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return HttpResponse(f"خطای غیرمنتظره: {e}", status=500)