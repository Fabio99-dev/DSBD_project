from flask import Flask, render_template, request, redirect, session
from flask_session import Session
from config import Config
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta
import os
import cryptography
import re
import hashlib

def checkNullValues(data):
   
   for key, value in data.items():
      if value == "" and key != "advances":
         return False
      
      return True  


def create_app(config = Config):

   #Creazione del modulo flask
   app = Flask(__name__)

   app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URI")
   app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
   app.secret_key ="my_secret"
    #La durata di una sessione viene fissata a 15 minuti
   #Dopo aver recuperato dal file config le configurazioni del database, si ottiene l'istanza
   #del database SQL 

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
     departTime = db.Column(db.String(200), nullable = False)
     notifyThreshold = db.Column(db.Integer, nullable = False)
     advances = db.Column(db.Boolean, nullable = False)      

     def __init__(self, departureCity,departureCAP,departureAddress,arrivalCity,arrivalCAP,arrivalAddress,
                  departTime, notifyThreshold, advances):
        self.departureCity = departureCity
        self.departureCAP = departureCAP
        self.departureAddress = departureAddress
        self.arrivalCity = arrivalCity
        self.arrivalCAP = arrivalCAP
        self.arrivalAddress = arrivalAddress
        self.departTime = departTime
        self.notifyThreshold = notifyThreshold
        self.advances = advances


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
            "notifyThreshold": request.form.get("notifyThreshold"),
            "advances": request.form.get("advances")
         }
         if checkNullValues(data) != True:
            session["ack"] = False
            return redirect("/privateArea")
         else:
            session["ack"] = True

            if data["advances"] == "on":
                r =  ROUTES(data["departureCity"], data["departureCAP"], 
                            data["departureAddress"], data["arrivalCity"], data["arrivalCAP"],
                            data["arrivalAddress"], data["departTime"], data["notifyThreshold"],
                            True)
            else:
               r =  ROUTES(data["departureCity"], data["departureCAP"], 
                            data["departureAddress"], data["arrivalCity"], data["arrivalCAP"],
                            data["arrivalAddress"], data["departTime"], data["notifyThreshold"],
                            False)
            db.session.add(instance=r)
            db.session.commit()
            return redirect("/privateArea") 
   
   return app