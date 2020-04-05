import math
import numpy as np


def score_station(station, departure=True):
    if departure:
        score = 20 * station["num_bikes_available"] / np.log2(0.1 * station["distance"])
    else:
        score = 10 * station["num_docks_available"] / np.log2(0.1 * station["distance"])
    station["score"] = min(math.floor(score), 99)
    return station
