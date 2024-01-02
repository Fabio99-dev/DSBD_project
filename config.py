#This file contains all enviroment variables useful for the module

import os

#mysql://root:toor@MyTrafficDB:6033/MyTrafficDB
class Config:
   SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI', default='mysql+pymysql://root:toor@MyTrafficDB:3306/MyTrafficDB')
  #SQLALCHEMY_DATABASE_PORT = os.environ.get('DATABASE_PORT', default=6033)
   #default='mysql+pymysql://root:toor@MyTrafficDB:6033/MyTrafficDB')
   SQLALCHEMY_TRACK_MODIFICATIONS  =False
 


