import pika
import psycopg2
import pandas as pd
import os
value = os.environ.get('RabbitMQ_host')
value1 = os.environ.get('Postgres_host')
# credentials=pika.PlainCredentials(os.environ['RabbitMQ_username'],os.environ['RabbitMQ_password'])
credentials=pika.PlainCredentials("myuser","mypassword")

# connection = pika.BlockingConnection(pika.ConnectionParameters(host="rabbitmq",heartbeat=1000,port=5672,virtual_host="/", credentials=credentials))
connection = pika.BlockingConnection(pika.ConnectionParameters("172.23.0.1",credentials=credentials, port=5672))

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
def fetch_record(srn_):
    
    try:
        cur.execute(f"SELECT * from students")
        data = cur.fetchall()
        df = pd.DataFrame(data,columns=['name','srn','section'])        
        conn.commit()
        print('The records in the DataBase are :')
        print(df)
    except Exception as e:
        print(f'failed to fetch the data due to:  {e}')
        conn.rollback()
def callback(ch,method,properties,body):
    
    try:
        fetch_record(body.decode())
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        print(f'Message could not be decoded due to {e}')
        ch.basic_reject(delivery_tag=method.delivery_tag, requeue = True)

channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='read_database',on_message_callback=callback)
print("Wait for the incomming messages...")
channel.start_consuming()

