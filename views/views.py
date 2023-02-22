from flask import Blueprint, request, jsonify
import pika
import json

from models.models import check_microservices

bp = Blueprint('api', __name__)

# RabbitMQ connection details
rabbitmq_host = 'localhost'
rabbitmq_port = 5672
rabbitmq_username = 'guest'
rabbitmq_password = 'guest'

@bp.route('/process-message', methods=['POST'])
def process_message():
    # Get message from request body
    message = request.json

    # Check status of microservices
    service = check_microservices()

    if service is not None:
        # Connect to RabbitMQ and send message to appropriate queue
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host, port=rabbitmq_port, credentials=pika.PlainCredentials(username=rabbitmq_username, password=rabbitmq_password)))
        channel = connection.channel()
        queue_name = f'{service}-queue'
        channel.queue_declare(queue=queue_name)
        channel.basic_publish(exchange='', routing_key=queue_name, body=json.dumps(message))
        connection.close()

        return jsonify({'message': f'Message sent to {service}-queue'}), 200
    else:
        return jsonify({'error': 'No available microservices to process message'}), 404
