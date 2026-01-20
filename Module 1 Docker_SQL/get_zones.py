import os
import pandas as pd
from sqlalchemy import create_engine

# Read a sample of the data
prefix = '/workspace/'
df = pd.read_csv(prefix + 'taxi_zone_lookup.csv')

# print(df.info())

engine = create_engine('postgresql://de_user:de_password@de_postgres_db:5432/ny_taxi')

# View all columns in df
print(pd.io.sql.get_schema(df, name='zones', con=engine))

# Create table in DB
df.head(n=0).to_sql(name='zones', con=engine, if_exists='replace')

# Load data
df.to_sql(name='zones', con=engine, if_exists='append')

print("Inserted:", len(df))