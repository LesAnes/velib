from enum import Enum

from fastapi import FastAPI

from modelling import read_data, train_time_series, forecast_time_series
from velib_api import fetch_velib_api

app = FastAPI()


class BikeType(str, Enum):
    mechanical = "mechanical"
    ebike = "ebike"


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/state/{station_id}")
def number_bike_at_station(station_id: int):
    stations = fetch_velib_api()
    try:
        station = list(filter(lambda s: s.get("station_id") == station_id, stations))[0]
    except IndexError:
        return {"station_id": station_id, "error": f"station {station_id} not found"}
    try:
        mechanical = station.get('num_bikes_available_types')[0].get('mechanical')
        ebike = station.get('num_bikes_available_types')[1].get('ebike')
    except IndexError:
        return {"station_id": station_id, "error": "no data available"}
    return {"station_id": station_id, "num_bikes_available_mechanical": mechanical, "num_bikes_available_ebike": ebike}


@app.get("/predict/{station_id}/{bike_type}/{delta_hours}")
def predict_number_bike_at_station(station_id: int, bike_type: BikeType, delta_hours: int = 1):
    df = read_data(station_id)
    m = train_time_series(df)
    forecast = forecast_time_series(m, delta_hours)
    num_bikes = int(forecast.loc[len(df) - 1, "yhat"])
    return {"station_id": station_id, "bike_type": bike_type, "delta_hours": delta_hours,
            "forecast": num_bikes}
