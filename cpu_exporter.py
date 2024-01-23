from prometheus_client import start_http_server, Gauge, Counter
import time
import psutil
import requests
import json
import kafka
import logging

#Metriche da analizzare:
#1. CPU load: su tutti i microservizi
#2. Tempo di risposta dalle API su data_analyzer e User manager
#3. Tempo di query del database sul route_handler
#4. Numero di richieste di monitoraggio fallite 

logging.basicConfig(level=logging.INFO)

# Crea una metrica di tipo Gauge con etichette
cpu_frequency_metric = Gauge('container_cpu_frequency', 'Instant cpu frequency of the container', ['container_id'])
cpu_load_metric = Gauge('container_cpu_load', 'Average load of CPU consumed by the container',  ['container_id'])
#metric_test = Gauge('sample metric test', 'this is a substitution con cpu load metric', ["container_id"])

def get_route_handler_data():
   
    logging.info("3. Running the route_handler monitoring function")

    route_handeler_data = requests.get("http://route_handler:3002/route_handler_cpu_metrics")
    if route_handeler_data.status_code == 200:
        # Imposta il valore della metrica con etichette
         decoded = json.dumps(route_handeler_data.json())
         object = json.loads(decoded)
         cpu_frequency_metric.labels(container_id="route_handler").set(object["frequency"])
         cpu_load_metric.labels(container_id="route_handler").set(object["load"])    

 
   
if __name__ == '__main__':
    # Avvia un server HTTP per esporre le metriche
    start_http_server(8000)
    logging.info("1. Microservice started successfully! ")
    count = 0
    consumer = kafka.KafkaConsumer(bootstrap_servers = ["kafka:9092"], consumer_timeout_ms = 2000)
    consumer.subscribe(["MetricResponse"])
    producer = kafka.KafkaProducer(bootstrap_servers = ["kafka:9092"])
    
    while True:

        get_route_handler_data()
        producer.send("MetricRequest",bytes(str("MetricRequest"), 'utf-8'))
        producer.flush() 
        message = consumer.poll()
        if message != None:
            for message in consumer:
                content = message.value.decode('utf-8')
              #  logging.info(str(content))
                object = json.loads(content)
                cpu_freq = float(object["frequency"])
                cpu_freq = round(cpu_freq,2)
                cpu_frequency_metric.labels(container_id=object["container_name"]).set(str(cpu_freq))
                cpu_load_metric.labels(container_id=object["container_name"]).set(object["load"])
                logging.info(str(object))
        time.sleep(15)
        