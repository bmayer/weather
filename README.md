# An Overly Complex Process to Collect Weather Stats
- collect weather stats every hour
- publish messages to RMQ
- consume messages and write to Influx
- Grafana for charts & graphs

## Consumer
```shell=
# Create Namespce
kubectl create ns weather

# RMQ Env Vars
kubectl create configmap rmq-env-vars --from-file=rmq-cm.yml -nweather

# Influx Env Vars
kubectl create configmap influxdb-env-vars --from-file=influxdb-cm.yml -nweather

# Python code as cm; volumeMount
kubectl create configmap rmq-consume-py --from-file=rmq-consume.py -nweather

# Deploy
kubectl apply -f rmq-consume-deploy.md
```

## Producer
```shell=
# Collect the Weather From These Areas; volumeMount
kubectl create configmap locations-json --from-file=locations.json -nweather

# Python code as cm; volumeMount
kubectl create configmap rmq-pub-py --from-file=rmq-pub.py -nweather

# Secret for access to weather.visualcrossing.com
#+ this will be replaced with Vault
kubectl create secret generic weather-env-vars --from-file=weather-secret.yml -nweather

# Cron
kubectl apply -f rmq-pub-cron.yml

```
