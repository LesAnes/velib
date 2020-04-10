from os import getenv
from os.path import join, dirname

import pymongo
from dotenv import load_dotenv

from models import LatLngBoundsLiteral, Coordinate

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


def get_stations_feedback_collection():
    db = myclient["stations"]
    return db["stations_feedback"]


def get_station_status(station_id):
    col = get_stations_status_collection()
    return list(col.find({"station_id": station_id}))


def get_last_station_status(station_id):
    col = get_stations_last_state_collection()
    return list(col.find({"station_id": station_id}, {"_id": 0}))[0]


def get_last_stations_status(station_ids, departure=True):
    col = get_stations_last_state_collection()
    if departure:
        return list(col.find({"station_id": {"$in": station_ids}, "is_installed": 1, "is_renting": 1}, {"_id": 0}))
    return list(col.find({"station_id": {"$in": station_ids}, "is_installed": 1, "is_returning": 1}, {"_id": 0}))


def get_station_information(station_id):
    col = get_station_information_collection()
    return list(col.find({"station_id": station_id}, {"_id": 0}))[0]


def get_stations_information_in_polygon(lat_lng_bounds_literal: LatLngBoundsLiteral,
                                        current_position: Coordinate = None):
    col = get_station_information_collection()
    return list(col.find({
        "loc": {
            "$geoWithin": {
                "$box": [
                    [lat_lng_bounds_literal.west, lat_lng_bounds_literal.south],
                    [lat_lng_bounds_literal.east, lat_lng_bounds_literal.north]
                ]
            }
        }
    }, {"_id": 0}))


def get_station_information_with_distance(station_id: int, latitude: float, longitude: float):
    col = get_station_information_collection()
    return list(col.aggregate([
        {
            "$geoNear": {
                "near": {"type": "Point", "coordinates": [longitude, latitude]},
                "key": "loc",
                "distanceField": "distance",
            }
        },
        {"$match": {"station_id": station_id}},
    ]))


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
        }, {"$limit": 15}
    ]))


def get_station_feedback(station_id):
    col = get_stations_feedback_collection()
    return list(col.find({"station_id": station_id}, {"_id": 0}))[0]


def submit_feedback(feedback):
    stations_feedback_col = get_stations_feedback_collection()
    try:
        if len(get_station_feedback(feedback.get("stationId"))) > 0:
            stations_feedback_col.update_one(
                {"station_id": feedback.get('station_id')},
                {"$set": feedback}
            )
    except IndexError:
        stations_feedback_col.insert_one(feedback)
