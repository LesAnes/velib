import matplotlib.pyplot as plt
import pandas as pd
from fbprophet import Prophet
from fbprophet.plot import add_changepoints_to_plot


def format_data(station_status, is_mechanical: bool = True) -> pd.DataFrame:
    station_status_df = pd.DataFrame(station_status)
    station_status_df['ds'] = pd.to_datetime(station_status_df['last_reported'], unit='s')
    station_status_df['y'] = station_status_df['mechanical'] if is_mechanical else station_status_df['ebike']
    return station_status_df


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
