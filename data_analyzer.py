import kafka
import logging, sys

#Logger
#logger = logging.Logger(level=logging.DEBUG, name="Vattela a pesca")
logging.basicConfig(level=logging.DEBUG)

def kafka_consumer():
    
    consumer = kafka.KafkaConsumer(bootstrap_servers = ["kafka:9092"], consumer_timeout_ms=5000)
    if consumer.bootstrap_connected() == True:
    
        consumer.subscribe(['PingRoute'])

        while True:
            message = consumer.poll()
            if(message != None):
                for message in consumer:

                    logging.debug("Value: " + message.value.decode('utf-8'))         

if __name__ == '__main__':
    kafka_consumer()