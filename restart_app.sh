#!/bin/bash

#Firstly shutdown the current instance of the application
docker-compose down

#Delete EVERYTHING
#docker system prune -a

#Then build a new image of the application

docker-compose build

#Start the new instance of the application

docker-compose up -d

#shows the process actually running 

docker ps --all
