FROM mysql:latest

ENV MYSQL_ROOT_PASSWORD=toor
ENV MYSQL_DATABASE=RoutesDB

EXPOSE 6034

COPY ./database_init2.sql /docker-entrypoint-initdb.d/

