import kafka
import logging, sys
import requests
from urllib.parse import quote
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
import psutil
import os

logging.basicConfig(level=logging.DEBUG)

# Configura le informazioni dell'account email
email_address = os.environ.get("SENDER_EMAIL")
password = os.environ.get("EMAIL_PASSWORD")

# Configura il server SMTP
smtp_server = os.environ.get("SMTP_SERVER")
smtp_port = os.environ.get("SMTP_PORT")

class Message:
   user_id = 0
   message = ""

   def __init__(self, user_id, message):
      self.user_id = user_id
      self.message = message

   def __str__(self):
      return f"user_id: {self.user_id}\n message: {self.message}"
   
   def __repr__(self):
      return self.__str__()
         

def to_str(string):
    instances = []
    #First remove the first and the last character
    string = string[1:]
    string = string[:len(string) - 1]
    #logging.debug("#######1° step: "+string + " ##############")
    #Then split the various instances
    elements = string.split("), (")
    count = 0
    for element in elements:
        #logging.debug("#######2° step: "+element + " ##############")
        #Remove the first and last character
        if count == 0:
            element = element[1:]
        elif count == len(elements) -1 :
            logging.debug("BEFORE:" + str(element))
            element = element[:len(element)-2]
            logging.debug("AFTER:" + str(element))
        #logging.debug("#######3° step: "+element + " ##############")
        #Split the user_id by the message
        parts = element.split(", ")
        #logging.debug("#######4° step: "+ str(parts) + " ##############")
        m = Message(parts[0],parts[1])
        instances.append(m)
        count = count +1
    logging.debug(str(instances))
    return instances        





consumer = kafka.KafkaConsumer(bootstrap_servers = ["kafka:9092"], consumer_timeout_ms=5000)
producer = kafka.KafkaProducer(bootstrap_servers = ["kafka:9092"])
if consumer.bootstrap_connected() == True:

    consumer.subscribe(['MetricRequest', 'AlertMessage'])
    while True:
     message = consumer.poll()
     if(message != None):
        for message in consumer:
            content = message.value.decode('utf-8')    
            logging.debug("--------------------------Reading the following message-------------------")    
            logging.debug("Value: " + content)
            if content != "MetricRequest":        
               instances = to_str(str(content))
               logging.debug(instances)       
               for instance in instances:
                  #for each instance, we have to resolve the user_id finding out the associated email
                  endpoint = "http://user_manager:3001/getEmail/" + quote(instance.user_id)
                  result = requests.get(endpoint)
                  if result.status_code == 200:
                     #parse the response from json to a python object
                     decoded = json.dumps(result.json())
                     object = json.loads(decoded)
                     if object["status"] == "ok":
                        #send the email.
                        subject = "Alert MyTraffic"
                        body = instance.message + "\n" + "Grazie" + "\n" +"Il team di MyTraffic"
                        sender_email = email_address
                        receiver_email = object["email"]

                        message = MIMEMultipart()
                        message["From"] = sender_email
                        message["To"] = receiver_email
                        message["Subject"] = subject
                        message.attach(MIMEText(body, "plain"))

                        with smtplib.SMTP(smtp_server, smtp_port) as server:
                           
                           server.starttls()
                           server.login(email_address, password)
                           server.sendmail(sender_email, receiver_email, message.as_string())
                     else:
                        logging.debug("Email not found!")

            else:
                data = {
                     "container_name": "notifier_service", 
                     "frequency": str(psutil.cpu_freq(False)[0]),
                     "ram_usage": str(psutil.virtual_memory()[2]),
                     "load":  str(psutil.cpu_percent())
                     }
                logging.debug("############## HO fatto il fetch delle metriche #########")
                producer.send("MetricResponse",bytes(json.dumps(data), 'utf-8'))
                    
                     

                       
                 
               
