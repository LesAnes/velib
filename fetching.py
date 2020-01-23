import time
from datetime import datetime
from pathlib import Path

import pandas as pd

from velib_api import fetch_velib_api

DATA_ROOT = "data/stations_status"

while True:
    print(datetime.now())
    stations = fetch_velib_api()
    for station in stations:
        STATION_PATH = f'{DATA_ROOT}/{station.get("station_id")}.csv'
        mechanical = station.get('num_bikes_available_types')[0].get('mechanical')
        ebike = station.get('num_bikes_available_types')[1].get('ebike')
        del station['num_bikes_available_types']
        if Path(STATION_PATH).exists():
            old_state = pd.read_csv(STATION_PATH)
            n = len(old_state)
            if int(station.get('last_reported')) > int(old_state.loc[n - 1, 'last_reported']):
                print(f'status updated for station {station.get("station_id")}')
                new_state = pd.DataFrame(station, index=[station.get("station_id")])
                new_state['mechanical'] = mechanical
                new_state['ebike'] = ebike
                dataframe = pd.concat([old_state, new_state])
                dataframe.to_csv(STATION_PATH, index=None)
        else:
            dataframe = pd.DataFrame(station, index=[station.get("station_id")])
            dataframe['mechanical'] = mechanical
            dataframe['ebike'] = ebike
            dataframe.to_csv(STATION_PATH, index=None)

    time.sleep(60 * 1)
