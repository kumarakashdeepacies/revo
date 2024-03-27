from configparser import RawConfigParser
from io import BytesIO

from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobClient, BlobServiceClient
import pandas as pd
import pyarrow.parquet as pq
from pyspark import SparkConf, SparkContext, SQLContext

account_url = "https://revolutiouatdatastore.blob.core.windows.net/"
STORAGEACCOUNTKEY = "ztIN0J1z+QfNRP+YItGimdULuwqktL7rxS9lcORwD5KyhSQJlXBQ6Ffc6NQtGkfw0E84eM7qYnJHxgFZjngusw=="
STORAGEACCOUNTNAME = "revolutiouatdatastore"

creds = DefaultAzureCredential()
service_client = BlobServiceClient(account_url=account_url, credential=creds)

container_name = "datastoretesting"
blob_name = "testblob1"
blob_url = f"{account_url}/{container_name}/{blob_name}"

blob_service_client_instance = BlobServiceClient(account_url=account_url, credential=STORAGEACCOUNTKEY)
blob_client_instance = blob_service_client_instance.get_blob_client(container_name, blob_name, snapshot=None)

# Text file upload

with open("./datasets/azure-blob.txt", "rb") as blob_file:
    blob_client_instance.upload_blob(data=blob_file, overwrite=True)

# parquet file upload

# Read the configuration
config = RawConfigParser()
config.read("blob.conf")


def setup_spark(config):
    """Setup Spark to connect to Azure Blob Storage"""
    jars = [
        "spark-2.4.0-bin-hadoop2.7/jars/hadoop-azure-2.7.3.jar",
        "spark-2.4.0-bin-hadoop2.7/jars/azure-storage-6.1.0.jar",
    ]
    conf = (
        SparkConf()
        .setAppName("Spark Blob Test")
        .set("spark.driver.extraClassPath", ":".join(jars))
        .set("fs.azure", "org.apache.hadoop.fs.azure.NativeAzureFileSystem")
        .set(
            f"fs.azure.account.key.{config['blob-store']['blob_account_name']}.blob.core.windows.net",
            config["blob-store"]["blob_account_key"],
        )
    )
    sc = SparkContext(conf=conf).getOrCreate()

    return SQLContext(sc)


sql_context = setup_spark(config)

df = pd.DataFrame.from_dict(
    [
        ("Mario", "Red", "1570863600000"),
        ("Luigi", "Green", "1571036400000"),
        ("Princess", "Pink", "1572418800000"),
    ]
).rename(columns={0: "name", 1: "color", 2: "timestampInEpoch"})
print(df.head())


def write_pandas_dataframe_to_blob(blob_service, df, container_name, blob_name):
    """Write Pandas dataframe to blob storage"""
    buffer = BytesIO()
    df.to_parquet(buffer)
    blob_service.upload_blob(data=buffer.getvalue(), overwrite=True)
    # df.to_parquet(
    # storage_options={'account_name': account_name,


BLOB_NAME_parquet = "testdata.parquet"
blob_client_instance_parquet = blob_service_client_instance.get_blob_client(
    container_name, BLOB_NAME_parquet, snapshot=None
)
write_pandas_dataframe_to_blob(blob_client_instance_parquet, df, container_name, BLOB_NAME_parquet)
