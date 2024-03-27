from configparser import RawConfigParser
from io import BytesIO

from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobClient, BlobServiceClient
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import pyspark
from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("PySpark test Parquet").getOrCreate()

newDataDF = spark.read.parquet("hdfs://namenode:9000/pinotinput/testdata.parquet")
print(newDataDF.head())
