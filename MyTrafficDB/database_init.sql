use MyTrafficDB;

CREATE TABLE users(

    id integer primary key auto_increment,
    nome varchar(200) not null,
    email varchar(200) not null unique,
    password varchar(500) not null


);


INSERT INTO users (nome, email, password) values("Giovanni00", "giovannicasch@gmail.com", "15e2b0d3c33891ebb0f1ef609ec419420c20e320ce94c65fbc8c3312448eb225");
INSERT INTO users (nome, email, password) values("Fabio99", "fabio.castiglione99@outlook.com", "15e2b0d3c33891ebb0f1ef609ec419420c20e320ce94c65fbc8c3312448eb225");
