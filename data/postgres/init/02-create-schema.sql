\connect trivia_game_db

---
--- Create the tables in your database
---
CREATE TABLE categories (
    id SERIAL NOT NULL PRIMARY KEY,
    title VARCHAR(250) NOT NULL UNIQUE,
    canon BOOLEAN DEFAULT true
);

CREATE TABLE games (
    id SERIAL NOT NULL PRIMARY KEY,
    episode_id INTEGER NOT NULL,
    aired VARCHAR(10),
    canon BOOLEAN DEFAULT true
);

CREATE TABLE clues (
    id SERIAL NOT NULL PRIMARY KEY,
    row_index INTEGER NOT NULL,
    column_index INTEGER NOT NULL,
    answer TEXT NOT NULL,
    question TEXT NOT NULL,
    game_id INTEGER REFERENCES games(id) ON DELETE CASCADE,
    board_index INTEGER NOT NULL,
    value INTEGER NOT NULL,
    category_id INTEGER NOT NULL REFERENCES categories(id) ON DELETE CASCADE,
    invalid_count INTEGER DEFAULT 0,
    canon BOOLEAN DEFAULT true
);

CREATE TABLE game_definitions (
    id SERIAL NOT NULL PRIMARY KEY,
    created_on TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE TABLE game_definition_clues (
    game_definition_id INTEGER NOT NULL REFERENCES game_definitions(id) ON DELETE CASCADE,
    clue_id INTEGER NOT NULL REFERENCES clues(id) ON DELETE CASCADE
);

---
--- Change the owner from postgres superuser to the user for
--- the database
---
ALTER TABLE categories OWNER TO trivia_game_user;
ALTER TABLE games OWNER TO trivia_game_user;
ALTER TABLE clues OWNER TO trivia_game_user;
ALTER TABLE game_definitions OWNER TO trivia_game_user;
ALTER TABLE game_definition_clues OWNER TO trivia_game_user;
