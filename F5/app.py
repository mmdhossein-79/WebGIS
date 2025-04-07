from flask import Flask, request, jsonify
import psycopg2
import math

app = Flask(__name__)

# تنظیمات اتصال به دیتابیس
DB_CONFIG = {
    "dbname": "webgis_project",
    "user": "postgres",
    "password": "Mm314816",  
    "host": "localhost",
    "port": "5432"
}

# تابع محاسبه فاصله با فرمول Haversine
def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371  # شعاع زمین به کیلومتر
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

@app.route('/nearest_restaurant', methods=['GET'])
def get_nearest_restaurant():
    try:
        user_lat = float(request.args.get('lat'))
        user_lon = float(request.args.get('lon'))
    except (TypeError, ValueError):
        return jsonify({"error": "لطفاً مختصات معتبر (lat و lon) وارد کنید"}), 400

    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
    except Exception as e:
        return jsonify({"error": f"خطا در اتصال به دیتابیس: {str(e)}"}), 500

    query = "SELECT id, name, lat, lon FROM restaurants;"
    cursor.execute(query)
    restaurants = cursor.fetchall()

    min_distance = float('inf')
    nearest_restaurant = None

    for restaurant in restaurants:
        restaurant_id, name, restaurant_lat, restaurant_lon = restaurant
        distance = calculate_distance(user_lat, user_lon, restaurant_lat, restaurant_lon)
        if distance < min_distance:
            min_distance = distance
            nearest_restaurant = {
                "id": restaurant_id,
                "name": name,
                "lat": restaurant_lat,
                "lon": restaurant_lon,
                "distance_km": round(distance, 2)
            }

    cursor.close()
    conn.close()

    if nearest_restaurant:
        return jsonify(nearest_restaurant)
    else:
        return jsonify({"error": "هیچ رستورانی پیدا نشد"}), 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)