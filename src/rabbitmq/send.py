#!/usr/bin/env python
import json
import pika
import uuid

from typing import Dict, Callable



def publish_message_to_topic(exchange: str, topic: str, message: Dict[str, str]) -> None:
    """
    Publishes a message to a specified RabbitMQ topic.

    Args:
        topic (str): The topic to publish the message to.
        message (str): The message to publish.
    """
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    channel.exchange_declare(exchange=exchange, exchange_type='direct')

    channel.basic_publish(exchange=exchange, routing_key=topic, body=json.dumps(message))
    print(f" [x] Sent '{message}' to topic '{topic}'")
    connection.close()


class RpcClient(object):
    def __init__(self, callback: Callable[[Dict], None]):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='localhost'))

        self.channel = self.connection.channel()

        result = self.channel.queue_declare(queue='', exclusive=True)
        self.callback_queue = result.method.queue
        self.callback = callback

        self.channel.basic_consume(
            queue=self.callback_queue,
            on_message_callback=self.on_response,
            auto_ack=True)

        self.response = None
        self.corr_id = None

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.callback(json.loads(body))

    def call(self, exchange: str, topic: str, message: Dict[str, str]) -> None:
        """
        Calls the RPC service with the given message.
        """
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(
            exchange=exchange,
            routing_key=topic,
            properties=pika.BasicProperties(
                reply_to=self.callback_queue,
                correlation_id=self.corr_id,
            ),
            body=json.dumps(message))
    