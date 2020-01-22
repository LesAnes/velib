import pandas as pd
import plotly.offline as py
from fbprophet import Prophet
from fbprophet.plot import plot_plotly

df = pd.read_csv('./data/stations_status/6512.csv')
df['ds'] = pd.to_datetime(df['last_reported'], unit='s')
df['y'] = df['mechanical']

m = Prophet()
m.fit(df)

future = m.make_future_dataframe(periods=6, freq='H')
forecast = m.predict(future)
print(forecast)

# fig = plot_plotly(m, forecast)
# py.plot(fig)
