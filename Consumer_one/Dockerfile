FROM python:3.9
WORKDIR /consumer_one
COPY . /consumer_one
RUN pip install --no-cache-dir -r requirements.txt
ENV RABBITMQ_HOST = rabbitmq-container
CMD ["python3","healthcheck.py"]
