from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import StructType,StructField, StringType, IntegerType, TimestampType

class Bronze:
    def __init__(self):
        self.schema = StructType([
            StructField("customer_id", StringType(), False),
            StructField("heart_rate", IntegerType(), False),
            StructField("timestamp", TimestampType(), False)
        ])

        self.spark = (
                SparkSession.builder
                .appName("KafkaToBronze")
                .config("spark.jars", "/opt/bitnami/spark/jars/spark-sql-kafka-0-10_2.12-3.4.1.jar")
                .config("fs.s3a.access.key",  "minio")
                .config("fs.s3a.secret.key",  "minio123")
                .config("fs.s3a.endpoint", "http://host.docker.internal:9000")
                .config("spark.hadoop.fs.s3a.path.style.access", "true")
                .getOrCreate()
            )

    def read_from_kafka(self):
        df = (
            self.spark.readStream
            .format("kafka")
            .option("kafka.bootstrap.servers", "kafka:9092")
            .option("subscribe", "heart_rate")
            .option("startingOffsets", "latest")
            .load()
        )

        return df

    def validate_data(self, df):
        # Exchange col 'value' from binary to string
        df = df.selectExpr("CAST(value AS STRING) as json_str") \
                .filter("json_str IS NOT NULL")

        df = df.select(from_json(col("json_str"), self.schema).alias("data")).select("data.*")

        df = df.withColumn("year", year("timestamp")) \
                .withColumn("month", month("timestamp")) \
                .withColumn("day", dayofmonth("timestamp"))

        return df

    @staticmethod
    def write_to_minio(df):
        query = df \
            .writeStream \
            .format("json") \
            .partitionBy("year", "month", "day") \
            .option("checkpointLocation", "s3a://heart-rate/bronze/bronze-checkpoint") \
            .outputMode("append") \
            .start("s3a://heart-rate/bronze/heart-rate-data")

        return query

    def process(self):
        df = self.read_from_kafka()
        df = self.validate_data(df)
        query = self.write_to_minio(df)
        query.awaitTermination()

if __name__ == "__main__":
    bronze = Bronze()
    bronze.process()