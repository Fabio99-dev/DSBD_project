use RoutesDB;

CREATE TABLE routes (

        id integer primary key auto_increment,
        departureCity varchar(300) not null,
        departureCAP varchar(10) not null,
        departureAddress varchar(500) not null,
        arrivalCity varchar(300) not null,
        arrivalCAP varchar(10) not null,
        arrivalAddress varchar(500) not null,
        departureLatitude REAL not null,
        departureLongitude REAL not null,
        arrivalLatitude REAL not null,
        arrivalLongitude REAL not null
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

INSERT INTO RoutesDB.routes (id, departureCity, departureCAP, departureAddress, arrivalCity, arrivalCAP, arrivalAddress, departureLatitude, departureLongitude, arrivalLatitude, arrivalLongitude) VALUES (1, 'Raddusa', '95040', 'Via Asilo Nido 4', 'Catania', '94125', 'Viale Andrea doria 6', 37.47191014, 14.53208878, 37.5393552, 15.0649028);
INSERT INTO RoutesDB.routes (id, departureCity, departureCAP, departureAddress, arrivalCity, arrivalCAP, arrivalAddress, departureLatitude, departureLongitude, arrivalLatitude, arrivalLongitude) VALUES (2, 'Raddusa', '95040', 'Via Asilo Nido 4', 'Piazza Armerina', '94015', 'Via generale muscarÃ ', 37.47191014, 14.53208878, 37.38999385, 14.3714024);
INSERT INTO RoutesDB.routes (id, departureCity, departureCAP, departureAddress, arrivalCity, arrivalCAP, arrivalAddress, departureLatitude, departureLongitude, arrivalLatitude, arrivalLongitude) VALUES (3, 'Aidone', '94010', 'Piazza Generale Cultreri', 'Raddusa', '95040', 'Via regina margherita 22', 37.41539197, 14.44367694, 37.4727285, 14.5333521);
INSERT INTO RoutesDB.routes (id, departureCity, departureCAP, departureAddress, arrivalCity, arrivalCAP, arrivalAddress, departureLatitude, departureLongitude, arrivalLatitude, arrivalLongitude) VALUES (4, 'San Giuliano Milanese', '20098', 'Via Francesco Baracca 7', 'San Donato Milanese', '20097', 'Via Milano 4', 45.398481, 9.2827215, 45.4331139, 9.2659103);
INSERT INTO RoutesDB.subscriptions (id, route_id, user_id, departTime, notifyThreshold, advances) VALUES (1, 1, 2, '12:00', 70, 1);
INSERT INTO RoutesDB.subscriptions (id, route_id, user_id, departTime, notifyThreshold, advances) VALUES (2, 2, 2, '09:00', 55, 1);
INSERT INTO RoutesDB.subscriptions (id, route_id, user_id, departTime, notifyThreshold, advances) VALUES (3, 1, 1, '12:00', 65, 0);
INSERT INTO RoutesDB.subscriptions (id, route_id, user_id, departTime, notifyThreshold, advances) VALUES (4, 3, 2, '09:00', 60, 0);
INSERT INTO RoutesDB.subscriptions (id, route_id, user_id, departTime, notifyThreshold, advances) VALUES (5, 4, 2, '07:00', 33, 0);