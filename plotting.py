import pandas as pd
import plotly.express as px

from db import get_station_status
from modelling import format_data

if __name__ == '__main__':
    station_id = "6245"
    station_status = get_station_status(station_id)
    df = format_data(station_status)
    df['last_reported'] = pd.to_datetime(df['last_reported'], unit='s')
    fig = px.line(df, x="last_reported", y="mechanical")
    fig.add_scatter(x=df["last_reported"], y=df["ebike"])
    fig.show()
