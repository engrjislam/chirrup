--
-- File generated with SQLiteStudio v3.1.1 on Thu Jul 6 17:01:54 2017
--
-- Text encoding used: System
--
PRAGMA foreign_keys = off;
BEGIN TRANSACTION;

-- Table: messages
INSERT INTO messages (message_id, room_id, user_id, content, created) VALUES (1, 1, 3, 'Hello1', 1362017481);
INSERT INTO messages (message_id, room_id, user_id, content, created) VALUES (2, 1, 2, 'Hi', 1362017481);
INSERT INTO messages (message_id, room_id, user_id, content, created) VALUES (3, 2, 3, 'Hello123123', 1362017481);
INSERT INTO messages (message_id, room_id, user_id, content, created) VALUES (4, 2, 2, 'H444i', 1362017481);
INSERT INTO messages (message_id, room_id, user_id, content, created) VALUES (5, 3, 3, 'Hello44', 1362017481);
INSERT INTO messages (message_id, room_id, user_id, content, created) VALUES (6, 3, 2, 'aa', 1362017481);
INSERT INTO messages (message_id, room_id, user_id, content, created) VALUES (7, 3, 2, 'bbb', 1362017481);
INSERT INTO messages (message_id, room_id, user_id, content, created) VALUES (8, 3, 2, 'ccc', 1362017481);
INSERT INTO messages (message_id, room_id, user_id, content, created) VALUES (9, 3, 2, 'dddd', 1362017481);
INSERT INTO messages (message_id, room_id, user_id, content, created) VALUES (10, 3, 2, 'gggg', 1362017481);

-- Table: room
INSERT INTO room (room_id, name, type, user_id, status, created, updated) VALUES (1, 'room1', 'PRIVATE', 1, 'ACTIVE', 1362017481, NULL);
INSERT INTO room (room_id, name, type, user_id, status, created, updated) VALUES (2, 'room2', 'PRIVATE', 2, 'ACTIVE', 1362017481, NULL);
INSERT INTO room (room_id, name, type, user_id, status, created, updated) VALUES (3, 'room3', 'PRIVATE', 2, 'ACTIVE', 1362017481, NULL);

-- Table: room_users
INSERT INTO room_users (id, room_id, user_id, created, updated) VALUES (1, 1, 3, 1362017481, NULL);
INSERT INTO room_users (id, room_id, user_id, created, updated) VALUES (2, 1, 2, 1362017481, NULL);

-- Table: token
-- INSERT INTO tokens (id, user_id, token, status, created, updated) VALUES (1, 2, 'assdfghjklwertyuiop', 'ACTIVE', 1362017481, NULL);

-- Table: user
INSERT INTO user (user_id, username, password, email, status, created, updated) VALUES (1, 'ABC1', '1234567890', '1@gmail.com', 'ACTIVE', 1362017481, NULL);
INSERT INTO user (user_id, username, password, email, status, created, updated) VALUES (2, 'ABC2', '1234567890', '2@gmail.com', 'ACTIVE', 1362017481, NULL);
INSERT INTO user (user_id, username, password, email, status, created, updated) VALUES (3, 'ABC3', '1234567890', '3@gmail.com', 'ACTIVE', 1362017481, NULL);
INSERT INTO user (user_id, username, password, email, status, created, updated) VALUES (4, 'ABC4', '1234567890', '4@gmail.com', 'ACTIVE', 1362017481, NULL);
INSERT INTO user (user_id, username, password, email, status, created, updated) VALUES (5, 'ABC5', '1234567890', '5@gmail.com', 'ACTIVE', 1362017481, NULL);
INSERT INTO user (user_id, username, password, email, status, created, updated) VALUES (6, 'ABC6', '1234567890', '6@gmail.com', 'ACTIVE', 1362017481, NULL);
INSERT INTO user (user_id, username, password, email, status, created, updated) VALUES (7, 'ABC7', '1234567890', '7@gmail.com', 'ACTIVE', 1362017481, NULL);
INSERT INTO user (user_id, username, password, email, status, created, updated) VALUES (8, 'ABC8', '1234567890', '8@gmail.com', 'ACTIVE', 1362017481, NULL);
INSERT INTO user (user_id, username, password, email, status, created, updated) VALUES (9, 'ABC9', '1234567890', '9@gmail.com', 'ACTIVE', 1362017481, NULL);
INSERT INTO user (user_id, username, password, email, status, created, updated) VALUES (10, 'ABC10', '1234567890', '10@gmail.com', 'ACTIVE', 1362017481, NULL);

COMMIT TRANSACTION;
PRAGMA foreign_keys = on;
