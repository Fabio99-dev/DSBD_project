from flask import Flask, render_template, request, redirect, session
from flask_session import Session
from config import Config
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta
import os
import cryptography
import re
import hashlib
import threading
from apscheduler.schedulers.background import BackgroundScheduler
import logging, sys

#Mutex globale per l'accesso al db
mutex_db = threading.Lock()

#Logger
#logger = logging.Logger(level=logging.DEBUG, name="Vattela a pesca")
logging.basicConfig(level=logging.DEBUG)

def checkNullValues(data):
   
   for key, value in data.items():
      if value == "" and key != "advances":
         return False
      
      return True

def queryDB(db,app):
   print("Il thread sta eseguendo.", file=sys.stdout, flush=True)
   app.logger.debug("Il thread sta eseguendo. By logger")
   #db.session.query().all()


def create_app(config = Config):


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
        #self.departTime = departTime
        #self.notifyThreshold = notifyThreshold
        #self.advances = advances

   class SUBSCRIPTIONS(db.Model):
      id = db.Column(db.Integer, primary_key=True, autoincrement=True)
      route_id = db.Column(db.Integer, nullable = False)
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



   #Istanzio un thread che si occupa ad intervalli regolari di effettuare query al db
   scheduler = BackgroundScheduler()
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