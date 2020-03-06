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


def get_station_status(station_id):
    return [el for el in myclient["stations"]["stations_status"].find({"station_id": station_id})]


def get_last_station_status(col, station_id):
    return col.find({"station_id": station_id}, {"_id": 0}).sort([("last_reported", pymongo.DESCENDING)]).limit(1)[0]


def get_last_station_status_from_api():
    req = requests.get("https://velib-metropole-opendata.smoove.pro/opendata/Velib_Metropole/station_status.json")
    return req.json()["stations"]


def get_closest_stations_information(col, latLngBoundsLiteral: LatLngBoundsLiteral):
    return [el for el in col.find({
        "loc": {
            "$geoWithin": {
                "$box": [
                    [latLngBoundsLiteral.west, latLngBoundsLiteral.south],
                    [latLngBoundsLiteral.east, latLngBoundsLiteral.north]
                ]
            }
        }
    }, {"_id": 0})]
