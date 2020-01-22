import pandas as pd
import plotly.offline as py
from fbprophet import Prophet
from fbprophet.plot import plot_plotly

def read_data(station_id: int) -> pd.DataFrame:
    df = pd.read_csv(f'data/stations_status/{station_id}.csv')
    df['ds'] = pd.to_datetime(df['last_reported'], unit='s')
    df['y'] = df['mechanical']

def train_time_series(df: pd.DataFrame) -> Prophet:
    m = Prophet()
    m.fit(df)
    return m

def forecast_time_series(m: Prophet, n_hours: int) -> pd.DataFrame:
    future = m.make_future_dataframe(periods=n_hours, freq='H')
    return m.predict(future)


if __name__ == "__main__":
    station_id = 6512
    df = read_data(station_id)
    m = train_time_series(df)
    forecast = forecast_time_series(m, 6)
    print(forecast)

    # fig = plot_plotly(m, forecast)
    # py.plot(fig)
