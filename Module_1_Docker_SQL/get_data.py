import os
import pandas as pd
from tqdm.auto import tqdm
from sqlalchemy import create_engine

# Read a sample of the data
# prefix = 'https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/'
# df = pd.read_csv(prefix + 'yellow_tripdata_2021-01.csv.gz', nrows=100)

dtype = {
    "VendorID": "Int64",
    "passenger_count": "Int64",
    "trip_distance": "float64",
    "RatecodeID": "Int64",
    "store_and_fwd_flag": "string",
    "PULocationID": "Int64",
    "DOLocationID": "Int64",
    "payment_type": "Int64",
    "fare_amount": "float64",
    "extra": "float64",
    "mta_tax": "float64",
    "tip_amount": "float64",
    "tolls_amount": "float64",
    "improvement_surcharge": "float64",
    "total_amount": "float64",
    "congestion_surcharge": "float64"
}

parse_dates = [
    "tpep_pickup_datetime",
    "tpep_dropoff_datetime"
]

# Full read
# df = pd.read_csv(
#     '/workspace/yellow_tripdata_2021-01.csv.gz',
#     nrows=100,
#     dtype=dtype,
#     parse_dates=parse_dates
# )

# Chank mode
# df = pd.read_csv(
#     '/workspace/yellow_tripdata_2021-01.csv.gz',
#     dtype=dtype,
#     parse_dates=parse_dates,
#     iterator=True,
#     chunksize=100000
# )
df_green = pd.read_parquet(
    '/workspace/green_tripdata_2025-11.parquet')
print(df_green.info())

# Test chunks
# for df_chunk in df:
#     print(len(df_chunk))

# print(df.head())

engine = create_engine('postgresql://de_user:de_password@de_postgres_db:5432/ny_taxi')

# View all columns in df
# print(pd.io.sql.get_schema(df, name='yellow_taxi_data', con=engine))
print(pd.io.sql.get_schema(df_green, name='green_taxi_data', con=engine))

# Create table in DB
# df.head(n=0).to_sql(name='yellow_taxi_data', con=engine, if_exists='replace')
df_green.head(n=0).to_sql(name='green_taxi_data', con=engine, if_exists='replace')

first = True

# for df_chunk in df:
# # for df_chunk in tqdm(df):

#     if first:
#         # Create table schema (no data)
#         df_chunk.head(0).to_sql(
#             name="yellow_taxi_data",
#             con=engine,
#             if_exists="replace"
#         )
#         first = False
#         print("Table created")

#     # Insert chunk
#     df_chunk.to_sql(
#         name="yellow_taxi_data",
#         con=engine,
#         if_exists="append"
#     )

#     print("Inserted:", len(df_chunk))

# Green taxi
# Insert data
df_green.to_sql(
    name="green_taxi_data",
    con=engine,
    if_exists="append"
)

print("Inserted:", len(df_green))
