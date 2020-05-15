import json

from fuzzywuzzy import process

from models import Coordinate

with open('./adresse_paris.json', 'r') as f:
    addresses_json = json.load(f)
    addresses = {a.get('recordid', ""): a.get(
        'fields', {}).get('l_adr', "") for a in addresses_json}


def geocode(place: str) -> Coordinate:
    result = process.extractOne(place, addresses)
    if result is None:
        raise "no address found"
    (closest_address, confidence, cutoff) = result
    if confidence < 90:
        raise "no address found"
    address_index = list(addresses.values()).index(closest_address)
    [lat, lng] = addresses_json[address_index].get(
        "fields", {}).get("geom_x_y")
    return Coordinate(lat=lat, lng=lng)
