import math


def score_station(station, departure=True):
    if departure:
        score = 10000 * station["num_bikes_available"] / (station["capacity"] * station["distance"])
    else:
        score = 10000 * station["num_docks_available"] / (station["capacity"] * station["distance"])
    station["score"] = math.floor(score)
    return station
