import json
import math
from enum import Enum

from fastapi import FastAPI

from data import stations_information, data_from_station
from distances import distance_between
from modelling import format_data, train_time_series, forecast_time_series
from velib_api import fetch_velib_api

app = FastAPI()


class BikeType(str, Enum):
    mechanical = "mechanical"
    ebike = "ebike"


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/state/{station_id}")
def number_bike_at_station(station_id: int):
    try:
        station = data_from_station(station_id)
        n = len(station)
    except IndexError:
        return {"error": f"station {station_id} not found"}
    return json.loads(station.loc[n-1, :].to_json())


@app.get("/predict/{station_id}/{bike_type}/{delta_hours}")
def predict_number_bike_at_station(station_id: int, bike_type: BikeType, delta_hours: int = 1):
    try:
        df = format_data(station_id)
    except FileNotFoundError:
        return {"error": f"station {station_id} not found"}
    m = train_time_series(df)
    forecast = forecast_time_series(m, delta_hours)
    num_bikes = math.ceil(forecast.loc[len(df) - 1, "yhat"]) if forecast.loc[len(df) - 1, "yhat"] > 0 else 0
    return {"station_id": station_id, "bike_type": bike_type, "delta_hours": delta_hours, "forecast": num_bikes}


@app.get("/closest/{latitude}/{longitude}")
def closest_stations(latitude: float, longitude: float, top: int = None):
    information = stations_information()
    information.loc[:, "distance"] = information.apply(
        lambda row: distance_between(latitude, longitude, row.lat, row.lon), axis=1)
    information_sorted = information.sort_values(by="distance").reset_index()
    return json.loads(information_sorted.to_json(orient='records'))


@app.get("/stations")
def all_stations():
    information = stations_information()
    return json.loads(information.to_json(orient='records'))
