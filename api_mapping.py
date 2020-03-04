def lat_lng_mapping(station):
    [lng, lat] = station.pop("loc")
    station["lng"] = lng
    station["lat"] = lat
    return station
