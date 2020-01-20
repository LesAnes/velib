import requests
import time
import numpy as np
import pandas as pd
from datetime import datetime
from pathlib import Path

STATION_STATUS_URL = "https://opendata.paris.fr/api/records/1.0/search/?dataset=velib-disponibilite-en-temps-reel&rows=1393"
DATA_ROOT = "data/paris_data"

while True:
    print(datetime.now())
    req = requests.get(STATION_STATUS_URL)
    if req.status_code == 200:
        stations = req.json().get('records')

        for station in stations:
            STATION_PATH = f'{DATA_ROOT}/{station.get("recordid")}.csv'
            record_id = station.get("recordid")
            timestamp = station.get('record_timestamp')
            geo = station.get('fields').get('geo')
            del station['fields']['geo']
            if Path(STATION_PATH).exists():
                old_state = pd.read_csv(STATION_PATH)
                n = len(old_state)
                if pd.to_datetime(timestamp) > pd.to_datetime(old_state.loc[n-1, 'record_timestamp']):
                    new_state = pd.DataFrame(station.get('fields'), index=[record_id])
                    new_state['lat'] = geo[0]
                    new_state['lon'] = geo[1]
                    new_state['record_timestamp'] = timestamp
                    dataframe = pd.concat([old_state, new_state])
                    dataframe.to_csv(STATION_PATH, index=None)
            else:
                dataframe = pd.DataFrame(station.get('fields'), index=[record_id])
                dataframe['lat'] = geo[0]
                dataframe['lon'] = geo[1]
                dataframe['record_timestamp'] = timestamp
                dataframe.to_csv(STATION_PATH, index=None)

    time.sleep(60)