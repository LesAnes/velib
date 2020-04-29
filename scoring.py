import math
import numpy as np

from modelling import get_stationarity_penalty


def score_station(station, departure=True):
    if departure:
        score = 20 * station["num_bikes_available"] / np.log2(0.1 * station["distance"])
    else:
        score = 100 * station["num_docks_available"] / ( 0.1 * station["distance"])
    station["score"] = max(1, min(math.floor(score - get_stationarity_penalty(station, departure)), 99))
    return station
