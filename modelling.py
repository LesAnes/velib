from fbprophet import Prophet
from fbprophet.plot import plot_plotly
import pandas as pd
import plotly.offline as py

df = pd.read_csv('./data/stations_status/6497.csv')
df['ds'] = pd.to_datetime(df['last_reported'],unit='s')
df['y'] = df['mechanical']

m = Prophet()
m.fit(df)

future = m.make_future_dataframe(periods=1)
forecast = m.predict(future)

fig = plot_plotly(m, forecast)  # This returns a plotly Figure
py.plot(fig)