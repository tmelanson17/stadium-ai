#!/usr/bin/env python
import pika
import json

from typing import Dict

import pika.exchange_type


def publish_message_to_topic(topic: str, message: Dict[str, str]) -> None:
    """
    Publishes a message to a specified RabbitMQ topic.

    Args:
        topic (str): The topic to publish the message to.
        message (str): The message to publish.
    """
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    channel.exchange_declare(exchange="image_data", exchange_type='direct')

    channel.basic_publish(exchange="image_data", routing_key=topic, body=json.dumps(message))
    print(f" [x] Sent '{message}' to topic '{topic}'")
    connection.close()