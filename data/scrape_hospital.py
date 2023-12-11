import csv
import googlemaps
from datetime import datetime
from tqdm import tqdm

gmap = googlemaps.Client(key="AIzaSyCrgPMtuTn25NrXQRIBQs4QKmYK-xuO-Y8")

taiwan_cities = [
    "台北市",
    "新北市",
    "桃園市",
    "台中市",
    "台南市",
    "高雄市",
    "基隆市",
    "新竹市",
    "嘉義市",
    "新竹縣",
    "苗栗縣",
    "彰化縣",
    "南投縣",
    "雲林縣",
    "嘉義縣",
    "屏東縣",
    "宜蘭縣",
    "花蓮縣",
    "台東縣",
    "澎湖縣",
    "金門縣",
    "連江縣"
]

ids = []
keywods = ["動物醫院", "寵物醫院", "獸醫院", "野鳥學會", "寵物診所"]

for keyword in tqdm(keywods):
    for city in tqdm(taiwan_cities):
        # Request json data from google map
        gmap.geocode(city, language="zh-TW")
        loc = gmap.geocode(city, language="zh-TW")[0]["geometry"]["location"]

        # Request a list of nearby animal hospitals
        now = datetime.now()
        animal_hospital = gmap.places_nearby(keyword="動物醫院", location=loc, radius=25000)
        for hospital in animal_hospital["results"]:
            ids.append(hospital["place_id"])

ids = list(set(ids))

hospitals = []

for id in ids:
    place = gmap.place(place_id=id, language="zh-TW")
    try: 
        result = place["result"]
        name, address, phone = result["name"], result["formatted_address"], result["formatted_phone_number"]
        hospitals.append({"name": name, "address": address, "phone": phone})
    except:
        pass
    

# save as csv file
with open("animal_hospital.csv", "w", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["name", "address", "phone"])
    writer.writeheader()
    for hospital in hospitals:
        writer.writerow(hospital)