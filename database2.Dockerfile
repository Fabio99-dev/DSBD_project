FROM mysql:latest

ENV MYSQL_ROOT_PASSWORD=toor
ENV MYSQL_DATABASE=RoutesDB
ENV MYSQL_USER=admin
ENV MYSQL_PASSWORD=root

EXPOSE 6034

COPY ./database_init2.sql /docker-entrypoint-initdb.d/

