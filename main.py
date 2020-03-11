import json
import json
import math
from enum import Enum
from typing import List

import humps
from bson.json_util import dumps
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from api_mapping import lat_lng_mapping
from db import get_station_status, get_stations_information_in_polygon, get_station_information_collection, \
    get_stations_status_collection, get_closest_stations_information, get_last_stations_status, \
    get_last_station_status, get_station_information, get_station_information_with_distance
from modelling import format_data, train_time_series, forecast_time_series
from models import LatLngBoundsLiteral, Coordinate

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


@app.post("/stations-in-polygon/")
def closest_stations_information_list(latLngBoundsLiteral: LatLngBoundsLiteral, currentPosition: Coordinate = None):
    stations = get_stations_information_in_polygon(latLngBoundsLiteral)
    mapped_stations = list(map(lat_lng_mapping, stations))
    return json.loads(dumps(humps.camelize(mapped_stations)))


@app.post("/departure/")
def departure_list(currentPosition: Coordinate):
    stations_info = get_closest_stations_information(currentPosition.lat, currentPosition.lng)
    stations_status = get_last_stations_status([s["station_id"] for s in stations_info])
    stations = []
    for s_status in stations_status:
        s_id = s_status["station_id"]
        s_info = list(filter(lambda s: s["station_id"] == s_id, stations_info))[0]
        s_info.pop("_id")
        stations.append({**s_info, **s_status})
    mapped_stations = list(map(lat_lng_mapping, stations))
    sorted_stations = sorted(mapped_stations, key=lambda i: i['distance'])
    return json.loads(dumps(humps.camelize(sorted_stations)))


@app.post("/arrival/")
def arrival_list(currentPosition: Coordinate):
    stations_info = get_closest_stations_information(currentPosition.lat, currentPosition.lng)
    stations_status = get_last_stations_status([s["station_id"] for s in stations_info], departure=False)
    stations = []
    for s_status in stations_status:
        s_id = s_status["station_id"]
        s_info = list(filter(lambda s: s["station_id"] == s_id, stations_info))[0]
        s_info.pop("_id")
        stations.append({**s_info, **s_status})
    mapped_stations = list(map(lat_lng_mapping, stations))
    sorted_stations = sorted(mapped_stations, key=lambda i: i['distance'])
    return json.loads(dumps(humps.camelize(sorted_stations)))


@app.post("/stations/{station_id}")
def stations_status_single(station_id: int, current_position: Coordinate = None):
    s_info = {}
    if current_position:
        s_info = get_station_information_with_distance(station_id, current_position.lat, current_position.lng)[0]
        s_info.pop("_id")
    else:
        s_info = get_station_information(station_id)
    s_status = get_last_station_status(station_id)
    return json.loads(dumps(humps.camelize(lat_lng_mapping({**s_info, **s_status}))))
