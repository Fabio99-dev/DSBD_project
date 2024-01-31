from flask import Flask, render_template, request, redirect, session
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from sqlalchemy.orm import aliased
from sqlalchemy import and_
import os
import threading
import cryptography
from apscheduler.schedulers.background import BackgroundScheduler
import logging, sys
import time
from prometheus_api_client import PrometheusConnect
from datetime import datetime, timedelta
import json
import pytz


class ServiceLevelObjective:

   nome=""
   unita_misura=""
   soglia_massima=100
   soglia_minima=0
   misurazione_attuale =0

   def __init__(self, nome, unita_misura, soglia_massima=100, soglia_minima=0):
      self.nome = nome
      self.soglia_massima = soglia_massima
      self.soglia_minima = soglia_minima
      self.unita_misura = unita_misura
      self.misurazione_attuale = 0

   def set_soglia_massima(self,soglia_massima):
      self.soglia_massima = soglia_massima   

   def set_soglia_minima(self,soglia_minima):
      self.soglia_minima = soglia_minima  

   def aggiorna_misurazione_attuale(self, nuova_misurazione):
      # Aggiorna la misurazione attuale.
      self.misurazione_attuale = nuova_misurazione

   def stato(self):

      #controllo su availability_rate
      if self.nome == "availability_rate":
         return  float(self.misurazione_attuale) >= float(self.soglia_minima)
      else:
         if float(self.misurazione_attuale) >= float(self.soglia_massima):
            return False
         elif float(self.misurazione_attuale) <= float(self.soglia_minima):
            return False
         else:
            return True

def __str__(self):
   return f"nome={self.nome}, sogliaMassima={self.soglia_massima}, sogliaMinima={self.soglia_minima}, unita_misura={self.unita_misura}, misurazione_attuale={self.misurazione_attuale}"

def __repr__(self):
   return self.__str__()


#Logger
logging.basicConfig(level=logging.DEBUG)


def create_app():

   #Creazione del modulo flask
   app = Flask(__name__)

   app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URI")
   app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
   app.secret_key ="my_secret"
   
 
   app.logger.debug("Application started. By logger")
   db = SQLAlchemy(app)

   # Recupera l'URL di Prometheus dall'ambiente
   prometheus_url = os.environ.get('PROMETHEUS_URL')
  
   # Connettiti a Prometheus
   prometheus = PrometheusConnect(url=prometheus_url)


   class SLAS(db.Model):
      id = db.Column(db.Integer, primary_key=True, autoincrement=True)
      metrica = db.Column(db.String, nullable=False, unique=True)
      soglia_minima = db.Column(db.Numeric, nullable=True)
      soglia_massima = db.Column(db.Numeric, nullable=True)
      unita_misura = db.Column(db.String, nullable=True)
      attivata = db.Column(db.Boolean, nullable = False)

      def __init__(self, metrica, soglia_minima, soglia_massima, unita_misura, attivata):
         self.metrica = metrica
         self.soglia_minima = soglia_minima
         self.soglia_massima = soglia_massima
         self.unita_misura = unita_misura
         self.attivata = attivata

 
   # Funzione per eseguire la query
   def count_entries_with_condition(slo, start_hour):
      
      if slo.nome == "availability_rate":
         prometheus_query = f"sum(sum_over_time(count({slo.nome} < {slo.soglia_minima} )[{start_hour}h:25s]))"
      else:   
         prometheus_query = f"sum(sum_over_time(count({slo.nome} < {slo.soglia_minima} or {slo.nome} > {slo.soglia_massima})[{start_hour}h:25s]))"
      
      prometheus_data = prometheus.custom_query(query=prometheus_query)
      logging.debug(str(prometheus_data))
      if prometheus_data == []:
         return 0
      else:
         return prometheus_data[0]["value"][1]

   def get_last_value(slo):

      with app.app_context():    
      # Query Prometheus per ottenere i dati 
       prometheus_query = f"{slo.nome}"
       prometheus_data = prometheus.custom_query(query=prometheus_query)
       for data_point in prometheus_data:
          slo.aggiorna_misurazione_attuale(float(data_point["value"][1]))

       return slo.misurazione_attuale
      

   def calcola_differenza_tempo(data):

      fuso_orario_italia = pytz.timezone('Europe/Rome')
      data_oggi = datetime.now(fuso_orario_italia)

      # Parsifica la data specificata nel formato "YYYY-MM-DDTHH:mm"
      data = datetime.strptime(data, "%Y-%m-%dT%H:%M")

      # Assicurati che entrambe le date abbiano lo stesso fuso orario
      data_oggi = data_oggi.replace(tzinfo=None)
      data = data.replace(tzinfo=None)
      
      # Calcola la differenza di tempo
      differenza_tempo = abs(data - data_oggi)

      # Accedi ai componenti della differenza
      giorni = differenza_tempo.days
      ore, remainder = divmod(differenza_tempo.seconds, 3600)
      minuti, secondi = divmod(remainder, 60)

      # Restituisci la differenza di tempo come una tupla

      # Viene impostato come tempo minimo 25s che è il tempo di scrape, in modo da avere dati aggiornati
      if giorni == 0 and ore == 0 and minuti == 0 and secondi < 25:
         secondi = 25

      return giorni,ore,minuti,secondi
 

   '''
   Questa route ritorna all'utente l'interfaccia per modifica l'SLA mostrando anche l'SLA corrente e lo stato
   di quest'ultimo
   '''
   @app.route("/setSLA", methods = ["GET"])
   def setSLA():
      
      results = db.session.query(SLAS).all()
      data = []

      for item in results:
         entry = {}   
         entry["nome_metrica"] = item.metrica
         entry["soglia_minima"] = item.soglia_minima
         entry["soglia_massima"] = item.soglia_massima
         entry["unita_misura"] = item.unita_misura
         entry["attivata"] = item.attivata
         if item.attivata == True:
            slo = ServiceLevelObjective(
            nome=item.metrica,
            unita_misura=item.unita_misura,
            soglia_massima=item.soglia_massima,
            soglia_minima=item.soglia_minima)
            entry["valore_attuale"] = get_last_value(slo)
            entry["violazioni_1h"] = count_entries_with_condition(slo, 1)
            entry["violazioni_3h"] = count_entries_with_condition(slo, 3)
            entry["violazioni_6h"] = count_entries_with_condition(slo, 6)
            entry["stato_slo"] = str(slo.stato())
         data.append(entry)
         
      return render_template("setSLA.html",data=data)


   '''
   Questa route gestisce l'invio del form di modifica dell'SLA.
   Salva nel database le modifiche richieste.
   '''

   @app.route('/sendSlaData', methods=['POST'])
   def sendSlaData():

      sla = []

      metrics = [

         ('cpu_load', 'sogliaMin_cpu_load', 'sogliaMax_cpu_load'),
         ('api_response_time', 'sogliaMin_api_response_time', 'sogliaMax_api_response_time'),
         ('query_db_time', 'sogliaMin_query_db_time', 'sogliaMax_query_db_time'),
         ('ram_load', 'sogliaMin_ram_load', 'sogliaMax_ram_load'),
         ('availability_rate', 'sogliaMin_availability_rate', 'sogliaMax_availability_rate')

      ]

      for item in metrics:

         if request.form.get(item[0]) == '1':
            if item[0] == 'cpu_load' or item[0] == 'ram_load' or item[0] == 'availability_rate':
               unita_misura = "%"
            else:
               unita_misura = "s"

            sla.append(ServiceLevelObjective(
               nome=item[0],
               unita_misura=unita_misura,
               soglia_massima=request.form.get(item[2]),
               soglia_minima=request.form.get(item[1])
            ))


      #Salvataggio nel database della SLA
      results = db.session.query(SLAS).all()

      for result in results:

         result.attivata = False
         for slo in sla:

            if result.metrica == slo.nome:
               result.soglia_minima = slo.soglia_minima
               result.soglia_massima = slo.soglia_massima
               result.attivata = True
            
      db.session.commit()
      return redirect("/setSLA")
   

   '''
   Questa route ritorna il numero di violazioni dell'SLA in un intervallo scelto dall'utente.
   '''

   @app.route('/customSearch', methods=['POST'])
   def customSearch():
      
      data = request.get_json()
      data_inizio = data["data_inizio"]
      data_fine = data["data_fine"]
 
      logging.debug("data_inizio: " + data_inizio)
      logging.debug("data_fine: " + data_fine)
    
      results = db.session.query(SLAS).filter(SLAS.attivata == True).all()
      prometheus_results = []
      
      diff_tempo_data_inizio = calcola_differenza_tempo(data_inizio)
      diff_tempo_data_fine = calcola_differenza_tempo(data_fine)

      logging.debug("diff inizio: " + str(diff_tempo_data_inizio))
      logging.debug("diff fine: " + str(diff_tempo_data_fine))

      for result in results:
      
         prometheus_query = f"sum(sum_over_time(count({result.metrica} < {result.soglia_minima} or {result.metrica} > {result.soglia_massima})[{diff_tempo_data_inizio[0]}d{diff_tempo_data_inizio[1]}h{diff_tempo_data_inizio[2]}m{diff_tempo_data_inizio[3]}s:25s]))" + " - " + f"sum(sum_over_time(count({result.metrica} < {result.soglia_minima} or {result.metrica} > {result.soglia_massima})[{diff_tempo_data_fine[0]}d{diff_tempo_data_fine[1]}h{diff_tempo_data_fine[2]}m{diff_tempo_data_fine[3]}s:25s]))"
         prometheus_data = prometheus.custom_query(query=prometheus_query)
         
         logging.debug(str(prometheus_data))
         if prometheus_data == []:
            prometheus_results.append({"nome": result.metrica, "violazioni": 0})
         else:
            prometheus_results.append({"nome": result.metrica, "violazioni": prometheus_data[0]["value"][1]})
         
      return json.dumps(prometheus_results)
   


   return app
