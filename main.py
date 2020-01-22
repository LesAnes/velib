from fastapi import FastAPI
from enum import Enum
from datetime import datetime
import pandas as pd
from modelling import read_data, train_time_series, forecast_time_series

app = FastAPI()

class BikeType(str, Enum):
    mechanical = "mechanical"
    ebike = "ebike"

@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/state/{station_id}/{bike_type}")
def number_bike_at_station(station_id: int, bike_type: BikeType):
    df = read_data(station_id)
    return {"station_id": station_id, "bike_type": bike_type, "number_bike": forecast.loc[len(df) - 1, bike_type]}


@app.get("/predict/{station_id}/{bike_type}/{delta_hours}")
def predict_number_bike_at_station(station_id: int, bike_type: BikeType, delta_hours: int = 1):
    df = read_data(station_id)
    m = train_time_series(df)
    forecast = forecast_time_series(m, delta_hours)
    return {"station_id": station_id, "bike_type": bike_type, "delta_hours": delta_hours,
        "forecast": int(forecast.loc[len(df) - 1, "yhat"])}
