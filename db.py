from os import getenv
from os.path import join, dirname

import pymongo
import requests
from dotenv import load_dotenv

from models import LatLngBoundsLiteral

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

myclient = pymongo.MongoClient(
    f"{getenv('MONGODB_URI')}/stations?ssl=true&replicaSet=Velibetter-shard-0&authSource=admin&retryWrites=true&w=majority"
)


def get_station_information_collection():
    db = myclient["stations"]
    return db["station_information"]


def get_stations_status_collection():
    db = myclient["stations"]
    return db["stations_status"]


def get_stations_last_state_collection():
    db = myclient["stations"]
    return db["stations_last_state"]


def get_station_status(station_id):
    col = get_stations_status_collection()
    return list(col.find({"station_id": station_id}))


def get_last_station_status(station_id):
    col = get_stations_last_state_collection()
    return list(col.find({"station_id": station_id}, {"_id": 0}))[0]


def get_station_information(station_id):
    col = get_station_information_collection()
    return list(col.find({"station_id": station_id}, {"_id": 0}))[0]


def get_last_stations_status(station_ids, departure=True):
    col = get_stations_last_state_collection()
    if departure:
        return list(col.find({"station_id": {"$in": station_ids}, "is_installed": 1, "is_renting": 1}, {"_id": 0}))
    return list(col.find({"station_id": {"$in": station_ids}, "is_installed": 1, "is_returning": 1}, {"_id": 0}))


def get_last_station_status_from_api():
    req = requests.get("https://velib-metropole-opendata.smoove.pro/opendata/Velib_Metropole/station_status.json")
    return req.json()["stations"]


def get_stations_information_in_polygon(latLngBoundsLiteral: LatLngBoundsLiteral):
    col = get_station_information_collection()
    return list(col.find({
        "loc": {
            "$geoWithin": {
                "$box": [
                    [latLngBoundsLiteral.west, latLngBoundsLiteral.south],
                    [latLngBoundsLiteral.east, latLngBoundsLiteral.north]
                ]
            }
        }
    }, {"_id": 0}))


def get_closest_stations_information(latitude: float, longitude: float):
    col = get_station_information_collection()
    return list(col.aggregate([
        {
            "$geoNear": {
                "near": {"type": "Point", "coordinates": [longitude, latitude]},
                "key": "loc",
                "distanceField": "distance",
                "maxDistance": 1000
            }
        },
        {"$limit": 15}
    ]))
