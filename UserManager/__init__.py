from flask import Flask, render_template, request, redirect, session
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
import requests as http_request
from datetime import timedelta
from datetime import datetime
from urllib.parse import quote
import os, socket
import cryptography
import re
import hashlib
import logging
import psutil
import json



def create_app():

   #Creazione del modulo flask
   app = Flask(__name__)

   app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URI')
   app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
   app.permanent_session_lifetime = timedelta(minutes=30) 
   app.secret_key ="my_secret"
   
   #La durata di una sessione viene fissata a 30 minuti
   #Dopo aver recuperato dal file config le configurazioni del database, si ottiene l'istanza
   #del database SQL 

   db = SQLAlchemy(app)

   logging.basicConfig(level=logging.DEBUG)

   #Si definiscono quindi i modelli delle tabelle che compongo il db
   class USERS(db.Model):
     id = db.Column(db.Integer, primary_key=True, autoincrement=True)
     nome = db.Column(db.String(300), nullable=False, unique = True)
     email = db.Column(db.String(300), nullable=False, unique=True)
     password = db.Column(db.String(300), nullable=False, unique=True)

     def __init__(self, nome, email, password):
        self.nome = nome
        self.email = email
        self.password = password
   
   @app.route("/logout")
   def logout():
      session["authorized"] = None
      session["ack"] = None
      session["name"] = None
      return redirect("/login")
      
   @app.route("/login", methods=['POST', 'GET'])
   def login():
      session.permanent = False
      data = None
      if(request.method == 'GET'):  
       #  print(os.environ.get('DATABASE_URI'))
         return render_template("login.html", data=data)
      else:
         email = request.form["email"]
         password = request.form["password"]
         remember = request.form.get("remember")
         logging.debug("Value of " + str(remember))
         user = db.session.query(USERS).filter(USERS.email == email)
         if user.first() != None:
            if user.first().password == hashlib.sha256(password.encode('utf-8')).hexdigest():
               #redirect to the new page.
               if remember == "1":
                  session["authorized"] = user.first().id
                  session["name"] = user.first().nome
                  #session.permanent = True
                  session.permanent = False
                 # app.permanent_session_lifetime = timedelta(seconds=5)
               else:
                  session["authorized"] = user.first().id
                  session["name"] = user.first().nome
                  """session.permanent = False
                  app.permanent_session_lifetime = timedelta(minutes=15)"""
                  session.permanent = True
               return redirect(location="/privateArea")
            else:
               #error message. Password wrong
               data ="Login fallito. Password errata"
               return render_template("login.html", data = data)
         else:
            #error message. User not found
            data = "Login fallito. Email non trovata."
            return render_template("login.html", data = data)

    
   @app.route("/register", methods=['POST', 'GET'])
   def register():
      
      email_pattern = r"^\S+@\S+\.\S+$"
      data = None
       
      if(request.method == 'GET'):  
         return render_template("register.html", data = data)
      else:
         #se la richiesta è POST recupero i dati dal form e verifico se sono corretti.
         name = request.form["name"]
         email = request.form["email"]
         password = request.form["password"]

         if name.isspace() == True or len(name) < 3:
            data ="Nome non valido. Inserisci almeno tre caratteri"
            return render_template("register.html", data = data)
         if re.match(pattern=email_pattern, string=email) == None: 
            data ="L'indirizzo email non è valido. Riprova"
            return render_template("register.html", data = data)
         else:
            user = db.session.query(USERS).filter(USERS.email == email)
            if user.first() != None: #usiamo first() perchè la quey ha al massimo un risultato
               data ="L'email inserita è girà registrata al servizio"
               return render_template("register.html", data = data)
            else:
               pass

         if len(password) <8:
            data ="La password inserita è troppo debole. Inserisci almeno 8 caratteri"
            return render_template("register.html", data = data)


         #insert to database, chipering the password

         u = USERS(name, email,hashlib.sha256(password.encode('utf-8')).hexdigest()) 
         db.session.add(instance=u)      
         db.session.commit()
         data = False
         return render_template("register.html", data = data)

   @app.route("/editAlert/<alertID>", methods = ["GET"])
   def editAlert(alertID):
      
      if request.method == "GET":
         endpoint = "http://route_handler:3002/getSubscriptionData/"+quote(alertID)
         response = http_request.get(endpoint)
         if response.status_code == 200:
            decoded = json.dumps(response.json())
            data = json.loads(decoded)
            return render_template("privateArea2.html", data = data)
    
      
   
   @app.route("/privateArea", methods =["GET", "POST"])
   def privateArea():
      if request.method == "POST" or request.method == "GET":
         if session.get("authorized") != None:
          return render_template("privateArea2.html",data = None)     
         else:
            return redirect("login")   
      return render_template("errorpage.html")
   
   @app.route("/myAlerts", methods=["GET"])
   def myAlerts():
      return render_template("my_alerts.html")
   
   @app.route("/getEmail/<user_id>", methods = ["GET"])
   def getEmail(user_id):
      user = db.session.query(USERS).filter(USERS.id == user_id)
      if user.first() != None:
         return json.dumps({"status": "ok",
                 "user_id": user_id,
                 "email": user.first().email})
      else:
         return json.dumps({"status": "error",
                 "user_id": user_id,
                 "email": "email not found!"})
   
   @app.route("/get_metrics")
   def get_metrics():
      data = {

         "frequency": str(psutil.cpu_freq(False)[0]),
         "ram_usage": str(psutil.virtual_memory()[2]),
         "load":  str(psutil.cpu_percent())
      }
      return json.dumps(data)
     

     

   return app    

