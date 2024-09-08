import pika
import json
from app.utils.logging_config import app_logger

def get_rabbitmq_channel():
    """
    Establish a RabbitMQ connection and return the channel.
    Ensure RabbitMQ is installed and running locally (or adjust connection settings).
    """
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))  # Adjust this for your setup
    channel = connection.channel()

    # Ensure the queue exists
    channel.queue_declare(queue='frontend_errors', durable=True)
    
    return channel

def send_to_rabbitmq(message, client_info):
    """
    Send a message to the RabbitMQ queue.
    The message is passed as a dictionary.
    """
    try:
        channel = get_rabbitmq_channel()

        # Prepare the message in JSON format
        body = json.dumps({
            'message': message,
            'client_info': client_info
        })

        # Publish the message to the 'frontend_errors' queue
        app_logger.info(f'\tsend_to_rabbitmq [body]: {body}')

        channel.basic_publish(
            exchange='',
            routing_key='frontend_errors',
            body=body
        )

        return True
    except Exception as e:
        print(f"Failed to send to RabbitMQ: {str(e)}")
        return False
