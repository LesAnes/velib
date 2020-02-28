import requests


def fetch_velib_api() -> list:
    STATION_STATUS_URL = "https://velib-metropole-opendata.smoove.pro/opendata/Velib_Metropole/station_status.json"
    req = requests.get(STATION_STATUS_URL)
    if req.status_code == 200:
        stations = req.json().get('data').get('stations')
        return stations
    return []

def fetch_info_velib_api() -> list:
    STATION_STATUS_URL = "https://velib-metropole-opendata.smoove.pro/opendata/Velib_Metropole/station_information.json"
    req = requests.get(STATION_STATUS_URL)
    if req.status_code == 200:
        stations = req.json().get('data').get('stations')
        return stations
    return []
