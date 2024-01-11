from flask import Flask, render_template, request, redirect, session
from flask_session import Session
from config import Config
from flask_sqlalchemy import SQLAlchemy
import os
import cryptography
import threading
from apscheduler.schedulers.background import BackgroundScheduler
import logging, sys
import kafka
import socket

#Mutex globale per l'accesso al db
mutex_db = threading.Lock()

#Logger
#logger = logging.Logger(level=logging.DEBUG, name="Vattela a pesca")
logging.basicConfig(level=logging.DEBUG)

class message:
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
   def __repr__(self):
      return self.__str__()
   
   @classmethod
   def from_str(obj, input_string):
      parts = input_string.split(", ")
      route_id = int(parts[0].split("=")[1])
      departureCity = parts[1].split("=")[1]
      departureCAP = parts[2].split("=")[1]
      departureAddress = parts[3].split("=")[1]
      arrivalCity = parts[4].split("=")[1]
      arrivalCAP = parts[5].split("=")[1]
      arrivalAddress = parts[6].split("=")[1]
      subscriptionList = parts[7].split("=[")
      subscriptionParts = subscriptionList[1].split(", ") #Ogni entry è una sottoscrizione. 
      for entry in subscriptionParts:
         """Subscription ID: 1
            Route ID: 1
            User ID: 1
            Departure Time: 00:09
            Notify Threshold: 30
            Advances: False"""
         newList = []
         entryParts = entry.split("\n")
         subscription = {}
         for entryPart in entryParts:
            keyValuePair = entryPart.split(": ")
            subscription[keyValuePair[0]]=keyValuePair[1]
         newList.append(subscription)

      return message(route_id, departureCity, departureCAP, departureAddress, arrivalCity, arrivalCAP, arrivalAddress, newList)      






def checkNullValues(data):
   
   for key, value in data.items():
      if value == "" and key != "advances":
         return False
      
      return True

def create_app(config = Config):

   #Il route handler è un producer kafka perchè invia messaggi al data_analyzer.
   producer = kafka.KafkaProducer(bootstrap_servers = ["kafka:9092"])

   if producer.bootstrap_connected != True:
      logging.debug("SONO UN COGLIONE PIRLA CHE NON E' IN GRADO DI CONNETTERSI")

   #Creazione del modulo flask
   app = Flask(__name__)

   app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URI")
   app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
   app.secret_key ="my_secret"
    #La durata di una sessione viene fissata a 15 minuti
   #Dopo aver recuperato dal file config le configurazioni del database, si ottiene l'istanza
   #del database SQL 

   app.logger.debug("Application started. By logger")
   db = SQLAlchemy(app)

   #Si definiscono quindi i modelli delle tabelle che compongo il db
   class ROUTES(db.Model):
     id = db.Column(db.Integer, primary_key=True, autoincrement=True)
     departureCity = db.Column(db.String(300), nullable=False)
     departureCAP = db.Column(db.String(10), nullable=False)
     departureAddress = db.Column(db.String(500), nullable=False)
     arrivalCity = db.Column(db.String(300), nullable=False)
     arrivalCAP = db.Column(db.String(10), nullable=False)
     arrivalAddress = db.Column(db.String(500), nullable=False)
     #departTime = db.Column(db.String(200), nullable = False)
     #notifyThreshold = db.Column(db.Integer, nullable = False)
     #advances = db.Column(db.Boolean, nullable = False)      

     def __init__(self, departureCity,departureCAP,departureAddress,arrivalCity,arrivalCAP,arrivalAddress):
                  #departTime, notifyThreshold, advances):
        self.departureCity = departureCity
        self.departureCAP = departureCAP
        self.departureAddress = departureAddress
        self.arrivalCity = arrivalCity
        self.arrivalCAP = arrivalCAP
        self.arrivalAddress = arrivalAddress

     
   def __str__(self):
        return (
            f"route_id: {self.id}, departureCity: {self.departureCity}, departureCAP: {self.departureCAP}, departureAddress: {self.departureAddress}, arrivalCity: {self.arrivalCity}, arrivalCAP: {self.arrivalCAP}, arrivalAddress: {self.arrivalAddress}\n"
        )
   
   def __repr__(self):
      return self.__str__()
        

   class SUBSCRIPTIONS(db.Model):
      id = db.Column(db.Integer, primary_key=True, autoincrement=True)
      route_id = db.Column(db.Integer, db.ForeignKey('routes.id'),  nullable = False)
      user_id = db.Column(db.Integer, nullable = False)
      departTime = db.Column(db.String(200), nullable=False)
      notifyThreshold = db.Column(db.Integer, nullable = False)
      advances = db.Column(db.Boolean, nullable = False)
      

      def __init__(self, route_id, user_id, departTime, notifyThreshold, advances):

        self.route_id = route_id
        self.user_id = user_id 
        self.departTime = departTime
        self.notifyThreshold = notifyThreshold
        self.advances = advances

      def __str__(self):
        return (
            f"subscription_id: {self.id}. route_id: {self.route_id}. user_id: {self.user_id}. departureTime: {self.departTime}. notifyThreshold: {self.notifyThreshold}. advances: {self.advances}"
        )
      
      def __repr__(self):
        return self.__str__()
  



   #Istanzio un thread che si occupa ad intervalli regolari di effettuare query al db
   scheduler = BackgroundScheduler()
   def queryDB(db,app):
      print("Il thread sta eseguendo.", file=sys.stdout, flush=True)
      app.logger.debug("Il thread sta eseguendo. By logger")
      with app.app_context(), mutex_db:
         routes = db.session.query(ROUTES).all()
         for route in routes:
            subscriptions = db.session.query(SUBSCRIPTIONS).filter(SUBSCRIPTIONS.route_id == route.id).all()
            msg = message(route.id, route.departureCity, route.departureCAP, 
                          route.departureAddress, route.arrivalCity, route.arrivalCAP,
                          route.arrivalAddress, subscriptions)
            logging.debug(subscriptions)
            #code to send the kafka message...
            producer.send("PingRoute", bytes(str(msg),'utf-8'))
            #-------

            app.logger.debug(msg.arrivalAddress)
            app.logger.debug(msg.arrivalCity)   
            app.logger.debug(msg.subscriptionsList)
            app.logger.debug(str(msg.subscriptionsList.count))
            for subscription in subscriptions:
               
               app.logger.debug(str(subscription.id) + " " + str(subscription.route_id) + " " + str(subscription.departTime))
               
            app.logger.debug("----------------------------------")

        
            




   scheduler.add_job(queryDB, 'interval', seconds= 5, args=[db, app])   
   scheduler.start()          


   @app.route("/testMS2")
   def testMS2():
      return render_template("errorpage.html")
   

   @app.route("/sendData", methods = ["POST"])
   def sendData():
      if request.method != "POST":
         return render_template("errorpage.html")
      else:
         
         data = {

            "departureCity": request.form.get("departureCity"),
            "departureCAP": request.form.get("departureCAP"),
            "departureAddress": request.form.get("departureAddress"),
            "arrivalCity": request.form.get("arrivalCity"),
            "arrivalCAP": request.form.get("arrivalCAP"),
            "arrivalAddress": request.form.get("arrivalAddress"),
            "departTime": request.form.get("departTime"),
            "notifyThreshold": request.form.get("notifyThreshold")
         }
         if request.form.get("advances") == "on":
            data["advances"] = 1
         else:
            data["advances"] = 0

         if checkNullValues(data) != True:
            session["ack"] = False
            return redirect("/privateArea")
         else:
            session["ack"] = True
            with mutex_db:
               """1. Ricerca del percorso se per caso è già presente nel database.
                     1a. Se NON È presente bisogna creare l'istanza
                     1b. Se è presente, recuperare l'id.
                  2. Creare l'oggetto sottoscrizione passando l'id dell'oggetto creato. """
               route = db.session.query(ROUTES).filter(ROUTES.departureCity == data["departureCity"] and 
                                                      ROUTES.departureCAP == data["departureCAP"] and
                                                      ROUTES.departureAddress == data["departureAddress"] and
                                                      ROUTES.arrivalCity == data["arrivalCity"] and
                                                      ROUTES.arrivalCAP == data["arrivalCAP"] and 
                                                      ROUTES.arrivalAddress == data["arrivalAddress"])
               if route.first() == None:
                  r =  ROUTES(data["departureCity"], data["departureCAP"], data["departureAddress"],
                                 data["arrivalCity"], data["arrivalCAP"],data["arrivalAddress"])
                  db.session.add(instance=r)
                  db.session.commit()
                  route_id = r.id
                  

               else:
                  route_id = route.first().id

               #Creazione dell'oggetto subscription
               subscription = SUBSCRIPTIONS(route_id, session["authorized"], data["departTime"],
                  data["notifyThreshold"], data["advances"])

               #Aggiunta della sottoscrizione al database
               db.session.add(instance=subscription)
               db.session.commit()   
            return redirect("/privateArea")
   return app

"""if data["advances"] == "on":
                r =  ROUTES(data["departureCity"], data["departureCAP"], 
                            data["departureAddress"], data["arrivalCity"], data["arrivalCAP"],
                            data["arrivalAddress"], data["departTime"], data["notifyThreshold"],
                            True)
            else:
               r =  ROUTES(data["departureCity"], data["departureCAP"], 
                            data["departureAddress"], data["arrivalCity"], data["arrivalCAP"],
                            data["arrivalAddress"], data["departTime"], data["notifyThreshold"],
                            False)
            mutex_db.acquire()   
            db.session.add(instance=r)
            db.session.commit()
            mutex_db.release()
            return redirect("/privateArea") """