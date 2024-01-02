FROM mysql:latest

ENV MYSQL_ROOT_PASSWORD=toor
ENV MYSQL_DATABASE=MyTrafficDB

EXPOSE 6033

COPY ./database_init.sql /docker-entrypoint-initdb.d/
