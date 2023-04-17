from flask import Flask,request
import pika
import os
app = Flask(__name__)

connection = pika.BlockingConnection(pika.ConnectionParameters(host=os.environ['RabbitMQ_host'],heartbeat=1000))
channel = connection.channel();

channel.queue_declare(queue='health_check')
channel.queue_declare(queue='insert_record')
channel.queue_declare(queue='read_database')
channel.queue_declare(queue='delete_record')

channel.exchange_declare(exchange='my_exchange', exchange_type='direct')

channel.queue_bind(exchange='my_exchange', queue='health_check', routing_key='health_check')
channel.queue_bind(exchange='my_exchange', queue='insert_record', routing_key='insert_record')
channel.queue_bind(exchange='my_exchange', queue='read_database', routing_key='read_database')
channel.queue_bind(exchange='my_exchange', queue='delete_record', routing_key='delete_record')

@app.route('/')
def hello():
    if connection.is_open():
        return 'RabbitMQ connection established by the server'
    else:
        return 'Error in establishing the RabbitMQ conncetion'

@app.route('/health_check',methods=['GET'])
def health_check():
    message = request.args.get('message', 'RabbitMQ Connection Established')
    try:
        channel.basic_publish(exchange='my_exchange', routing_key='health_check', body=message)
        return 'Health Check message sent'
    except pika.exceptions.AMQPError as e:
        app.logger.error("Error occurred while publishing message to RabbitMQ: %s", str(e))
        return 'Could not send a health message'

@app.route('/insert_record', methods=['POST'])
def insert_record():
    name = request.form['name']
    srn = request.form['srn']
    section = request.form['section']
    message = f"{name},{srn},{section}"
    try:
        channel.basic_publish(exchange='my_exchange', routing_key='insert_record', body=message)
        return 'Record inserted'
    except pika.exceptions.AMQPError as e:
        app.logger.error("Error occurred while publishing message to RabbitMQ: %s", str(e))
        return 'Could not Insert record in the database'

@app.route('/read_database',methods=['GET'])
def read_database():
    try:
        channel.basic_publish(exchange='my_exchange', routing_key='read_database', body='Read All Records')
        return 'All records retrieved'
    except pika.exceptions.AMQPError as e:
        app.logger.error("Error occurred while publishing message to RabbitMQ: %s", str(e))
        return 'Could not fetch the records in the database'

@app.route('/delete_record',methods=['GET'])
def delete_record():
    srn = request.args.get('srn')
    try:
        channel.basic_publish(exchange='my_exchange', routing_key='delete_record', body=srn)
        return 'Record deleted'
    except pika.exceptions.AMQPError as e:
        app.logger.error("Error occurred while publishing message to RabbitMQ: %s", str(e))
        return 'Could not get the specified Record'

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')