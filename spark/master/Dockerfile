FROM bitnami/spark:3.4.1

LABEL maintainer="Gezim Sejdiu <g.sejdiu@gmail.com>, Giannis Mouchakis <gmouchakis@gmail.com>"

USER root
RUN install_packages curl
USER 1001

#COPY master.sh /

RUN curl -O https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/3.3.2/hadoop-aws-3.3.2.jar \
    && curl -O https://repo1.maven.org/maven2/com/amazonaws/aws-java-sdk-bundle/1.11.1026/aws-java-sdk-bundle-1.11.1026.jar \
    && curl -O https://repo1.maven.org/maven2/com/clickhouse/spark/clickhouse-spark-runtime-3.4_2.12/0.8.1/clickhouse-spark-runtime-3.4_2.12-0.8.1.jar \
    && curl -O https://repo1.maven.org/maven2/org/apache/spark/spark-sql-kafka-0-10_2.13/3.4.1/spark-sql-kafka-0-10_2.13-3.4.1.jar \
    && curl
    && mv hadoop-aws-3.3.2.jar /opt/bitnami/spark/jars/ \
    && mv aws-java-sdk-bundle-1.11.1026.jar /opt/bitnami/spark/jars/ \
    && mv clickhouse-spark-runtime-3.4_2.12-0.8.1.jar /opt/bitnami/spark/jars/ \
    && mv spark-sql-kafka-0-10_2.13-3.4.1.jar /opt/bitnami/spark/jars/

ENV SPARK_MASTER_PORT 7077
ENV SPARK_MASTER_WEBUI_PORT 8080
ENV SPARK_MASTER_LOG /spark/logs

EXPOSE 8080 7077 6066
