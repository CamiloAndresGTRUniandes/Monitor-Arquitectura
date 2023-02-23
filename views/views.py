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

#@bp.route('/process-message', methods=['POST'])
@bp.route('/suscriptor-peticion-ventas')
def process_message():
    connection = pika.BlockingConnection(pika.ConnectionParameters(rabbitmq_host))
    channel = connection.channel()

    channel.queue_declare(queue='peticion_ventas')

    def callback(ch, method, properties, body):
        # procesa el mensaje recibido aquí
        message = body
        print("Mensaje recibido: ", message)
        # Check status of microservices
        service = check_microservices()

        if service is not None:
            # Connect to RabbitMQ and send message to appropriate queue
            connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host, port=rabbitmq_port, credentials=pika.PlainCredentials(username=rabbitmq_username, password=rabbitmq_password)))
            channel = connection.channel()
            queue_name = f'{service}-consulta'
            channel.queue_declare(queue=queue_name)
            channel.basic_publish(exchange='', routing_key=queue_name, body=message)
            connection.close()

            print(f'Message sent to {service}-consulta')
        else:
            print('error: No available microservices to process message')

    channel.basic_consume(queue='peticion_ventas', on_message_callback=callback, auto_ack=True)

    print('Escuchando en la cola: peticion_ventas')
    channel.start_consuming()

    return 'Suscrito a la cola'
    
@bp.route('/suscriptor-respuesta-consulta')
def subscribe():
    connection = pika.BlockingConnection(pika.ConnectionParameters(rabbitmq_host))
    channel = connection.channel()

    channel.queue_declare(queue='respuesta_consulta')

    def callback(ch, method, properties, body):
        # procesa el mensaje recibido aquí
        message = body
        print("Mensaje recibido: ", message)
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host, port=rabbitmq_port, credentials=pika.PlainCredentials(username=rabbitmq_username, password=rabbitmq_password)))
        channel = connection.channel()
        queue_name = f'respuesta_ventas'
        channel.queue_declare(queue=queue_name)
        channel.basic_publish(exchange='', routing_key=queue_name, body=message)
        connection.close()
        print(f'Message sent to {queue_name}')

    channel.basic_consume(queue='respuesta_consulta', on_message_callback=callback, auto_ack=True)

    print('Escuchando en la cola: respuesta_consulta')
    channel.start_consuming()

    return 'Suscrito a la cola'
