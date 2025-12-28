-- This line added by reccomendation from chatgpt 
PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS chat_log;
DROP TABLE IF EXISTS user_notes;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
);

-- This table written with chatgpt assisatance
CREATE TABLE chat_log (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    message TEXT NOT NULL,
    role TEXT CHECK(role IN("assistant", "user")) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id)
);

CREATE TABLE user_notes (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    note TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id)
);

