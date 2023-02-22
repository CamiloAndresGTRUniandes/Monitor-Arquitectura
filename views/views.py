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
        queue_name = 'respuesta_ventas'#f'{service}-queue'
        channel.queue_declare(queue=queue_name)
        channel.basic_publish(exchange='', routing_key=queue_name, body=json.dumps(message))
        connection.close()

        return jsonify({'message': f'Message sent to {service}-queue'}), 200
    else:
        return jsonify({'error': 'No available microservices to process message'}), 404
    
@bp.route('/subscribe')
def subscribe():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    channel.queue_declare(queue='respuesta_ventas')

    def callback(ch, method, properties, body):
        # procesa el mensaje recibido aquí
        print("Mensaje recibido: ", body)

    channel.basic_consume(queue='respuesta_ventas', on_message_callback=callback, auto_ack=True)

    print('Escuchando en la cola: respuesta_ventas')
    channel.start_consuming()

    return 'Suscrito a la cola'
