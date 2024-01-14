import kafka
import logging, sys
from urllib.parse import quote
import requests
import threading

BING_API_KEY = "At71cbvTs-4zsbhV7M07ZYd41Y4FGK3PHvVOxTVZMz75lxwc1M-IQyZHypkgscJ6"

#Logger
#logger = logging.Logger(level=logging.DEBUG, name="Vattela a pesca")
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
   
   """Subscription(subscription_id=2. route_id=2. user_id=2. departureTime='09:00'. notifyThreshold=55. advances='True'"""
   
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
   

"""Obiettivo per il prossimo uservizio. La subscriptionsList contiene il departTime. 
   Implementare un algoritmo che mi permetta di prendere il depart time una volta sola per fare
   la query. 
   A risultato ottenuto bisogna fare la scan della subscription list e vedere quanti con
   quel depart time hanno violato la soglia.
    
     message(route_id=1, departureCity=Catania, departureCAP=94125, departureAddress=Viale andrea doria 6, arrivalCity=Raddusa, arrivalCAP=95040, arrivalAddress=Via regina margherita 22, 
     subscriptionsList=[Subscription(subscription_id=1. route_id=1. user_id=1. departureTime='00:09'. notifyThreshold=30. advances='True'), 
     Subscription(subscription_id=3. route_id=1. user_id=1. departureTime='09:00'. notifyThreshold=62. advances='True'), 
     Subscription(subscription_id=4. route_id=1. user_id=2. departureTime='00:00'. notifyThreshold=96. advances='True')]) """
def getDepartureTimes(subscriptionList):
   departureTimeList = []
   for item in subscriptionList:
      try:
        departureTimeList.index(item.departureTime,0)
      except ValueError as error:
         departureTimeList.append(item.departureTime)
   return departureTimeList

         
def handle_route(decodedMessage, departureTimes):
  for time in departureTimes:
    endpoint = "http://dev.virtualearth.net/REST/V1/Routes?wp.0="+quote(decodedMessage.departureLatitude)+","+quote(decodedMessage.departureLongitude)+"&wp.1=" + quote(decodedMessage.arrivalLatitude) + "," +quote(decodedMessage.arrivalLongitude) +"&dateTime="+ quote(time) + "&key=" + BING_API_KEY 
    response = requests.get(endpoint)

    if response.status_code == 200:
      data = response.json() 
      print(data)
    else:
      print(f"Errore {response.status_code}: {response.text}")    


def kafka_consumer():
    
    consumer = kafka.KafkaConsumer(bootstrap_servers = ["kafka:9092"], consumer_timeout_ms=5000)
    if consumer.bootstrap_connected() == True:
    
        consumer.subscribe(['PingRoute'])

        while True:
            logging.debug("-------------------------")
            message = consumer.poll()
            if(message != None):
                for message in consumer:
                    content = message.value.decode('utf-8')
                    logging.debug("--------------------------Reading the following message-------------------")    
                    logging.debug("Value: " + content)
                    decodedMessage = Message.from_str(content)
                    logging.debug(decodedMessage)
                    departureTimes = getDepartureTimes(decodedMessage.subscriptionsList)
                    #thread = threading.Thread(target=handle_route, args=(decodedMessage,departureTimes))
                    #handle_route(decodedMessage, departureTimes)
                    #1. Creo il thread.
                    #2. Mando il thread in esecuzione che elabora quella tratta 

if __name__ == '__main__':
    kafka_consumer()