#!/usr/bin/env python3

from influxdb import InfluxDBClient
from influxdb.exceptions import InfluxDBClientError, InfluxDBServerError
# import hvac
import json
import pika
import os
import sys

INFLUXDB_DB = os.environ['INFLUXDB_DB']
INFLUXDB_HOST = os.environ['INFLUXDB_HOST']
INFLUXDB_PORT = os.environ['INFLUXDB_PORT']
INFLUXDB_RP = os.environ['INFLUXDB_RP']
RABBIT_HOST  = os.environ['RABBIT_HOST']
RABBIT_QUEUE = os.environ['RABBIT_QUEUE']


def main():
  i_client = influx_client()
  rmq_consume(i_client)


# create influxdb client
def influx_client():
  i_client = InfluxDBClient(host='%s' % INFLUXDB_HOST, port='%s' % INFLUXDB_PORT)
  i_client.switch_database('%s' % INFLUXDB_DB)

  return i_client


def rmq_consume(*args):
  i_client = args[0]
  connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBIT_HOST))
  channel = connection.channel()

  channel.queue_declare(queue=RABBIT_QUEUE)

  def callback(ch, method, properties, body):
    print("- RMQ Received %r" % body)

    influx_payload = payload_builder(body)
    influxdb_writer(i_client, influx_payload)
    
  channel.basic_consume(queue=RABBIT_QUEUE, on_message_callback=callback, auto_ack=True)

  print('- Rabbit is ready. Waiting for messages. To exit press CTRL+C')
  channel.start_consuming()


def payload_builder(*args):
  b = args[0]
  influx_payload = []

  metrics = ['temp', 'humidity', 'pressure', 'windspeed', 'winddir', 'cloudcover', 'precip']
  for i in metrics:
    influx_payload.append(
      { "measurement": "weather",
        "tags": { "city": (json.loads(b))['city'] },
        "fields": { i: (json.loads(b))[i] }
      }
    )

  print(influx_payload)
  return influx_payload


def influxdb_writer(*args):

  # logger.debug('writing to influx')
  print('- writing to influx')

  i_client = args[0]
  influx_payload = args[1]

  try:
    i_client.write_points(influx_payload)
  except InfluxDBClientError as e:
    print(e)
    # logger.error(e)
  except InfluxDBServerError as e:
    print(e)
    # logger.error(e)


if __name__ == '__main__':
  try:
    main()
  except KeyboardInterrupt:
    print('Interrupted')
    try:
      sys.exit(0)
    except SystemExit:
      os._exit(0)
