import pika
import json

from typing import Dict, Callable

import pika.adapters.blocking_connection
import pika.spec

def listen(callbacks: Dict[str, Callable[[Dict], None]]) -> None:
    """
    Subscribes to a RabbitMQ topic and sets up a callback for incoming messages.

    Args:
        callbacks (Dict[str, Callable[[Dict], None]]): A dictionary mapping topic names to callback functions.
    """

    def on_message(
        channel: pika.adapters.blocking_connection.BlockingChannel, 
        method_frame: pika.spec.Basic.Deliver, 
        _header_frame: pika.spec.BasicProperties, 
        body: bytes):
        message = json.loads(body.decode('utf-8'))
        print(f" [x] Received message: {message}")
        key = method_frame.routing_key
        if key in callbacks:
            callbacks[key](message)
        channel.basic_ack(delivery_tag=method_frame.delivery_tag)

    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    channel.exchange_declare(exchange="image_data", exchange_type='direct')

    # Declare the exchange for the topic
    result = channel.queue_declare(queue='', exclusive=True)
    queue_name = result.method.queue

    for topic in callbacks.keys():

        channel.queue_bind(exchange="image_data", queue=queue_name, routing_key=topic)

    channel.basic_consume(queue=queue_name, on_message_callback=on_message, auto_ack=False)
    print(f" [*] Waiting for messages in topics '{list(callbacks.keys())}'. To exit press CTRL+C")

    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print("Exiting...")
        channel.stop_consuming()
        connection.close()