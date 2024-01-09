#!/bin/bash

#clean containers and images

docker system prune -a

#remove all images

docker image prune -a

#clean the volumes

docker volume prune -a
