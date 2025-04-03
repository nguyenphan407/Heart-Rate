from pyspark.sql import SparkSession
from pyspark.sql.functions import col, lag, unix_timestamp
from pyspark.sql.window import Window
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, TimestampType

class Gold:
    def __init__(self):
        self.schema = StructType([
            StructField('customer_id', StringType()),
            StructField('heart_rate', IntegerType()),
            StructField('timestamp', TimestampType()),
            StructField('heart_rate_qualification', StringType())
        ])

        self.spark = (
            SparkSession.builder
            .appName("Gold")
            .config("fs.s3a.access.key", "minio")
            .config("fs.s3a.secret.key", "minio123")
            .config("fs.s3a.endpoint", "http://host.docker.internal:9000")
            .config("spark.hadoop.fs.s3a.path.style.access", "true")
            .config("spark.sql.catalog.clickhouse", "com.clickhouse.spark.ClickHouseCatalog")
            .config("spark.sql.catalog.clickhouse.host", "host.docker.internal")
            .config("spark.sql.catalog.clickhouse.protocol", "http")
            .config("spark.sql.catalog.clickhouse.http_port", "8123")
            .config("spark.sql.catalog.clickhouse.user", "user")
            .config("spark.sql.catalog.clickhouse.password", "password")
            .config("spark.sql.catalog.clickhouse.database", "default")
            .config("spark.clickhouse.write.format", "json")
            .getOrCreate()
        )

    def read_silver(self):
        df = (
            self.spark
            .readStream
            .format("parquet")
            .schema(self.schema)
            .option("staringOffsets", "latest")
            .load("s3a://heart-rate/silver/heart-rate-data/")
        )

        return df

    def df_aggregated(self, df):
        customer_df = self.spark.sql("select * from clickhouse.default.customer")
        df.join(customer_df, "customer_id", "left_outer")

        return df

    def write_to_ch(self, df, batch_id):
        df = df \
            .withWatermark("timestamp", "1 minutes") \
            .withColumn("prev_timestamp",
                        lag("timestamp").
                        over(Window.partitionBy("customer_id")
                             .orderBy("timestamp")
                             )) \
            .withColumn("timestamp_diff_minutes",
                        ((unix_timestamp(col("timestamp")) - unix_timestamp(col("prev_timestamp"))) / 60).cast(
                            "integer")) \
            .drop("prev_timestamp")

        df.writeTo("clickhouse.default.`heart-rate`").append()

    def write(self, df):
        query = (
            df.writeStream
            .foreachBatch(self.write_to_ch)
            .start()
        )

        return query

    def process(self):
        df = self.read_silver()
        df = self.df_aggregated(df)
        query = self.write(df)
        query.awaitTermination()

if __name__ == "__main__":
    gold = Gold()
    gold.process()