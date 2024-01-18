from flask import Flask, render_template, request, redirect, session
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from sqlalchemy.orm import aliased
from sqlalchemy import and_
import os
import cryptography
import threading
from apscheduler.schedulers.background import BackgroundScheduler
import logging, sys
import kafka
import socket
import json

#Mutex globale per l'accesso al db
mutex_db = threading.Lock()

#Logger
#logger = logging.Logger(level=logging.DEBUG, name="Vattela a pesca")
logging.basicConfig(level=logging.DEBUG)

class message:
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
   



def checkNullValues(data):
   
   for key, value in data.items():
      if value == "" and key != "advances":
         return False
      
      return True

def create_app():

   #Il route handler è un producer kafka perchè invia messaggi al data_analyzer.
   producer = kafka.KafkaProducer(bootstrap_servers = ["kafka:9092"])

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
     departureLatitude = db.Column(db.Numeric, nullable=False)
     departureLongitude = db.Column(db.Numeric, nullable=False)
     arrivalLatitude = db.Column(db.Numeric, nullable=False)
     arrivalLongitude = db.Column(db.Numeric, nullable=False)
     def __init__(self, departureCity,departureCAP,departureAddress,arrivalCity,arrivalCAP,arrivalAddress,
                  departureLatitude, departureLongitude, arrivalLatitude, arrivalLongitude):
        self.departureCity = departureCity
        self.departureCAP = departureCAP
        self.departureAddress = departureAddress
        self.arrivalCity = arrivalCity
        self.arrivalCAP = arrivalCAP
        self.arrivalAddress = arrivalAddress
        self.departureLatitude = departureLatitude
        self.departureLongitude = departureLongitude
        self.arrivalLatitude = arrivalLatitude
        self.arrivalLongitude = arrivalLongitude

     
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
  



  # @app.route("/queryDB", methods=["GET"])
   def queryDB(db, app):
      
      with app.app_context(),mutex_db:
         routes = db.session.query(ROUTES).all()
         for route in routes:
            subscriptions = db.session.query(SUBSCRIPTIONS).filter(SUBSCRIPTIONS.route_id == route.id).all()
            msg = message(route.id, route.departureLatitude, route.departureLongitude,
                          route.arrivalLatitude, route.arrivalLongitude, subscriptions)
            logging.debug(subscriptions)
            #code to send the kafka message...
            producer.send("PingRoute", bytes(str(msg),'utf-8'))
            logging.debug("######## Ho inviato il messaggio Kafka ###########")
            #-------

            """app.logger.debug(msg.arrivalAddress)
            app.logger.debug(msg.arrivalCity)   
            app.logger.debug(msg.subscriptionsList)
            app.logger.debug(str(msg.subscriptionsList.count))
            for subscription in subscriptions:
               
               app.logger.debug(str(subscription.id) + " " + str(subscription.route_id) + " " + str(subscription.departTime))
               
            app.logger.debug("----------------------------------")"""


  #NOTA BENE!!!! Il route handler NON deve eseguire in debug perchè altrimenti verranno creati due 
            #Thread!!       

  #Istanzio un thread che si occupa ad intervalli regolari di effettuare query al db       
   scheduler = BackgroundScheduler()
   scheduler.add_job(queryDB, 'interval', minutes=1, args=[db, app])   
   scheduler.start()

   @app.route("/debugScheduler")
   def debugScheduler():

      return "<p>" + str(scheduler.get_jobs()) + "</p>"

   @app.route("/getData/<user_id>", methods = ["GET"])
   def getData(user_id):
      with mutex_db:
         route_alias = aliased(ROUTES)
         subscription_alias = aliased(SUBSCRIPTIONS)
         query_result = (
            db.session.query(route_alias, subscription_alias)
            .join(subscription_alias, route_alias.id == subscription_alias.route_id)
            .filter(subscription_alias.user_id == user_id)
            .all()
         )
      routes = []        
      for route, subscription in query_result:
         entry = {

            "subscription_id": subscription.id,
            "route_id": route.id,     
            "departureCity": route.departureCity,
            "departureCAP": route.departureCAP,
            "departureAddress": route.departureAddress,
            "arrivalCity": route.arrivalCity,
            "arrivalCAP": route.arrivalCAP,
            "arrivalAddress": route.arrivalAddress,
            "departTime": subscription.departTime,
            "notifyThreshold": subscription.notifyThreshold,
            "advances": subscription.advances

         }
         routes.append(entry)

      return routes

   @app.route("/deleteAlert/<alertID>/<routeID>", methods = ["GET"])
   def deleteAlert(alertID, routeID):

      with mutex_db:
         #Si Elimina la sottoscrizione alla route per quell'utente   
         db.session.query(SUBSCRIPTIONS).filter_by(id=alertID).delete()
         #Si ricava poi il numero di sottoscrizioni per quella tratta
         subscriptionCount = db.session.query(func.count(func.distinct(SUBSCRIPTIONS.route_id))).\
          filter(SUBSCRIPTIONS.route_id == routeID).scalar()
         #Se è uguale a 0, allora si elmina anche la route dal db
         if(subscriptionCount == 0):
            db.session.query(ROUTES).filter_by(id=routeID).delete()
         db.session.commit()

         
      return redirect("/myAlerts")
   
   @app.route("/getSubscriptionData/<alertID>", methods = ["GET"])
   def getSubscriptionData(alertID):
      
      with mutex_db:
         route, subscription = db.session.query(ROUTES, SUBSCRIPTIONS).filter(SUBSCRIPTIONS.id == alertID).first()
   
      data = {

            "subscription_id": subscription.id,
            "route_id": route.id,     
            "departureCity": route.departureCity,
            "departureCAP": route.departureCAP,
            "departureAddress": route.departureAddress,
            "arrivalCity": route.arrivalCity,
            "arrivalCAP": route.arrivalCAP,
            "arrivalAddress": route.arrivalAddress,
            "departTime": subscription.departTime,
            "notifyThreshold": subscription.notifyThreshold,
            "advances": subscription.advances

         }
      return json.dumps(data)
   
   @app.route("/changeAlert", methods = ["POST"])
   def changeAlert():

      data = {

         "subscription_id": request.form.get("subscription_id"),
         "departTime": request.form.get("departTime"),
         "notifyThreshold":request.form.get("notifyThreshold")
      }

      if checkNullValues(data) != True:
         session["ack"] = False
         return redirect("/privateArea")

      with mutex_db:
         row = db.session.query(SUBSCRIPTIONS).filter(SUBSCRIPTIONS.id == data["subscription_id"]).first()

         row.departTime = request.form.get("departTime")
         row.notifyThreshold = request.form.get("notifyThreshold")
         if(request.form.get("advances") == "on"):
            row.advances = True
         else:
            row.advances = False
         db.session.commit()
         session["ack"] = True
         return redirect("/privateArea")

      


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
            "notifyThreshold": request.form.get("notifyThreshold"),
            "departureLatitude": request.form.get("departureLatitude"),
            "departureLongitude": request.form.get("departureLongitude"),
            "arrivalLatitude": request.form.get("arrivalLatitude"),
            "arrivalLongitude": request.form.get("arrivalLongitude")
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
               route = db.session.query(ROUTES).filter(
                           and_(
                              ROUTES.departureCity == data["departureCity"],
                              ROUTES.departureCAP == data["departureCAP"],
                              ROUTES.departureAddress == data["departureAddress"],
                              ROUTES.arrivalCity == data["arrivalCity"],
                              ROUTES.arrivalCAP == data["arrivalCAP"],
                              ROUTES.arrivalAddress == data["arrivalAddress"]
                           )
                        )
               if route.first() == None:
                  r =  ROUTES(data["departureCity"], data["departureCAP"], data["departureAddress"],
                                 data["arrivalCity"], data["arrivalCAP"],data["arrivalAddress"],data["departureLatitude"],
                                 data["departureLongitude"], data["arrivalLatitude"], data["arrivalLongitude"])
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
