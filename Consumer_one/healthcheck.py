import pika
import os

connection = pika.BlockingConnection(pika.ConnectionParameters(host=os.environ['RabbitMQ_host'],heartbeat=1000))
channel = connection.channel()

def callback(ch, method, properties, body):
    print(f"Received {body.decode()}")
    ch.basic_ack(delivery_tag=method.delivery_tag)
    print(f"message is achknowledges {method.delivery_tag}")

channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='health_check', on_message_callback=callback)

print('Waiting for messages. To exit press CTRL+C')
channel.start_consuming()