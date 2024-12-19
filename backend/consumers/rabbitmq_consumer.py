import sys
import os
import pika
import json
from app.config.logging_config import frontend_logger
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def callback(ch, method, properties, body):
    """
    Callback function that gets called when a message is received from RabbitMQ.
    Logs the error message using the existing frontend_logger.
    """
    data = json.loads(body)
    message = data.get('message')
    client_info = data.get('client_info', {})

    # Log the error
    frontend_logger.error(f"Frontend error: {message}, Client info: {client_info}")

def start_consumer():
    """
    Start consuming messages from the RabbitMQ queue.
    This will continuously run and process messages as they come in.
    """
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))  # Adjust this if needed
    channel = connection.channel()
    channel.queue_declare(queue='frontend_errors', durable=True)

    # Consume messages from the 'frontend_errors' queue
    channel.basic_consume(queue='frontend_errors', on_message_callback=callback, auto_ack=True)

    print("Waiting for messages. To exit press CTRL+C")
    channel.start_consuming()

if __name__ == '__main__':
    start_consumer()
