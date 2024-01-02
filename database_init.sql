use MyTrafficDB;

CREATE TABLE users(

    id integer primary key auto_increment,
    nome varchar(200) not null,
    email varchar(200) not null unique,
    password varchar(500) not null


);