import json
import math
from enum import Enum
from typing import List

import humps
from bson.json_util import dumps
from fastapi import FastAPI
from pydantic import BaseModel
from starlette.middleware.cors import CORSMiddleware

from api_mapping import lat_lng_mapping
from db import get_station_status, get_closest_stations_information, get_station_information_collection, \
    get_stations_status_collection, get_last_station_status
from modelling import format_data, train_time_series, forecast_time_series
from models import LatLngBoundsLiteral
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


@app.post("/closest-station-info-list/")
def closest_stations_information_list(latLngBoundsLiteral: LatLngBoundsLiteral):
    col = get_station_information_collection()
    stations = get_closest_stations_information(col, latLngBoundsLiteral)
    mapped_stations = list(map(lat_lng_mapping, stations))
    return json.loads(dumps(humps.camelize(mapped_stations)))


@app.get("/station-status/{station_id}")
def stations_status_list(station_id: int):
    col = get_stations_status_collection()
    station = get_last_station_status(col, station_id)
    return json.loads(dumps(humps.camelize(station)))


@app.post("/station-status-list/")
def stations_status_list(station_ids: List[int]):
    col = get_stations_status_collection()
    stations = [get_last_station_status(col, station_id) for station_id in station_ids]
    return json.loads(dumps(humps.camelize(stations)))


@app.get("/station-info-list/")
def station_information_list():
    col = get_station_information_collection()
    stations = list(col.find({}, {"_id": 0}))
    mapped_stations = list(map(lat_lng_mapping, stations))
    return json.loads(dumps(humps.camelize(mapped_stations)))
