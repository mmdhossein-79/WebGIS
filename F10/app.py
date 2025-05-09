from flask import Flask, render_template, request
import math

app = Flask(__name__)

# تابع تبدیل Tile به BBOX
def tile_to_bbox(tile_x, tile_y, zoom):
    def tile_to_lon_lat(x, y, z):
        n = 2 ** z
        lon_deg = x / n * 360.0 - 180.0
        lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * y / n)))
        lat_deg = math.degrees(lat_rad)
        return lon_deg, lat_deg

    min_lon, max_lat = tile_to_lon_lat(tile_x, tile_y, zoom)
    max_lon, min_lat = tile_to_lon_lat(tile_x + 1, tile_y + 1, zoom)
    return min_lon, min_lat, max_lon, max_lat

# تابع تبدیل مختصات به Tile
def lon_lat_to_tile(lon, lat, zoom):
    lat_rad = math.radians(lat)
    n = 2 ** zoom
    tile_x = int((lon + 180.0) / 360.0 * n)
    tile_y = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
    return tile_x, tile_y

@app.route('/', methods=['GET', 'POST'])
def index():
    bbox_result = None
    tile_result = None
    
    if request.method == 'POST':
        if 'tile_x' in request.form:
            try:
                tile_x = int(request.form['tile_x'])
                tile_y = int(request.form['tile_y'])
                zoom = int(request.form['zoom'])
                min_lon, min_lat, max_lon, max_lat = tile_to_bbox(tile_x, tile_y, zoom)
                bbox_result = {
                    'min_lon': round(min_lon, 6),
                    'min_lat': round(min_lat, 6),
                    'max_lon': round(max_lon, 6),
                    'max_lat': round(max_lat, 6)
                }
            except ValueError:
                bbox_result = {'error': 'لطفاً مقادیر عددی معتبر وارد کنید'}
        
        elif 'lon' in request.form:
            try:
                lon = float(request.form['lon'])
                lat = float(request.form['lat'])
                zoom = int(request.form['zoom'])
                tile_x, tile_y = lon_lat_to_tile(lon, lat, zoom)
                tile_result = {'tile_x': tile_x, 'tile_y': tile_y}
            except ValueError:
                tile_result = {'error': 'لطفاً مقادیر عددی معتبر وارد کنید'}

    return render_template('index.html', bbox_result=bbox_result, tile_result=tile_result)

if __name__ == '__main__':
    app.run(debug=True)