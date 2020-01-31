import time
from datetime import datetime

from db import get_stations_status_collection
from velib_api import fetch_velib_api

col = get_stations_status_collection()

while True:
    print(datetime.now())
    stations = fetch_velib_api()
    for station in stations:
        mechanical = station.get('num_bikes_available_types')[0].get('mechanical')
        ebike = station.get('num_bikes_available_types')[1].get('ebike')
        del station['num_bikes_available_types']
        if int(station.get('last_reported')) > int(
                col.find({"station_id": station.get("station_id")}).sort("last_reported", -1)[0].get('last_reported')):
            print(f'status updated for station {station.get("station_id")}')
            station['mechanical'] = mechanical
            station['ebike'] = ebike
            col.insert_one(station)

    time.sleep(60 * 1)
