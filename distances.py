import numpy as np

from db import get_stations_status_collection, get_last_station_status, get_last_station_status_from_api


def distance_between(s_lat, s_lng, e_lat, e_lng):
    R = 6373.0
    s_lat = s_lat * np.pi / 180.0
    s_lng = np.deg2rad(s_lng)
    e_lat = np.deg2rad(e_lat)
    e_lng = np.deg2rad(e_lng)
    d = np.sin((e_lat - s_lat) / 2) ** 2 + np.cos(s_lat) * np.cos(e_lat) * np.sin((e_lng - s_lng) / 2) ** 2
    return 2 * R * np.arcsin(np.sqrt(d))


def sort_stations(latitude, longitude, status_collection, station_info):
    # station_status = get_last_station_status(status_collection, station_info["station_id"])
    station_status = get_last_station_status_from_api()
    if station_status["is_installed"] == 1 and station_status["is_returning"] == 1:
        station_info["distance"] = distance_between(latitude, longitude, station_info["loc"][1],
                                                    station_info["loc"][0])
    return station_info
