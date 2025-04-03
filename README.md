# Real-Time Heart-Rate Streaming and Analysis
## Introduction
This application streams and analyzes heart-rate data in real time for the healthcare industry.
## Stack
* **Data Ingestion: Apache Kafka**

* **Data Storage**:

  * **MinIO**

  * **ClickHouse**

* **Data Processing: Apache Spark (Structured Streaming)**

* **Visualization Tools: Superset**
* **Docker & Docker-Compose**


## Architecture Overview (Medallion Architecture)
<img width="1092" alt="Ảnh màn hình 2025-04-03 lúc 13 30 49" src="https://github.com/user-attachments/assets/5d014533-070a-4f3f-9570-af549c29a3e9" />


## Set up
1. Navigate to the root directory of project and run this command: 
  ``` bash
    docker-compose up
  ```
  Now, the heart-rate container is appear in your docker destop
<img width="1102" alt="Ảnh màn hình 2025-04-03 lúc 15 00 20" src="https://github.com/user-attachments/assets/714c326d-237b-4df3-9b84-e8e9c7e7ef9f" />

2. Enter the spark-master container by executing:
  ```bash
    docker exec -it spark-master /bin/bash
  ``` 
  Then, run the following command to start spark jobs:
  ```bash
    spark-submit /opt/jobs/bronze.py &
    spark-submit /opt/jobs/silver.py &
    spark-submit /opt/jobs/gold.py &
  ``` 
3. Once the jobs are running, you can monitor Spark Streaming on localhost:4040 (make sure the producer container is running to generate sample data).
<img width="1440" alt="Ảnh màn hình 2025-04-03 lúc 15 13 42" src="https://github.com/user-attachments/assets/c84f90df-050b-402f-ad5f-bcae83a915cb" />
4. Finally, create a dashboard in Superset (accessible on port 8088) to visualize the results. Superset supports real-time data, so your dashboard will update automatically.
<img width="1180" alt="Ảnh màn hình 2025-04-03 lúc 14 54 05" src="https://github.com/user-attachments/assets/370c987a-d15f-420f-8c29-32043951223c" />
