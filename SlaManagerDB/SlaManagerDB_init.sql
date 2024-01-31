CREATE DATABASE IF NOT EXISTS SlaManagerDB;
USE SlaManagerDB;

CREATE TABLE slas(

    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    metrica VARCHAR(300) NOT NULL UNIQUE,
    soglia_minima DOUBLE,
    soglia_massima DOUBLE,
    unita_misura VARCHAR(10) NOT NULL,
    attivata Boolean NOT NULL

);

INSERT INTO slas (metrica, soglia_minima, soglia_massima, unita_misura, attivata) VALUES('cpu_load', 0,0,'%', 0);
INSERT INTO slas (metrica, soglia_minima, soglia_massima, unita_misura, attivata) VALUES('ram_load', 0,0,'%', 0);
INSERT INTO slas (metrica, soglia_minima, soglia_massima, unita_misura, attivata) VALUES('api_response_time', 0,0,'s', 0);
INSERT INTO slas (metrica, soglia_minima, soglia_massima, unita_misura, attivata) VALUES('query_db_time', 0,0,'s', 0);
INSERT INTO slas (metrica, soglia_minima, soglia_massima, unita_misura, attivata) VALUES('availability_rate', 0,100,'%', 0);