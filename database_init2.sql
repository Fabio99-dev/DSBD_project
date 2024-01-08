use RoutesDB;

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
