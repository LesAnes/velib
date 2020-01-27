import json
from typing import List
from pathlib import Path

import pandas as pd


def data_from_station(station_id: int) -> pd.DataFrame:
    return pd.read_csv(f'data/stations_status/{station_id}.csv')


def stations_information() -> pd.DataFrame:
    with open('data/station_information.json', 'r') as f:
        information = json.load(f)
    stations: List = information.get('data').get('stations')
    return pd.DataFrame(stations)


def get_stations() -> dict:
    stations = {}
    for p in Path("data/stations_status").glob("*.csv"):
        station = pd.read_csv(p)
        stations[station.station_id.values[-1]] = {
            k: station[k].values[-1]
            for k in ["num_bikes_available", "num_docks_available", "is_installed", "is_returning", "is_renting",
                      "last_reported", "mechanical", "ebike"]
        }
    return stations


def get_stations_with_bikes(station_ids: List[int]) -> List[int]:
    stations_with_bikes = []
    for i in station_ids:
        station = pd.read_csv(f"data/stations_status/{i}.csv")
        if station.mechanical.values[-1] > 0 or station.ebike.values[-1] > 0:
            stations_with_bikes.append(station.station_id.values[-1])
    return stations_with_bikes


def get_stations_with_docks(station_ids: List[int]) -> List[int]:
    stations_with_docks = []
    for i in station_ids:
        station = pd.read_csv(f"data/stations_status/{i}.csv")
        if station.num_docks_available.values[-1] > 0:
            stations_with_docks.append(station.station_id.values[-1])
    return stations_with_docks
