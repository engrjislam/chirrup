--
-- File generated with SQLiteStudio v3.1.1 on Thu Jul 6 15:38:18 2017
--
-- Text encoding used: System
--
PRAGMA foreign_keys = off;
BEGIN TRANSACTION;

-- Table: messages
CREATE TABLE messages (
    message_id      INTEGER  PRIMARY KEY ,
    room_id         BIGINT   REFERENCES room (room_id) ON DELETE CASCADE
                                                       ON UPDATE CASCADE,
    user_id         BIGINT   REFERENCES user (user_id) ON DELETE CASCADE
                                                       ON UPDATE CASCADE
                             NOT NULL,
    content         TEXT     NOT NULL,
    created         INTEGER  NOT NULL
);


-- Table: room
CREATE TABLE room (
    room_id BIGINT       PRIMARY KEY,
    name    VARCHAR (64) UNIQUE
                         NOT NULL,
    type    VARCHAR (8)  NOT NULL,
    admin   BIGINT       NOT NULL
                         REFERENCES user (user_id) ON DELETE RESTRICT  -- user can't remove the account if admin in a room
                                                   ON UPDATE CASCADE,
    status VARCHAR(16)   NOT NULL, -- ACTIVE / INACTIVE
    created INTEGER      NOT NULL,
    updated INTEGER
);


-- Table: room_users, named based on room and user relation
CREATE TABLE room_users (
    id      BIGINT   PRIMARY KEY,
    room_id BIGINT   REFERENCES room (room_id) ON DELETE CASCADE
                                               ON UPDATE CASCADE,
    user_id BIGINT   REFERENCES user (user_id) ON DELETE CASCADE
                                               ON UPDATE CASCADE,
    joined INTEGER NOT NULL
);

/*
-- Table: token
CREATE TABLE token (
    id      BIGINT        PRIMARY KEY,
    user_id BIGINT        REFERENCES user (user_id) ON DELETE RESTRICT
                                               ON UPDATE CASCADE,
    token   VARCHAR (128) NOT NULL
                          UNIQUE,
    status  VARCHAR (8)   NOT NULL,
    created INTEGER      NOT NULL,
    updated INTEGER
);
*/

-- Table: user
CREATE TABLE user (
    user_id  BIGINT        PRIMARY KEY,
    username VARCHAR (128) UNIQUE
                           NOT NULL,
    email    VARCHAR (64)  UNIQUE
                           NOT NULL,
    status   VARCHAR(16)   NOT NULL, -- ACTIVE / INACTIVE
    created  INTEGER       NOT NULL,
    updated  INTEGER
);

CREATE TABLE user_profile (
    user_id  BIGINT        REFERENCES user (user_id) ON DELETE CASCADE
                                                     ON UPDATE CASCADE,
    nickname VARCHAR (64)  UNIQUE
                           NOT NULL,
    image    VARCHAR (64),
    PRIMARY KEY(user_id)
);


COMMIT TRANSACTION;
PRAGMA foreign_keys = on;
