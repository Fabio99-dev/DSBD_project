import kafka
import logging, sys

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
   departureCity = ''
   departureCAP = ''
   departureAddress = ''
   arrivalCity = ''
   arrivalCAP = ''
   arrivalAddress = ''
   subscriptionsList = () #Lista di tuple aventi user_id, departTime, notifyThreshold, advances
   """Obiettivo per il prossimo uservizio. La subscriptionsList contiene il departTime. 
   Implementare un algoritmo che mi permetta di prendere il depart time una volta sola per fare
   la query. 
   A risultato ottenuto bisogna fare la scan della subscription list e vedere quanti con
   quel depart time hanno violato la soglia. """

   def __init__(self, route_id,departureCity, departureCAP, departureAddress, 
                arrivalCity, arrivalCAP, arrivalAddress, subscriptionsList):
      self.route_id = route_id
      self.departureCity = departureCity
      self.departureCAP = departureCAP
      self.departureAddress = departureAddress
      self.arrivalCity = arrivalCity
      self.arrivalCAP = arrivalCAP
      self.arrivalAddress = arrivalAddress
      self.subscriptionsList = subscriptionsList


   def __str__(self):
      return f"message(route_id={self.route_id}, departureCity={self.departureCity}, departureCAP={self.departureCAP}, departureAddress={self.departureAddress}, arrivalCity={self.arrivalCity}, arrivalCAP={self.arrivalCAP}, arrivalAddress={self.arrivalAddress}, subscriptionsList={self.subscriptionsList})"
   
   @classmethod
   def from_str(obj, input_string):
      
      mystring = input_string[8:]
      parts = mystring.split(", ")
      route_id = int(parts[0].split("=")[1])
      #logging.debug("Route_id:" + str(route_id))
      departureCity = parts[1].split("=")[1]
      #logging.debug("departureCity:" + str(departureCity))
      departureCAP = parts[2].split("=")[1]
      #logging.debug("departureCAP:" + str(departureCAP))
      departureAddress = parts[3].split("=")[1]
      #logging.debug("departureAddress:" + str(departureAddress))
      arrivalCity = parts[4].split("=")[1]
      #logging.debug("arrivalCity:" + str(arrivalCity))
      arrivalCAP = parts[5].split("=")[1]
      #logging.debug("arrivalCAP:" + str(arrivalCAP))
      arrivalAddress = parts[6].split("=")[1]
      #logging.debug("arrivalAddress:" + str(arrivalAddress))
      subscriptionList = []
      for i in range(7,len(parts)):
          if i == 0:
            parts[i] = parts[i][19:]
          elif i == len(parts):
            parts[i] = parts[i][:len(parts[i]) - 2]    
          key_value_pairs = parts[i].split(". ")

          s = Subscription(int(key_value_pairs[0].split(": ")[1]),int(key_value_pairs[1].split(": ")[1]),
                          int(key_value_pairs[2].split(": ")[1]), key_value_pairs[3].split(": ")[1],int(key_value_pairs[4].split(": ")[1]),
                          bool(key_value_pairs[5].split(": ")[1]))
          subscriptionList.append(s)
            
             
      return Message(route_id, departureCity, departureCAP, departureAddress, arrivalCity, arrivalCAP, arrivalAddress, subscriptionsList=subscriptionList)
   
         

def get_class(class_name):
    return getattr(sys.modules[__name__], class_name)      

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
                    #logging.debug("Value: " + content)
                    decodedMessage = Message.from_str(content)
                    logging.debug(decodedMessage)   

if __name__ == '__main__':
    kafka_consumer()