from datetime import datetime

from db import get_stations_status_collection, get_stations_last_state_collection, update_station_last_state, \
    remove_old_status
from velib_api import fetch_velib_api

stations_status_col = get_stations_status_collection()
stations_last_state_col = get_stations_last_state_collection()


def main():
    print(datetime.now())
    stations = fetch_velib_api()
    for station in stations:
        # Api mapping
        station['mechanical'] = station.get('num_bikes_available_types')[0].get('mechanical')
        station['ebike'] = station.get('num_bikes_available_types')[1].get('ebike')
        station['station_code'] = station.get('stationCode')
        del station['num_bikes_available_types']
        del station['numBikesAvailable']
        del station['numDocksAvailable']

        status_by_station_id = stations_status_col.find({'station_id': station.get('station_id')})
        status_by_station_id_sorted = status_by_station_id.sort('last_reported', -1)
        last_reported = status_by_station_id_sorted[0].get(
            'last_reported') if status_by_station_id_sorted.count() > 0 else None
        if last_reported and int(station.get('last_reported')) > int(last_reported):
            print(f'status updated for station {station.get("station_id")}')
            remove_old_status()
            stations_status_col.insert_one(station)
            update_station_last_state(station)


if __name__ == '__main__':
    main()
