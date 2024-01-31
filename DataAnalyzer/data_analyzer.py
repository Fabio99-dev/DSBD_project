import kafka
import logging, sys
from urllib.parse import quote
import requests
import concurrent.futures
import json
import psutil
import time as timeLibrary
import os

BING_API_KEY = os.environ.get("BING_API_KEY")
#Logger

logging.basicConfig(level=logging.DEBUG)
   
class Subscription():
      subscription_id = 0
      route_id = 0
      user_id = 0
      departureTime = ""
      notifyThreshold = 0
      advances = False
      

      def __init__(self, id ,route_id, user_id, departTime, notifyThreshold, advances):

        self.subscription_id = id    
        self.route_id = route_id
        self.user_id = user_id 
        self.departureTime = departTime
        self.notifyThreshold = notifyThreshold
        self.advances = advances

      def __str__(self):
        return (
            f"subscription_id: {self.subscription_id}, route_id: {self.route_id}, user_id: {self.user_id}, departureTime: {self.departureTime}, notifyThreshold: {self.notifyThreshold}, advances: {self.advances}\n"
        )
      
      def __repr__(self):
        return f"Subscription(subscription_id={self.subscription_id}. route_id={self.route_id}. user_id={self.user_id}. departureTime='{self.departureTime}'. notifyThreshold={self.notifyThreshold}. advances='{self.advances}')"


class Message:
   route_id = 0
   departureLatitude = 0,
   departureLongitude = 0,
   arrivalLatitude = 0,
   arrivalLongitude = 0,
   subscriptionsList = () #Lista di tuple aventi user_id, departTime, notifyThreshold, advances
   

   def __init__(self, route_id,departureLatitude, departureLongitude, arrivalLatitude, 
                arrivalLongitude, subscriptionsList):
      self.route_id = route_id
      self.departureLatitude = departureLatitude
      self.departureLongitude = departureLongitude
      self.arrivalLatitude = arrivalLatitude
      self.arrivalLongitude = arrivalLongitude
      self.subscriptionsList = subscriptionsList
      
   def __str__(self):

      return f"message(route_id={self.route_id}, departureLatitude={self.departureLatitude}, departureLongitude={self.departureLongitude}, arrivalLatitude={self.arrivalLatitude}, arrivalLongitude={self.arrivalLongitude}, subscriptionsList={self.subscriptionsList})"
   
   def __repr__(self):
      return self.__str__()

   '''
   Questa funzione converte una stringa di un messaggio kafka in un oggetto Message
   '''
   @classmethod
   def from_str(obj, input_string):
      
      mystring = input_string[8:]
      parts = mystring.split(", ")
      route_id = int(parts[0].split("=")[1])
      #logging.debug("Route_id:" + str(route_id))
      departureLatitude = parts[1].split("=")[1]
      #logging.debug("departureCity:" + str(departureCity))
      departureLongitude = parts[2].split("=")[1]
      #logging.debug("departureCAP:" + str(departureCAP))
      arrivalLatitude = parts[3].split("=")[1]
      #logging.debug("departureAddress:" + str(departureAddress))
      arrivalLongitude = parts[4].split("=")[1]
      subscriptionList = []
      for i in range(5,len(parts)):
          if i == 0:
            parts[i] = parts[i][19:]
          elif i == len(parts):
            parts[i] = parts[i][:len(parts[i]) - 2]    
          key_value_pairs = parts[i].split(". ")

          s = Subscription(int(key_value_pairs[0].split(": ")[1]),int(key_value_pairs[1].split(": ")[1]),
                          int(key_value_pairs[2].split(": ")[1]), key_value_pairs[3].split(": ")[1],int(key_value_pairs[4].split(": ")[1]),
                          bool(key_value_pairs[5].split(": ")[1]))
          subscriptionList.append(s)
            
             
      return Message(route_id, departureLatitude, departureLongitude, arrivalLatitude, arrivalLongitude, subscriptionList)
   
#Questa funzione ritorna a partire dalla lista delle sottoscrizioni tutti gli orari di partenza per quella tratta
def getDepartureTimes(subscriptionList):
   departureTimeList = []
   for item in subscriptionList:
      try:
        departureTimeList.index(item.departureTime,0)
      except ValueError as error:
         departureTimeList.append(item.departureTime)
   return departureTimeList

#Questa funzione ritorna i sottoscrittori per quel determinato orario per una determinata tratta
def get_subscribers_time(subscriptionList, departureTime):
   
   timed_subscribers = []

   for subscription in subscriptionList:
      
      if subscription.departureTime == departureTime:
         data = (subscription.notifyThreshold, subscription.advances, subscription.user_id)
         timed_subscribers.append(data)
   return timed_subscribers      

'''
Questa funzione si occupa di processare il messaggio kafka:
1. Effettua la query all'API esterna
2. Invia un messaggio kafka al notifier service in caso di verifica della condizione dell'alert
'''         
def handle_route(decodedMessage, departureTimes):

 producer = kafka.KafkaProducer(bootstrap_servers = ["kafka:9092"])
 
 for time in departureTimes:
    start_time = timeLibrary.time()
    endpoint = "http://dev.virtualearth.net/REST/V1/Routes?wp.0="+quote(decodedMessage.departureLatitude)+","+quote(decodedMessage.departureLongitude)+"&wp.1=" + quote(decodedMessage.arrivalLatitude) + "," +quote(decodedMessage.arrivalLongitude) +"&dateTime="+ quote(time) + "&key=" + BING_API_KEY 
    response = requests.get(endpoint)
    elapsed_time = timeLibrary.time() - start_time
    logging.debug("############# STO ESEGUENDO IL THREAD #############")  
    if response.status_code == 200:
      #Conversione del JSON in object Python
      decoded = json.dumps(response.json())
      object = json.loads(decoded)
      #Il travel time viene restituito in secondi, pertanto viene convertito in minuti
      travelTime = int(object["resourceSets"][0]["resources"][0]["travelDurationTraffic"]/60)
     # logging.debug("TRAVEL TIME: " + str(travelTime)) 
      standardTime = int(object["resourceSets"][0]["resources"][0]["travelDuration"]/60)
      #logging.debug("STANDARD TIME: " + str(standardTime)) 
      timed_subscribers = get_subscribers_time(decodedMessage.subscriptionsList, time)
      logging.debug("-******************** "  + str(timed_subscribers) + "***************************")
      alerts_to_send = []
      #logging.debug("--------------------------Reading the following message-------------------")  
      for subscribe in timed_subscribers:
         #logging.debug("--------------------------Inside the loop-------------------") 
         #logging.debug("FIRST OPERATION " + str(int(standardTime) + int(subscribe[0])))
         if int(standardTime) + int(subscribe[0]) > int(travelTime):
            #logging.debug("######## PASSED THE FIRST CHECK #######")
            delta = int(subscribe[0]) - int(travelTime)
            message = "La tratta da id: " + str(decodedMessage.route_id) + " ha un ritardo di " + str(delta) + " minuti\n"+"Orario di partenza: " + time
            entry = (subscribe[2], message)
            alerts_to_send.append(entry)
         #logging.debug("SECOND OPERATION " + str(int(standardTime) - int(subscribe[0])))
         elif subscribe[1] == True and abs((int(standardTime) - int(subscribe[0]))) < int(travelTime):
            #logging.debug("########### PASSED THE SECOND CHECK ###########")
            #Code to send a kafka message
            delta = int(travelTime) - int(subscribe[0]) 
            message = "La tratta da id: " + str(decodedMessage.route_id) + " ha un anticipo di " + str(delta) + " minuti\n"+"Orario di partenza: " + time
            entry = (subscribe[2], message)
            alerts_to_send.append(entry)
         #logging.debug("############ I'M INSIDE THE LOOP #################")
      #send the kafka message here
      logging.debug("#############RESULT###############")       
      logging.debug("RESULT: " + str(alerts_to_send))       
      producer.send("AlertMessage",bytes(str(alerts_to_send), 'utf-8'))  
      return elapsed_time
     # producer.close()     
            
           
    else:
      print(f"Errore {response.status_code}: {response.text}")    


'''
E' la funzione principale del microservizio. Resta in ascolto dei messaggi kafka e li elabora a seconda del tipo.
E' sottoscritto ai topic: MetricRequest e PingRoute.
'''
def kafka_consumer():
    
    consumer = kafka.KafkaConsumer(bootstrap_servers = ["kafka:9092"])
    if consumer.bootstrap_connected() == True:
    
        consumer.subscribe(['MetricRequest', 'PingRoute'])

        while True:
            elapsed_time = 0
            message = consumer.poll()
            if(message != None):
                for message in consumer:
                    
                    logging.debug("########## Reading the following message ################")
                    content = message.value.decode('utf-8')
                    logging.debug(content)
                    if content != "MetricRequest":  
                       logging.debug("Value: " + content)
                       decodedMessage = Message.from_str(content)
                     #logging.debug(decodedMessage)
                       departureTimes = getDepartureTimes(decodedMessage.subscriptionsList)
                       logging.debug("########## departure times ################")
                       logging.debug(departureTimes) 
                           #with concurrent.futures.ThreadPoolExecutor() as executor:
                           # executor.submit(handle_route, decodedMessage, departureTimes)
                       elapsed_time = handle_route(decodedMessage, departureTimes)
                    else:
                       producer = kafka.KafkaProducer(bootstrap_servers = ["kafka:9092"])
                       data = {
                        "container_name": "data_analyzer", 
                        "frequency": str(psutil.cpu_freq(False)[0]),
                        "load":  str(psutil.cpu_percent()),
                        "ram_usage": str(psutil.virtual_memory()[2]),
                        "elapsed_time": str(elapsed_time)
                        }
                       logging.debug("###############HO fatto il fetch delle metriche #########")
                       producer.send("MetricResponse",bytes(json.dumps(data), 'utf-8'))
                      
                       producer.close()  
                  

if __name__ == '__main__':
    kafka_consumer()