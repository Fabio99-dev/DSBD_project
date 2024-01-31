FROM mysql:latest

ENV MYSQL_ROOT_PASSWORD=toor
ENV MYSQL_DATABASE=SlaManagerDB


EXPOSE 6035

COPY ./SlaManagerDB_init.sql /docker-entrypoint-initdb.d/
