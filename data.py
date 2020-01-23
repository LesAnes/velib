import json
from typing import List

import pandas as pd


def data_from_station(station_id: int) -> pd.DataFrame:
    return pd.read_csv(f'data/stations_status/{station_id}.csv')


def stations_information() -> pd.DataFrame:
    with open('data/station_information.json', 'r') as f:
        information = json.load(f)
    stations: List = information.get('data').get('stations')
    return pd.DataFrame(stations)
