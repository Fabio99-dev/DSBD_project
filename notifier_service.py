import kafka
import logging, sys
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


logging.basicConfig(level=logging.DEBUG)

# Configura le informazioni dell'account email
email_address = "mymusic56124@gmail.com"
password = "pumi jyaw fika vudo"

# Configura il server SMTP
smtp_server = "smtp.gmail.com"
smtp_port = 587

consumer = kafka.KafkaConsumer(bootstrap_servers = ["kafka:9092"], consumer_timeout_ms=5000)
if consumer.bootstrap_connected() == True:

    consumer.subscribe(['AlertMessage'])
    while True:
     message = consumer.poll()
     if(message != None):
        for message in consumer:
            content = message.value.decode('utf-8')    
            logging.debug("--------------------------Reading the following message-------------------")    
            logging.debug("Value: " + content)