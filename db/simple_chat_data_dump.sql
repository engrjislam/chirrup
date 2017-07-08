--
-- File generated with SQLiteStudio v3.1.1 on Thu Jul 6 17:01:54 2017
--
-- Text encoding used: System
--
PRAGMA foreign_keys = off;
BEGIN TRANSACTION;

-- Table: messages
INSERT INTO messages (id, room_id, user_id, content, created) VALUES (2, 1, 3, 'Hello', '2107-07-07 16:45:00');
INSERT INTO messages (id, room_id, user_id, content, created) VALUES (1, 1, 2, 'Hi', '2107-07-07 16:45:00');

-- Table: room
INSERT INTO room (id, name, type, user_id, created, updated) VALUES (1, 'room1', 'PRIVATE', 2, '2107-07-07 16:45:00', NULL);

-- Table: room_members
INSERT INTO room_members (id, room_id, user_id, created, updated) VALUES (2, 1, 3, '2107-07-07 16:45:00', NULL);
INSERT INTO room_members (id, room_id, user_id, created, updated) VALUES (1, 1, 2, '2107-07-07 16:45:00', NULL);

-- Table: token
INSERT INTO token (id, user_id, token, status, created, updated) VALUES (1, 2, 'assdfghjklwertyuiop', 'ACTIVE', '2107-07-07 16:45:00', NULL);


-- Table: user
INSERT INTO user (id, name, username, email, password, image, created, updated) VALUES (2, 'ABC2', 'abc2', 'abc2@gmail.com', '1234567890', 'abc2.jpg', '2107-07-07 16:45:00', NULL);
INSERT INTO user (id, name, username, email, password, image, created, updated) VALUES (3, 'ABC3', 'abc3', 'abc3@gmail.com', '1234567890', 'abc3.jpg', '2107-07-07 16:45:00', NULL);

COMMIT TRANSACTION;
PRAGMA foreign_keys = on;
