CREATE DATABASE israel_league CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;

USE israel_league;

CREATE TABLE players (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255),
    team_name VARCHAR(255),
    goals INT,
    assists INT,
    key_passes INT,
    accurate_passes INT,
    chances_created INT,
    sprints INT,
    xg FLOAT,
    dribble_success FLOAT,
    tackle_success FLOAT,
    aerial_duels_success FLOAT,
    round_number VARCHAR(10)
);