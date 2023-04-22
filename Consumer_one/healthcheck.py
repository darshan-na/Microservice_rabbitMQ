import pika
import os

# credentials=pika.PlainCredentials(os.environ['RabbitMQ_username'],os.environ['RabbitMQ_password'])
credentials=pika.PlainCredentials("myuser","mypassword")

# connection = pika.BlockingConnection(pika.ConnectionParameters(host="rabbitmq",heartbeat=1000,port=5672,virtual_host="/", credentials=credentials))
connection = pika.BlockingConnection(pika.ConnectionParameters("172.23.0.1",credentials=credentials, port=5672))



channel = connection.channel()

def callback(ch, method, properties, body):
    print(f"Received {body.decode()}")
    ch.basic_ack(delivery_tag=method.delivery_tag)
    print(f"message is achknowledges {method.delivery_tag}")

channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='health_check', on_message_callback=callback)

print('Waiting for messages. To exit press CTRL+C')
channel.start_consuming()

