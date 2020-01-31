import json
from os import getenv
from pathlib import Path

import pandas as pd
import pymongo
from dotenv import load_dotenv

load_dotenv('.env')

myclient = pymongo.MongoClient(
    f"{getenv('MONGODB_URI')}/stations?ssl=true&replicaSet=Velibetter-shard-0&authSource=admin&retryWrites=true&w=majority")

db = myclient["stations"]

with open('data/station_information.json') as f:
    data = json.load(f)

db["station_information"].insert_many(data.get('data').get('stations'))
col = db["stations_status"]

concat = pd.DataFrame()
for p in Path('data/stations_status').glob('*.csv'):
    df = pd.read_csv(p)
    col.insert_many(json.loads(df.dropna().to_json(orient='records')))
