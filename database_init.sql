use MyTrafficDB;

CREATE TABLE users(

    id integer primary key auto_increment,
    nome varchar(200) not null,
    email varchar(200) not null unique,
    password varchar(500) not null


);

CREATE TABLE routes (

        id integer primary key auto_increment,
        departureCity varchar(300) not null,
        departureCAP varchar(10) not null,
        departureAddress varchar(500) not null,
        arrivalCity varchar(300) not null,
        arrivalCAP varchar(10) not null,
        arrivalAddress varchar(500) not null,
        departTime varchar(200) not null,
        notifyThreshold integer not null,
        advances bool not null


);

INSERT INTO users (nome, email, password) values("Fabio", "cas@gmail.com", "15e2b0d3c33891ebb0f1ef609ec419420c20e320ce94c65fbc8c3312448eb225")