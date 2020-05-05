import math

import pandas as pd
from statsmodels.tsa.arima_model import ARMA
from statsmodels.tsa.stattools import adfuller

from db import get_station_status


def format_prediction_data(station_status, is_mechanical: bool = True, is_departure: bool = True) -> pd.DataFrame:
    station_status_df = pd.DataFrame(station_status)
    if is_departure:
        data = station_status_df['mechanical'].dropna().tolist() if is_mechanical else station_status_df[
            'ebike'].dropna().tolist()
    else:
        data = station_status_df['num_docks_available'].dropna().tolist()
    return pd.DataFrame(data)


def predict_time_series(station_status, is_mechanical: bool, max_bikes: int, delta: int,
                        is_departure: bool) -> int:
    df = format_prediction_data(station_status, is_mechanical, is_departure)
    model = ARMA(df, order=(2, 1)).fit(disp=False)
    forecasts = model.predict(len(df), len(df) + 6 * int(delta))  # because we fetch every 10min
    forecast = min(max_bikes, max(0, math.ceil(forecasts.tolist()[-1])))
    return forecast


def get_stationarity_penalty(station, is_departure: bool):
    target_column = 'num_bikes_available' if is_departure else 'num_docks_available'
    if (station[target_column] / station['capacity']) > 0.33:
        return 0
    station_status = pd.DataFrame(get_historical_data(station, 6 * 6))
    X = station_status[target_column].dropna().tolist()
    result = adfuller(X)
    p_value = result[1]
    return 15 if p_value < 0.05 else 0


def get_historical_data(station, last: int) -> pd.DataFrame:
    station_id = station["station_id"]
    return get_station_status(station_id)[-last:]


def get_forecast(station, delta_hours: int = 1, is_departure: bool = True):
    station_status = get_historical_data(station, 48 * 6)
    max_value = station_status[-1]["num_bikes_available"] + station_status[-1]["num_docks_available"]
    try:
        if is_departure:
            station["mechanical"] = predict_time_series(station_status, True, max_value, delta_hours, True)
            station["ebike"] = predict_time_series(station_status, False, max_value, delta_hours, True)
            station["num_bikes_available"] = station["mechanical"] + station["ebike"]
        else:
            station["num_docks_available"] = predict_time_series(station_status, False, max_value, delta_hours, True)
    except Exception as e:
        print(f"station {station['station_id']}: {e}")
    return station
