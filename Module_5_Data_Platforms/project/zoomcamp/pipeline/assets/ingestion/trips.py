"""@bruin

name: ingestion.trips
connection: duckdb-default

materialization:
  type: table
  strategy: append
image: python:3.11

columns:
  - name: pickup_datetime
    type: timestamp
    description: When the meter was engaged
  - name: dropoff_datetime
    type: timestamp
    description: When the meter was disengaged

@bruin"""


import os
import json
import pandas as pd
from datetime import datetime
from typing import List, Tuple
from dateutil.relativedelta import relativedelta


# # NYC Taxi TLC data endpoint
BASE_URL = "https://d37ci6vzurychx.cloudfront.net"

def generate_months_to_ingest(start_date: str, end_date: str) -> List[Tuple[int, int]]:
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    months = []
    while start <= end:
        months.append((start.year, start.month))
        start += relativedelta(months=1)
    return months


def build_parquet_url(taxi_type: str, year: int, month: int) -> str:
  return f"{BASE_URL}/trip-data/{taxi_type}_tripdata_{year}-{month:02d}.parquet"


def fetch_trip_data(taxi_type: str, year: int, month: int) -> pd.DataFrame:
    url = build_parquet_url(taxi_type, year, month)
    return pd.read_parquet(url)


def materialize():
    start_date = os.environ["BRUIN_START_DATE"]
    end_date = os.environ["BRUIN_END_DATE"]
    taxi_types = json.loads(os.environ["BRUIN_VARS"]).get("taxi_types", ["yellow"])

    # Generate list of months between start and end dates
    # Fetch parquet files from:
    # https://d37ci6vzurychx.cloudfront.net/trip-data/{taxi_type}_tripdata_{year}-{month}.parquet
    
    all_dfs = []
    months = generate_months_to_ingest(start_date, end_date)
    
    for taxi_type in taxi_types:
        for year, month in months:
            url = build_parquet_url(taxi_type, year, month)
            try:
                df = pd.read_parquet(url)
                all_dfs.append(df)
            except Exception as e:
                print(f"Failed to fetch {url}: {e}")

    return pd.concat(all_dfs, ignore_index=True) if all_dfs else pd.DataFrame()
