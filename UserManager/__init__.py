from flask import Flask, render_template, request
from config import Config
from flask_sqlalchemy import SQLAlchemy
import mysql.connector
import os, socket
import cryptography

def get_host_ip():
    try:
        # Ottieni l'hostname della macchina
        host_name = socket.gethostname()
        # Ottieni l'indirizzo IP associato all'hostname
        host_ip = socket.gethostbyname(host_name)
        return host_ip
    except Exception as e:
        print(f"Errore durante il recupero dell'indirizzo IP: {str(e)}")
        return None

def create_app(config = Config):

   #Creazione del modulo flask
   app = Flask(__name__)

   app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URI')
   app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
   #Dopo aver recuperato dal file config le configurazioni del database, si ottiene l'istanza
   #del database SQL 

   db = SQLAlchemy(app)

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
      
   @app.route("/login", methods=['POST', 'GET'])
   def login():

      if(request.method == 'GET'):  
       #  print(os.environ.get('DATABASE_URI'))
         return render_template("login.html")
      else:
         pass 
    
   @app.route("/register", methods=['POST', 'GET'])
   def register():
       
      if(request.method == 'GET'):  
         return render_template("register.html")
      else:
         pass 

   """def test_db():
       
       config = {
          
        'user': 'root',
        'password': 'toor',
        'host': 'api.test.com',
        'port': '6033',
        'database': 'MyTrafficDB'

       } 
       connection = mysql.connector.connect(**config)
       cursor = connection.cursor(dictionary=True)
       cursor.execute('INSERT INTO USERS(nome,email,password) VALUES("Fabio","castiglionefabio80@gmail.com", "123456789")')
       cursor.close()
       connection.close()"""
      

   #FINALMENTE COSI' FUNZIONA
   #DA FARE: GESTIRE CHE ALLA TERMINAZIONE DEL CONTAINER IL DATABASE FA IL DUMP
   #E INDICARE CHE AL CARICAMENTO DEL CONTAINER CARICA IL DUMP PRECEDENTEMENTE FATTO
   #https://www.youtube.com/watch?v=WBqHr2kPc_A usare questa fonte
   @app.route("/myip")
   def myip():
      return get_host_ip()

   @app.route("/test")
   def test():
     # test_db()
     u = USERS("Fabio","castiglionefabio80@gmail.com", '123456789')
     db.session.add(instance=u)
     db.session.commit() 

     

   return app    

