use RoutesDB;

CREATE TABLE routes (

        id integer primary key auto_increment,
        departureCity varchar(300) not null,
        departureCAP varchar(10) not null,
        departureAddress varchar(500) not null,
        arrivalCity varchar(300) not null,
        arrivalCAP varchar(10) not null,
        arrivalAddress varchar(500) not null
);

CREATE TABLE subscriptions
(

    id       integer primary key auto_increment,
    route_id integer not null,
    user_id  integer not null,
    departTime varchar(200) not null,
    notifyThreshold integer not null,
    advances bool not null,
    FOREIGN KEY (route_id) REFERENCES routes (id)
);

INSERT INTO RoutesDB.routes (id, departureCity, departureCAP, departureAddress, arrivalCity, arrivalCAP, arrivalAddress) VALUES (1, 'Catania', '94125', 'Viale andrea doria 6', 'Raddusa', '95040', 'Via regina margherita 22');
INSERT INTO RoutesDB.routes (id, departureCity, departureCAP, departureAddress, arrivalCity, arrivalCAP, arrivalAddress) VALUES (2, 'Raddusa', '95040', 'Via Asilo Nido 4', 'Catania', '95125', 'Viale Andrea doria 6');

INSERT INTO RoutesDB.subscriptions (id, route_id, user_id, departTime, notifyThreshold, advances) VALUES (1, 1, 1, '00:09', 30, 0);
INSERT INTO RoutesDB.subscriptions (id, route_id, user_id, departTime, notifyThreshold, advances) VALUES (2, 2, 1, '09:00', 30, 0);
INSERT INTO RoutesDB.subscriptions (id, route_id, user_id, departTime, notifyThreshold, advances) VALUES (3, 1, 1, '09:00', 62, 0);
INSERT INTO RoutesDB.subscriptions (id, route_id, user_id, departTime, notifyThreshold, advances) VALUES (4, 1, 2, '00:00', 96, 1);