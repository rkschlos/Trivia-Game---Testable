-- In here, you can create any extra users and databases
-- that you might need for all of your services

CREATE USER trivia_game_user WITH LOGIN PASSWORD 'secret';

CREATE DATABASE trivia_game_db WITH OWNER trivia_game_user;
