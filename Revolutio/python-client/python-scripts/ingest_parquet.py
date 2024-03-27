from configparser import RawConfigParser
import datetime
from io import BytesIO
import os

from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobClient, BlobServiceClient
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import pyspark
from pyspark.sql import SparkSession

filename = "testdata"
current_datetime = datetime.datetime.now()
time = int(current_datetime.strftime("%Y%m%d%H%M%S"))
print(time)
df = pd.DataFrame.from_dict(
    [
        ("Mario", "White", f"{time}", "1"),
        ("Luigi", "Golden", f"{time}", "2"),
        ("Princess", "Pink", f"{time}", "3"),
        ("King", "White", f"{time}", "4"),
        ("Knight", "Purple", f"{time}", "5"),
        ("Queen", "Violet", f"{time}", "6"),
        ("Joker", "Golden", f"{time}", "7"),
    ]
).rename(columns={0: "name", 1: "color", 2: "timestampInEpoch", 3: "Sno"})
print(df.head())
table_from_pandas = pa.Table.from_pandas(df)
path = f"./datasets/{filename}"
if os.path.exists(path):
    pass
else:
    os.mkdir(f"./datasets/{filename}")
pq.write_table(table_from_pandas, f"./datasets/{filename}/{time}.parquet")
