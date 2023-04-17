FROM python:3.9
WORKDIR /producer
COPY . /producer
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 5000
ENV RABBITMQ_HOST = rabbitmq
CMD ["python","producer.py"]
