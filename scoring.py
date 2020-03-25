from models import Station


def score_station(station: Station, departure=True):
    if departure:
        score = 10000 * station.numBikesAvailable / (station.capacity * station.distance)
    else:
        score = 10000 * station.numDocksAvailable / (station.capacity * station.distance)
    station["score"] = score
    return station