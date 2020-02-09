import json
import math
from datetime import timedelta
from enum import Enum

from cachier import cachier
from fastapi import FastAPI

from data import stations_information, get_stations, get_stations_with_bikes, get_stations_with_docks
from db import get_stations_status_collection, get_station_status
from distances import distance_between
from modelling import format_data, train_time_series, forecast_time_series

app = FastAPI()


class BikeType(str, Enum):
    mechanical = "mechanical"
    ebike = "ebike"


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/predict/{station_id}/{bike_type}/{delta_hours}")
def predict_number_bike_at_station(station_id: int, bike_type: BikeType, delta_hours: int = 1):
    station_status_collection = get_stations_status_collection()
    try:
        station_status = get_station_status(station_status_collection, station_id)
        df = format_data(station_status)
    except FileNotFoundError:
        return {"error": f"station {station_id} not found"}
    m = train_time_series(df)
    forecast = forecast_time_series(m, delta_hours)
    num_bikes = math.ceil(forecast.loc[len(df) - 1, "yhat"]) if forecast.loc[len(df) - 1, "yhat"] > 0 else 0
    return {"station_id": station_id, "bike_type": bike_type, "delta_hours": delta_hours, "forecast": num_bikes}


@app.get("/stations/")
@cachier(stale_after=timedelta(minutes=2))
def all_stations(latitude: float, longitude: float):
    information = stations_information()
    stations = get_stations()
    information.loc[:, "distance"] = information.apply(
        lambda row: distance_between(latitude, longitude, row.lat, row.lon), axis=1)
    information_sorted = information.sort_values(by="distance").reset_index()
    information_sorted['last_state'] = information_sorted.station_id.apply(lambda x: stations.get(x))
    available_for_departure = get_stations_with_bikes(information_sorted.station_id.values[:10])
    available_for_arrival = get_stations_with_docks(information_sorted.station_id.values[:10])
    information_sorted.loc[:, 'index_departure'] = information_sorted.station_id.apply(
        lambda x: available_for_departure.index(x) if x in available_for_departure else -1)
    information_sorted.loc[:, 'index_arrival'] = information_sorted.station_id.apply(
        lambda x: available_for_arrival.index(x) if x in available_for_arrival else -1)
    return json.loads(information_sorted.drop("index", axis=1).to_json(orient='records'))
