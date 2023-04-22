import pika
import psycopg2
import os

# credentials=pika.PlainCredentials(os.environ['RabbitMQ_username'],os.environ['RabbitMQ_password'])
credentials=pika.PlainCredentials("myuser","mypassword")

# connection = pika.BlockingConnection(pika.ConnectionParameters(host="rabbitmq",heartbeat=1000,port=5672,virtual_host="/", credentials=credentials))
connection = pika.BlockingConnection(pika.ConnectionParameters("172.23.0.1",credentials=credentials, port=5672))



channel = connection.channel()
if(connection.is_open):
    print('RabbitMQ connection Successful')

conn = psycopg2.connect(
    host=os.environ['Postgres_host'],
    user="postgres",
    database="student_db",
    password="password",
    port = 5432
)
if(conn.closed==0):
    print('Postgres connection Successful')

cur = conn.cursor()
def insert_into_database(message):
    try:
        name_, srn_, section_ = message.split(",")
        cur.execute("INSERT INTO students (name, srn, section) VALUES (%s, %s, %s)",
                       (name_, srn_, section_))
        conn.commit()
        print(f"Data inserted into database: {message}")
    except Exception as e:
        print(f"Error inserting into database: {e}")
        conn.rollback()
def callback(ch,method,properties,body):
    try:
        insert_into_database(body.decode())
        print("successfully inserted into the databse")
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        print(f"Error in decoding the message: {e}")
        ch.basic_reject(delivery_tag=method.delivery_tag, requeue=True)

channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue="insert_record", on_message_callback=callback)
print('Waiting for messages. To exit press CTRL+C')
channel.start_consuming()

