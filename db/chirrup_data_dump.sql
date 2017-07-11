--
-- File generated with SQLiteStudio v3.1.1 on Thu Jul 6 17:01:54 2017
--
-- Text encoding used: System
--
PRAGMA foreign_keys = off;
BEGIN TRANSACTION;

-- Table: messages
INSERT INTO messages (message_id, room_id, user_id, content, created) VALUES (1, 1, 3, 'Hello', '2107-07-07 16:45:00');
INSERT INTO messages (message_id, room_id, user_id, content, created) VALUES (2, 1, 2, 'Hi', '2107-07-07 16:45:00');

-- Table: room
INSERT INTO rooms (room_id, name, type, user_id, status, created, updated) VALUES (1, 'room1', 'PRIVATE', 2, 'ACTIVE','2107-07-07 16:45:00', NULL);

-- Table: room_users
INSERT INTO room_users (id, room_id, user_id, created, updated) VALUES (2, 1, 3, '2107-07-07 16:45:00', NULL);
INSERT INTO room_users (id, room_id, user_id, created, updated) VALUES (1, 1, 2, '2107-07-07 16:45:00', NULL);

-- Table: token
INSERT INTO tokens (id, user_id, token, status, created, updated) VALUES (1, 2, 'assdfghjklwertyuiop', 'ACTIVE', '2107-07-07 16:45:00', NULL);

-- Table: user
INSERT INTO users (user_id, username, password, email, status, created, updated) VALUES (2, 'ABC2',  '1234567890', 'abc2@gmail.com', 'ACTIVE', '2107-07-07 16:45:00', NULL);
INSERT INTO users (user_id, username, password, email, status, created, updated) VALUES (3, 'ABC3', '1234567890', 'abc2@gmail.com', 'ACTIVE', '2107-07-07 16:45:00', NULL);

COMMIT TRANSACTION;
PRAGMA foreign_keys = on;
