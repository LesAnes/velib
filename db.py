from os.path import join, dirname

import pymongo
from os import getenv

from dotenv import load_dotenv

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
    return [el for el in db["stations_status"].find({})]


def get_station_status(station_id):
    return [el for el in myclient["stations"]["stations_status"].find({"station_id": station_id})]
