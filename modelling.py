import math

import pandas as pd
from statsmodels.tsa.arima_model import ARMA
from statsmodels.tsa.stattools import kpss, adfuller

from db import get_station_status


def format_ts_data(station_status, is_mechanical: bool = True, is_departure: bool = True) -> pd.DataFrame:
    station_status_df = pd.DataFrame(station_status)
    if is_departure:
        data = station_status_df['mechanical'].dropna().tolist() if is_mechanical else station_status_df[
            'ebike'].dropna().tolist()
    else:
        data = station_status_df['num_docks_available'].dropna().tolist()
    data = data[-300:]
    return pd.DataFrame(data)


def predict_time_series(station_status, is_mechanical: bool, max_bikes: int, delta: int,
                        is_departure: bool) -> int:
    df = format_ts_data(station_status, is_mechanical, is_departure)
    # print(adfuller(df))
    model = ARMA(df, order=(2, 1)).fit(disp=False)
    forecasts = model.predict(len(df), len(df) + 6 * int(delta)) # because we fetch every 10min
    forecast = min(max_bikes, max(0, math.ceil(forecasts.tolist()[-1])))
    return forecast


def get_forecast(station, delta_hours: int = 1, is_departure: bool = True):
    station_id = station["station_id"]
    station_status = get_station_status(station_id)
    max_value = station_status[0]["num_bikes_available"] + station_status[0]["num_docks_available"]
    if is_departure:
        station["mechanical"] = predict_time_series(station_status, True, max_value, delta_hours, True)
        station["ebike"] = predict_time_series(station_status, False, max_value, delta_hours, True)
    else:
        station["num_docks_available"] = predict_time_series(station_status, False, max_value, delta_hours, True)
    return station
