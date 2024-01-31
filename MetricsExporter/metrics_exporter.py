from prometheus_client import start_http_server, Gauge, Counter
import time
import psutil
import requests
import json
import kafka
import logging
import docker
from datetime import datetime

#Metriche da analizzare:
#1. CPU load: su tutti i microservizi
#2. Tempo di risposta dalle API su data_analyzer e User manager
#3. Tempo di query del database sul route_handler

logging.basicConfig(level=logging.INFO)

#Statistiche dei container
docker_client = docker.DockerClient(base_url = ' unix:///var/run/docker.sock', version = 'auto')

user_manager = docker_client.containers.get("user_manager")
route_handler = docker_client.containers.get("route_handler")
data_analyzer = docker_client.containers.get("data_analyzer")
notifier_service = docker_client.containers.get("notifier_service")


# Crea una metrica di tipo Gauge con etichette
cpu_frequency_metric = Gauge('container_cpu_frequency', 'Instant cpu frequency of the container', ['container_id'])
cpu_load_metric = Gauge('cpu_load', 'Average load of CPU consumed by the container',  ['container_id'])
query_time = Gauge('query_db_time', 'Time spent for querying the RouteDB by the route handler', ["container_id"])
api_response_time = Gauge('api_response_time', 'response time of bing API', ["container_id"])
ram_usage = Gauge('ram_load', 'Average percentage of RAM memory usage', ["container_id"])
container_restart_count = Gauge('container_restart_count', 'Number of restart for a container', ["container_id"])
avalaiability_rate = Gauge('availability_rate', 'rate of availability of the container referred to the creation time', ["container_id"])

def get_docker_statistics():

    for container in docker_client.containers.list(all=True):
         started_at_datetime = datetime.strptime(str(container.attrs['State']['StartedAt'])[:-5],"%Y-%m-%dT%H:%M:%S.%f")
         started_at_timestamp = int(started_at_datetime.timestamp())
         created_at = datetime.strptime(str(route_handler.attrs['Created'])[:-5],"%Y-%m-%dT%H:%M:%S.%f")
         created_at_int = int(created_at.timestamp())
         avalaiability_rate.labels(container_id = container.name).set(int( float(started_at_timestamp) / float(created_at_int) *100))
         container_restart_count.labels(container_id = container.name).set(container.attrs['RestartCount'])

        

def get_route_handler_data():
   
    logging.info("3. Running the route_handler monitoring function")

    route_handeler_data = requests.get("http://route_handler:3002/route_handler_cpu_metrics")
    if route_handeler_data.status_code == 200:
        # Imposta il valore della metrica con etichette
         decoded = json.dumps(route_handeler_data.json())
         object = json.loads(decoded)
         #CPU FREQUENCY METRIC
         cpu_frequency_metric.labels(container_id="route_handler").set(object["frequency"])
         #CPU LOAD METRIC
         cpu_load_metric.labels(container_id="route_handler").set(object["load"])
         #RAM LOAD METRIC
         ram_usage.labels(container_id = "route_handler").set(object["ram_usage"])
         #QUERY TIME
         query_time.labels(container_id = "route_handler").set(str(object["query_time"]))
        
         #logging.info(int( float(started_at_timestamp) / float(created_at_int) *100))
def get_user_manager_data():

    route_handeler_data = requests.get("http://user_manager:3001/get_metrics")
    if route_handeler_data.status_code == 200:
        # Imposta il valore della metrica con etichette
         decoded = json.dumps(route_handeler_data.json())
         object = json.loads(decoded)
         cpu_frequency_metric.labels(container_id="user_manager").set(object["frequency"])
         cpu_load_metric.labels(container_id="user_manager").set(object["load"])    
         ram_usage.labels(container_id = "user_manager").set(object["ram_usage"])
         started_at_datetime = datetime.strptime(str(user_manager.attrs['State']['StartedAt'])[:-5],"%Y-%m-%dT%H:%M:%S.%f")
         started_at_timestamp = int(started_at_datetime.timestamp())
         created_at = datetime.strptime(str(user_manager.attrs['Created'])[:-5],"%Y-%m-%dT%H:%M:%S.%f")
         created_at_int = int(created_at.timestamp())
         avalaiability_rate.labels(container_id = "user_manager").set(int( float(started_at_timestamp) / float(created_at_int) *100))

 
   
if __name__ == '__main__':
    # Avvia un server HTTP per esporre le metriche
    start_http_server(8000)
    logging.info("1. Microservice started successfully! ")
    count = 0
    consumer = kafka.KafkaConsumer(bootstrap_servers = ["kafka:9092"], consumer_timeout_ms = 2000)
    consumer.subscribe(["MetricResponse"])
    producer = kafka.KafkaProducer(bootstrap_servers = ["kafka:9092"])
    
    while True:

        get_user_manager_data()

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
                ram_usage.labels(container_id = object["container_name"]).set(object["ram_usage"])
                if 'elapsed_time' in object:
                    api_response_time.labels(container_id="data_analyzer").set(object['elapsed_time'])

                logging.info(str(object))

                get_docker_statistics()
               
        time.sleep(15)
        