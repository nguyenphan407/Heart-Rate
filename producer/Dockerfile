FROM python:3.9-slim

RUN apt-get update && apt-get install -y libpq-dev gcc

COPY . .

RUN pip install -r requirements.txt

CMD ["python", "heart_rate_producer.py"]