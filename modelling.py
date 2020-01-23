import matplotlib.pyplot as plt
import pandas as pd
from fbprophet import Prophet
from fbprophet.plot import add_changepoints_to_plot


def format_data(station_id: int, is_mechanical: bool = True) -> pd.DataFrame:
    df = pd.read_csv(f'data/stations_status/{station_id}.csv')
    df['ds'] = pd.to_datetime(df['last_reported'], unit='s')
    df['y'] = df['mechanical'] if is_mechanical else df['ebike']
    return df


def train_time_series(df: pd.DataFrame) -> Prophet:
    m = Prophet()
    m.fit(df)
    return m


def forecast_time_series(m: Prophet, n_hours: int) -> pd.DataFrame:
    future = m.make_future_dataframe(periods=n_hours, freq='H')
    return m.predict(future)


if __name__ == "__main__":
    station_id = 38522
    df = format_data(station_id)
    m = train_time_series(df)
    forecast = forecast_time_series(m, 6)

    fig = m.plot(forecast)
    a = add_changepoints_to_plot(fig.gca(), m, forecast)
    plt.plot()
    plt.savefig('fig.png')
