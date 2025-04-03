from kafka import KafkaProducer
import json
import time
import random
from minio import Minio
import structlog

log = structlog.get_logger()

producer = KafkaProducer(
    bootstrap_servers='kafka:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def _get_minio_client():
    return Minio(
        endpoint='minio:9000',
        access_key='minio',
        secret_key='minio123',
        secure=False
    )

# def _get_customer():
#     client = _get_minio_client()
#     response = client.get_object('customer', 'customer.csv')
#     json_data = json.loads(response.read().decode('utf-8'))
#
#     return json_data

def generate_heart_rate_data(customer_id):
    return {
        "customer_id": customer_id,
        "heart_rate": random.randint(50, 150),
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
    }

def produce_heart_rate():
    log.info('Producing heart rate')
    customer_ids = ["12345", "67890", "54321"]
    while True:
        for customer_id in customer_ids:
            data = generate_heart_rate_data(customer_id)
            producer.send('heart_rate', value=data)
            log.info(f"Sent: {data}")
            time.sleep(5)

if __name__ == "__main__" :
    produce_heart_rate()