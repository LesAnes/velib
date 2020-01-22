import plotly.express as px
import pandas as pd

df = pd.read_csv('./data/stations_status_concat/43004.csv')
df['last_reported'] = pd.to_datetime(df['last_reported'],unit='s')
fig = px.line(df, x="last_reported", y="mechanical")
fig.add_scatter(x=df["last_reported"], y=df["ebike"])
fig.show()