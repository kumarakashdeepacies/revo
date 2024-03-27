from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json
from pyspark.sql.types import BooleanType, LongType, StringType, StructField, StructType

# Spark session & context
spark = (
    SparkSession.builder.master("local")
    .appName("studentcheck_query")
    # Add kafka package
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.2.1")
    .getOrCreate()
)

sc = spark.sparkContext

df = (
    spark.readStream.format("kafka")
    .option("kafka.bootstrap.servers", "broker:29092")  # kafka server
    .option("subscribe", "studentcheck.dbo.student")  # topic
    .option("startingOffsets", "earliest")  # start from beginning
    .load()
)

# Convert binary to string key and value
df1 = df.withColumn("key", df["key"].cast(StringType())).withColumn("value", df["value"].cast(StringType()))

from pyspark.sql.functions import from_json
from pyspark.sql.types import BooleanType, IntegerType, LongType, StructField, StructType

schema_data = StructType(
    [
        StructField("StudentID", IntegerType(), True),
        StructField("FirstName", StringType(), True),
        StructField("LastName", StringType(), True),
        StructField("Age", IntegerType(), True),
        StructField("ContactNo", IntegerType(), True),
    ]
)

df_data = (
    df1
    # Sets schema for event data
    .withColumn("value", from_json("value", schema_data))
)
print(df_data)
from pyspark.sql.functions import col, from_unixtime, to_date, to_timestamp

# Transform into tabular
# Convert unix timestamp to timestamp
# Create partition column (change_timestamp_date)
df_data_formatted = df_data.select(
    col("key").alias("event_key"),
    col("topic").alias("event_topic"),
    col("timestamp").alias("event_timestamp"),
    "value",
)

raw_path = "/opt/application/data_store"
checkpoint_path = "/opt/application/data_store/checkpoint"

queryStream = (
    df1.writeStream.format("parquet")
    .queryName("studentcheck_query")
    .option("checkpointLocation", checkpoint_path)
    .option("path", raw_path)
    .outputMode("append")
    .start()
)
