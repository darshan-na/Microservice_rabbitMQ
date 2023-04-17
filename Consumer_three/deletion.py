import pika
import psycopg2
import os

connection = pika.BlockingConnection(pika.ConnectionParameters(host=os.environ['RabbitMQ_host'],heartbeat=1000))
if(connection.is_open):
    print("RabbitMQ connection established")
else:
    print("RabbitMQ connection Failed")
channel = connection.channel()

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
table_name = 'students'
def delete_record(srn_):
    
    try:
        cur.execute(f"DELETE from students where srn = '{srn_}'")
        conn.commit()
        print(f'Record with srn: {srn_} successfully deleted')
    except Exception as e:
        print(f'delete failed due to:  {e}')
        conn.rollback()
def callback(ch,method,properties,body):
    
    try:
        delete_record(body.decode())
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        print(f'Message could not be decoded due to {e}')
        ch.basic_reject(delivery_tag=method.delivery_tag, requeue = True)

channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='delete_record',on_message_callback=callback)
print("Wait for the incomming messages...")
channel.start_consuming()

