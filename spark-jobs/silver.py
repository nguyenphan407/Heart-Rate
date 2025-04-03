from pyspark.sql.functions import when, col, lag, unix_timestamp
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, TimestampType

from pyspark.sql import SparkSession
from pyspark.sql.window import Window

class Silver:
    def __init__(self):
        self.schema = StructType([
            StructField('customer_id', StringType()),
            StructField('heart_rate', IntegerType()),
            StructField('timestamp', TimestampType())
        ])

        self.spark = (SparkSession.builder
                        .appName("Silver")
                        .config("fs.s3a.access.key", "minio")
                        .config("fs.s3a.secret.key", "minio123")
                        .config("fs.s3a.endpoint", "http://host.docker.internal:9000")
                        .config("spark.hadoop.fs.s3a.path.style.access", "true")
                        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
                        .config("spark.delta.logStore.class", "org.apache.spark.sql.delta.storage.S3SingleDriverLogStore")
                        .getOrCreate()
                    )

    def read_bronze(self):
        df = self.spark.readStream \
                .format('json') \
                .schema(self.schema) \
                .option("staringOffsets", "latest") \
                .load("s3a://heart-rate/bronze/heart-rate-data/")

        return df

    def enrichment(self, df):
        # Add heart rate qualification
        df = df.withColumn("heart_rate_qualification",
                            when(col("heart_rate") <= 70, "Low")
                            .when((70 < col("heart_rate")) & (col("heart_rate") <= 110), "Medium")
                            .when(col("heart_rate") >110, "High"))

        return df

    def write(self, df):
        query = (
            df.writeStream
            .format("delta")
            .partitionBy("year", "month", "day")
            .option("checkpointLocation", "s3a://heart-rate/silver/silver-checkpoint")
            .outputMode("append")
            .start("s3a://heart-rate/silver/heart-rate-data/")
        )

        return query

    def process(self):
        df = self.read_bronze()
        df = self.enrichment(df)
        query = self.write(df)
        query.awaitTermination()

if __name__ == '__main__':
    silver = Silver()
    silver.process()