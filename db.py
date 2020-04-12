from os import getenv
from os.path import join, dirname

import pymongo
from dotenv import load_dotenv

from main import Feedback, FeedbackType
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


def get_station_status(station_id) -> list:
    col = get_stations_status_collection()
    return list(col.find({"station_id": station_id}))


def get_last_station_status(station_id) -> list:
    col = get_stations_last_state_collection()
    return list(col.find({"station_id": station_id}, {"_id": 0}))[0]


def get_last_stations_status(station_ids, departure=True) -> list:
    col = get_stations_last_state_collection()
    if departure:
        return list(col.find({"station_id": {"$in": station_ids}, "is_installed": 1, "is_renting": 1}, {"_id": 0}))
    return list(col.find({"station_id": {"$in": station_ids}, "is_installed": 1, "is_returning": 1}, {"_id": 0}))


def get_station_information(station_id) -> list:
    col = get_station_information_collection()
    return list(col.find({"station_id": station_id}, {"_id": 0}))[0]


def get_stations_information_in_polygon(lat_lng_bounds_literal: LatLngBoundsLiteral,
                                        current_position: Coordinate = None) -> list:
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


def get_station_information_with_distance(station_id: int, latitude: float, longitude: float) -> list:
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


def get_closest_stations_information(latitude: float, longitude: float) -> list:
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


def update_station_last_state(station):
    col = get_stations_last_state_collection()
    station.pop('_id')
    col.update_one(
        {"station_id": station.get('station_id')},
        {"$set": station}
    )


def submit_feedback(feedback) -> None:
    stations_feedback_col = get_stations_feedback_collection()
    stations_feedback_col.insert_one(feedback)


def is_valid_input(value: str) -> bool:
    try:
        int(value)
        return True
    except:
        return False


def apply_feedback(feedback: Feedback):
    s_status = get_last_station_status(feedback.stationId)
    station_total = int(s_status["mechanical"]) + int(s_status["ebike"]) + int(s_status["num_docks_available"])
    if feedback.type == FeedbackType.confirmed:
        s_status["mechanical"] = feedback.numberMechanical if is_valid_input(feedback.numberMechanical) else s_status[
            "mechanical"]
        s_status["ebike"] = feedback.numberEbike if is_valid_input(feedback.numberEbike) else s_status["ebike"]
        s_status["num_docks_available"] = feedback.numberDock if is_valid_input(feedback.numberDock) else s_status[
            "num_docks_available"]
    else:
        s_status["mechanical"] = min(station_total,
                                     max(0, int(s_status["mechanical"]) - int(feedback.numberMechanical))) \
            if is_valid_input(feedback.numberMechanical) else s_status["mechanical"]
        s_status["ebike"] = min(station_total, max(0, int(s_status["ebike"]) - int(feedback.numberEbike))) \
            if is_valid_input(feedback.numberMechanical) else s_status["ebike"]
        s_status["num_docks_available"] = min(station_total,
                                              max(0, int(s_status["num_docks_available"]) - int(feedback.numberEbike))) \
            if is_valid_input(feedback.numberMechanical) else s_status["num_docks_available"]
