import requests
import time
import numpy as np
import pandas as pd
from datetime import datetime
from pathlib import Path

STATION_STATUS_URL = "https://velib-metropole-opendata.smoove.pro/opendata/Velib_Metropole/station_status.json"
DATA_ROOT = "data/stations_status"

while True:
    print(datetime.now())
    req = requests.get(STATION_STATUS_URL)
    if req.status_code == 200:
        stations = req.json().get('data').get('stations')

        for station in stations:
            STATION_PATH = f'{DATA_ROOT}/{station.get("station_id")}.csv'
            if Path(STATION_PATH).exists():
                old_state = pd.read_csv(STATION_PATH)
                n = len(old_state)
                if int(station.get('last_reported')) > int(old_state.loc[n-1, 'last_reported']):
                    print(f'status updated for station {station.get("station_id")}')
                    new_state = pd.DataFrame(station)
                    dataframe = pd.concat([old_state, new_state])
                    dataframe.to_csv(STATION_PATH, index=None)
            else:
                dataframe = pd.DataFrame(station)
                dataframe.to_csv(STATION_PATH, index=None)

    time.sleep(60)