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
INSERT INTO room (room_id, name, type, admin, status, created, updated) VALUES (1, 'room1', 'PRIVATE', 1, 'ACTIVE', 1362017481, NULL);
INSERT INTO room (room_id, name, type, admin, status, created, updated) VALUES (2, 'room2', 'PUBLIC', 2, 'ACTIVE', 1362017481, NULL);
INSERT INTO room (room_id, name, type, admin, status, created, updated) VALUES (3, 'room3', 'PRIVATE', 2, 'ACTIVE', 1362017481, NULL);
INSERT INTO room (room_id, name, type, admin, status, created, updated) VALUES (4, 'room4', 'PRIVATE', 1, 'ACTIVE', 1362017481, NULL);
INSERT INTO room (room_id, name, type, admin, status, created, updated) VALUES (5, 'room5', 'PUBLIC', 2, 'ACTIVE', 1362017481, NULL);
INSERT INTO room (room_id, name, type, admin, status, created, updated) VALUES (6, 'room6', 'PRIVATE', 2, 'ACTIVE', 1362017481, NULL);
INSERT INTO room (room_id, name, type, admin, status, created, updated) VALUES (7, 'room7', 'PRIVATE', 1, 'ACTIVE', 1362017481, NULL);
INSERT INTO room (room_id, name, type, admin, status, created, updated) VALUES (8, 'room8', 'PRIVATE', 2, 'ACTIVE', 1362017481, NULL);
INSERT INTO room (room_id, name, type, admin, status, created, updated) VALUES (9, 'room9', 'PRIVATE', 2, 'ACTIVE', 1362017481, NULL);
INSERT INTO room (room_id, name, type, admin, status, created, updated) VALUES (10, 'room10', 'PRIVATE', 1, 'ACTIVE', 1362017481, NULL);

-- Table: room_users
INSERT INTO room_users (id, room_id, user_id, joined) VALUES (1, 1, 3, 1362017481);
INSERT INTO room_users (id, room_id, user_id, joined) VALUES (2, 1, 2, 1362017481);
INSERT INTO room_users (id, room_id, user_id, joined) VALUES (3, 1, 3, 1362017481);
INSERT INTO room_users (id, room_id, user_id, joined) VALUES (4, 1, 2, 1362017481);
INSERT INTO room_users (id, room_id, user_id, joined) VALUES (5, 1, 3, 1362017481);
INSERT INTO room_users (id, room_id, user_id, joined) VALUES (6, 2, 2, 1362017481);
INSERT INTO room_users (id, room_id, user_id, joined) VALUES (7, 2, 3, 1362017481);
INSERT INTO room_users (id, room_id, user_id, joined) VALUES (8, 2, 2, 1362017481);
INSERT INTO room_users (id, room_id, user_id, joined) VALUES (9, 2, 3, 1362017481);
INSERT INTO room_users (id, room_id, user_id, joined) VALUES (10, 2, 2, 1362017481);

-- Table: token
-- INSERT INTO tokens (id, user_id, token, status, created, updated) VALUES (1, 2, 'assdfghjklwertyuiop', 'ACTIVE', 1362017481, NULL);

-- Table: user
INSERT INTO user (user_id, username, email, status, created, updated) VALUES (1, 'ABC1', '1@gmail.com', 'ACTIVE', 1362017481, NULL);
INSERT INTO user (user_id, username, email, status, created, updated) VALUES (2, 'ABC2', '2@gmail.com', 'ACTIVE', 1362017481, NULL);
INSERT INTO user (user_id, username, email, status, created, updated) VALUES (3, 'ABC3', '3@gmail.com', 'ACTIVE', 1362017481, NULL);
INSERT INTO user (user_id, username, email, status, created, updated) VALUES (4, 'ABC4', '4@gmail.com', 'ACTIVE', 1362017481, NULL);
INSERT INTO user (user_id, username, email, status, created, updated) VALUES (5, 'ABC5', '5@gmail.com', 'ACTIVE', 1362017481, NULL);
INSERT INTO user (user_id, username, email, status, created, updated) VALUES (6, 'ABC6', '6@gmail.com', 'ACTIVE', 1362017481, NULL);
INSERT INTO user (user_id, username, email, status, created, updated) VALUES (7, 'ABC7', '7@gmail.com', 'ACTIVE', 1362017481, NULL);
INSERT INTO user (user_id, username, email, status, created, updated) VALUES (8, 'ABC8', '8@gmail.com', 'ACTIVE', 1362017481, NULL);
INSERT INTO user (user_id, username, email, status, created, updated) VALUES (9, 'ABC9', '9@gmail.com', 'ACTIVE', 1362017481, NULL);
INSERT INTO user (user_id, username, email, status, created, updated) VALUES (10, 'ABC10', '10@gmail.com', 'ACTIVE', 1362017481, NULL);

-- Table: user_profile
INSERT INTO user_profile (user_id, nickname, image) VALUES (1, 'rICK', 'rick.jpg');
INSERT INTO user_profile (user_id, nickname, image) VALUES (2, 'ABC2', 'something.jpg');
INSERT INTO user_profile (user_id, nickname, image) VALUES (3, 'ABC3', 'something.jpg');
INSERT INTO user_profile (user_id, nickname, image) VALUES (4, 'ABC4', 'something.jpg');
INSERT INTO user_profile (user_id, nickname, image) VALUES (5, 'mORTY', 'morty.jpg');
INSERT INTO user_profile (user_id, nickname, image) VALUES (6, 'ABC6', 'something.jpg');
INSERT INTO user_profile (user_id, nickname, image) VALUES (7, 'ABC7', 'something.jpg');
INSERT INTO user_profile (user_id, nickname, image) VALUES (8, 'ABC8', NULL);
INSERT INTO user_profile (user_id, nickname, image) VALUES (9, 'ABC9', NULL);
INSERT INTO user_profile (user_id, nickname, image) VALUES (10, 'ABC10', NULL);


COMMIT TRANSACTION;
PRAGMA foreign_keys = on;
