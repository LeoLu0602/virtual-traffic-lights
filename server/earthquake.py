import requests
import math
import time
from geopy.distance import geodesic
import pyttsx3
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
supabase = create_client(os.getenv("URL"), os.getenv("KEY"))

# 車輛當前位置（需要替換為實際的 GPS 資料）
vehicle_location = (-15.7535, -74.1516)  # (latitude, longitude)

# 初始化語音引擎
engine = pyttsx3.init()

# 定義計算 MMI 的函數
def calculate_mmi(magnitude, distance):
    # 防止距離為零導致的數學錯誤
    if distance == 0:
        distance = 0.1
    MMI = 1.5 * magnitude - math.log10(distance) - 3.0
    return MMI

# 主函數
def fetch_and_alert():
    try:
        # 定義 USGS API 端點和參數
        url = 'https://earthquake.usgs.gov/fdsnws/event/1/query'

        params = {
            'format': 'geojson',
            'starttime': 'now-1minutes',  # 只獲取最近 5 分鐘內的地震
            'minmagnitude': 5             # 最小震級，可根據需求調整
        }

        # 發送 GET 請求
        response = requests.get(url, params=params)

        # 檢查請求是否成功
        if response.status_code == 200:
            data = response.json()
            # 檢查是否有新的地震事件
            if data['features']:
                for feature in data['features']:
                    properties = feature['properties']
                    mag = properties['mag']
                    place = properties['place']
                    time_epoch = properties['time'] / 1000  # 時間戳記（秒）
                    coordinates = feature['geometry']['coordinates']
                    longitude, latitude, depth = coordinates

                    # 計算震源距離
                    epicenter_location = (latitude, longitude)
                    distance = geodesic(vehicle_location, epicenter_location).kilometers

                    # 計算預估震度
                    mmi = calculate_mmi(mag, distance)

                    # 根據 MMI 提示駕駛員
                    if mmi >= 6:
                        message = f"occur at {place} a {mag} magnitude of earthquake, estimated Seismic Scale {mmi:.1f}, Please slow down immediately and find a safe place to stop."
                    elif mmi >= 5:
                        message = f"occur at {place} a {mag} magnitude of earthquake, estimated seismic scale {mmi:.1f}, It is recommended to reduce your speed while driving."
                    elif mmi >= 3:
                        message = f"occur at {place} a {mag} magnitude of earthquake, estimated seismic scale {mmi:.1f}, Please pay attention and be aware of your surroundings."
                    else:
                        message = f"occur at {place} 的 {mag} magnitude of earthquake, estimated seismic scale {mmi:.1f}, No special action needed."

                    print(message)

                    supabase.table("intersection").upsert(
                        {
                            "id": 1,
                            "earthquake_alert": message,
                        }
                    ).execute()
                    time.sleep(5)
                    supabase.table("intersection").upsert(
                        {
                            "id": 1,
                            "earthquake_alert": '',
                        }
                    ).execute()

                    # 語音提示
                    engine.say(message)
                    engine.runAndWait()
            else:
                print("No new earthquake events at this time.")
        else:
            print(f"An error occurred while fetching data.：{response.status_code}")
    except Exception as e:
        print(f"error：{e}")

# 主循環，每 5 秒鐘執行一次
if __name__ == "__main__":
    # fake earthquake
    time.sleep(10)
    supabase.table("intersection").upsert(
        {
            "id": 1,
            "earthquake_alert": "Earthquake! Please slow down immediately and find a safe place to stop.",
        }
    ).execute()
    time.sleep(5)
    supabase.table("intersection").upsert(
        {
            "id": 1,
            "earthquake_alert": '',
        }
    ).execute()
    while True:
        fetch_and_alert()
        time.sleep(5)
