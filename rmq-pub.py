#!/usr/bin/env python3

from datetime import date, datetime
# import hvac
import json
import pika
import pytz
import os
import requests

RABBIT_HOST  = os.environ['RABBIT_HOST']
RABBIT_QUEUE = os.environ['RABBIT_QUEUE']
# VAULT_ADDR = 'http://10.0.0.236:8200'
# VAULT_ADDR = 'http://vault-full.vault-full.svc.cluster.local:8200'
# VAULT_AUTH = 'kubernetes'
# VAULT_MOUNT = "%s/" % (VAULT_AUTH)
# VAULT_ROLE = 'duckdns'
WEATHER_TOKEN = os.environ['WEATHER_TOKEN']
WEATHER_URL = os.environ['WEATHER_URL']


def main():
  # (date_now, hour_now) = get_time()
  # loc = get_locations()
  get_weather(get_locations())


def get_locations():
  with open('/weather/locations.json', 'r') as f:
    loc = json.load(f)

  return loc


def _get_time(*args):
  tz = args[0]
  date_now = datetime.now(pytz.timezone(tz)).date()
  hour_now = int(datetime.now(pytz.timezone(tz)).hour)

  return (date_now, hour_now)


def get_weather(*args):
  # print('{} - {}' .format(args[0], args[1]))
  loc = args[0]

  for i in range(len(loc)):
    zip_code = loc[i]['zip']
    (date_now, hour_now) = _get_time(loc[i]['tz'])

    r = requests.get('{}/{}/{}T{}:00:00?unitGroup=us&key={}' .format(WEATHER_URL, zip_code, date_now, hour_now, WEATHER_TOKEN))

    city = loc[i]['city']
    temp = r.json()['days'][0]['hours'][hour_now]['temp'] or 0.0
    humidity = r.json()['days'][0]['hours'][hour_now]['humidity'] or 0.0
    pressure = r.json()['days'][0]['hours'][hour_now]['pressure'] or 0.0
    windspeed = r.json()['days'][0]['hours'][hour_now]['windspeed'] or 0.0
    winddir = r.json()['days'][0]['hours'][hour_now]['winddir'] or 0.0
    cloudcover = r.json()['days'][0]['hours'][hour_now]['cloudcover'] or 0.0
    precip = r.json()['days'][0]['hours'][hour_now]['precip'] or 0.0

    w = {
      "city": city,
      "temp": temp,
      "humidity": humidity,
      "pressure": pressure,
      "windspeed": windspeed,
      "winddir": winddir,
      "cloudcover": cloudcover,
      "precip": precip
    }

    msg = json.dumps(w)
    print(msg)

    rmq_pub(msg)
  

def rmq_pub(*args):
  msg = args[0]

  connection = pika.BlockingConnection(pika.ConnectionParameters('{}' .format(RABBIT_HOST)))
  channel = connection.channel()
  channel.queue_declare(queue='{}' .format(RABBIT_QUEUE))
  channel.basic_publish(exchange='', routing_key=RABBIT_QUEUE, body=msg)

  connection.close()


# grab the jwt
# def read_jwt():
#   f = open('/var/run/secrets/kubernetes.io/serviceaccount/token')
#   jwt = f.read()
#   f.close()

#   return jwt

# # Authenticate to Vault/create vault client
# def vault_client(*args):
#   jwt = args[0]

#   v_client = hvac.Client(url=VAULT_ADDR)
#   v_client.auth_kubernetes(VAULT_ROLE, jwt, use_token=True, mount_point=VAULT_MOUNT)

#   if v_client.is_authenticated() == True:
#     print("I Am Authenticated To Vault")
#     return v_client
#   else:
#     print("Vault Authentication Failed")
#     exit

if __name__ == '__main__':
  main()
