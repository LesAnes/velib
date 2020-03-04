import json
import math
from enum import Enum

import humps
from bson.json_util import dumps
from fastapi import FastAPI
from pydantic import BaseModel
from starlette.middleware.cors import CORSMiddleware

from db import get_station_information_collection, get_station_status, get_closest_stations_information
from modelling import format_data, train_time_series, forecast_time_series
from velib_api import fetch_velib_api

app = FastAPI()

origins = [
    "http://127.0.0.1:4200",
    "http://localhost:4200",
    "https://dazzling-agnesi-2a409f.netlify.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class BikeType(str, Enum):
    mechanical = "mechanical"
    ebike = "ebike"


class LatLngBoundsLiteral(BaseModel):
    east: float
    nort: float
    south: float
    west: float


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/predict/{station_id}/{bike_type}/{delta_hours}")
def predict_number_bike_at_station(station_id: int, bike_type: BikeType, delta_hours: int = 1):
    try:
        station_status = get_station_status(station_id)
        df = format_data(station_status)
    except FileNotFoundError:
        return {"error": f"station {station_id} not found"}
    m = train_time_series(df)
    forecast = forecast_time_series(m, delta_hours)
    num_bikes = math.ceil(forecast.loc[len(df) - 1, "yhat"]) if forecast.loc[len(df) - 1, "yhat"] > 0 else 0
    return {"station_id": station_id, "bike_type": bike_type, "delta_hours": delta_hours, "forecast": num_bikes}


#
# @app.get("/stations/")
# @cachier(stale_after=timedelta(minutes=2))
# def all_stations(latitude: float, longitude: float):
#     information = stations_information()
#     stations = get_stations()
#     information.loc[:, "distance"] = information.apply(
#         lambda row: distance_between(latitude, longitude, row.lat, row.lon), axis=1)
#     information_sorted = information.sort_values(by="distance").reset_index()
#     information_sorted['last_state'] = information_sorted.station_id.apply(lambda x: stations.get(x))
#     available_for_departure = get_stations_with_bikes(information_sorted.station_id.values[:10])
#     available_for_arrival = get_stations_with_docks(information_sorted.station_id.values[:10])
#     information_sorted.loc[:, 'index_departure'] = information_sorted.station_id.apply(
#         lambda x: available_for_departure.index(x) if x in available_for_departure else -1)
#     information_sorted.loc[:, 'index_arrival'] = information_sorted.station_id.apply(
#         lambda x: available_for_arrival.index(x) if x in available_for_arrival else -1)
#     return json.loads(information_sorted.drop("index", axis=1).to_json(orient='records'))


@app.get("/station-list/")
def station_list():
    stations = fetch_velib_api()
    return stations


@app.get("/closest-station-list/")
def closest_stations_information_list(latLngBoundsLiteral: LatLngBoundsLiteral):
    stations = get_closest_stations_information(latLngBoundsLiteral)
    return json.loads(dumps(humps.camelize(stations)))


@app.get("/station-info-list/")
def station_information_list():
    col = get_station_information_collection()
    return json.loads(dumps(humps.camelize(list(col.find({}, {"_id": 0})))))
