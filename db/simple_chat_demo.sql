--
-- File generated with SQLiteStudio v3.1.1 on Thu Jul 6 15:38:18 2017
--
-- Text encoding used: System
--
PRAGMA foreign_keys = off;
BEGIN TRANSACTION;

-- Table: massages
CREATE TABLE massages (
    id      BIGINT   PRIMARY KEY,
    room_id BIGINT   REFERENCES room (id) ON DELETE CASCADE
                                          ON UPDATE CASCADE,
    user_id BIGINT   REFERENCES user (id) ON DELETE CASCADE
                                          ON UPDATE CASCADE
                     NOT NULL,
    content TEXT     NOT NULL,
    created DATETIME NOT NULL
);


-- Table: room
CREATE TABLE room (
    id      BIGINT       PRIMARY KEY,
    name    VARCHAR (64) UNIQUE
                         NOT NULL,
    type    VARCHAR (8)  NOT NULL,
    user_id BIGINT       NOT NULL
                         REFERENCES user (id) ON DELETE CASCADE
                                              ON UPDATE CASCADE,
    created DATETIME     NOT NULL,
    updated DATETIME
);


-- Table: room_members
CREATE TABLE room_members (
    id      BIGINT   PRIMARY KEY,
    room_id BIGINT   REFERENCES room (id) ON DELETE CASCADE
                                          ON UPDATE CASCADE,
    user_id BIGINT   REFERENCES user (id) ON DELETE CASCADE
                                          ON UPDATE CASCADE,
    created DATETIME NOT NULL,
    updated DATETIME
);


-- Table: token
CREATE TABLE token (
    id      BIGINT        PRIMARY KEY,
    user_id BIGINT        REFERENCES user (id) ON DELETE RESTRICT
                                               ON UPDATE CASCADE,
    token   VARCHAR (128) NOT NULL
                          UNIQUE,
    status  VARCHAR (8)   NOT NULL,
    created DATETIME      NOT NULL,
    updated DATETIME
);


-- Table: user
CREATE TABLE user (
    id       BIGINT        PRIMARY KEY,
    name     VARCHAR (128) NOT NULL,
    username VARCHAR (64)  UNIQUE
                           NOT NULL,
    email    VARCHAR (64)  UNIQUE
                           NOT NULL,
    password VARCHAR (64)  NOT NULL,
    image    VARCHAR (64),
    created  DATETIME      NOT NULL,
    updated  DATETIME
);


COMMIT TRANSACTION;
PRAGMA foreign_keys = on;
