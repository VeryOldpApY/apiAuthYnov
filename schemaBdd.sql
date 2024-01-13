DROP TABLE IF EXISTS account;
DROP TABLE IF EXISTS role;
DROP TABLE IF EXISTS account_role;

create table account
(
    id       integer not null
        constraint account_pm
            primary key autoincrement,
    uid TEXT NOT NULL UNIQUE,
    username TEXT    not null
        constraint account_pk
            unique,
    password TEXT    not null,
    token    TEXT    not null,
    status TINYINT DEFAULT 1    
);
INSERT INTO account (username, uid, password, token, status)
VALUES ('account_admin', 'uid1', 'password', 'token1', 1),
('account_user', 'uid2', 'password', 'token2', 1);


create table role
(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    uid TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL UNIQUE
);
INSERT INTO role (name, uid)
VALUES ('ROLE_ADMIN', 'uid1'), ('ROLE_USER', 'uid2');


create table account_role
(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id INTEGER NOT NULL,
    role_id INTEGER NOT NULL,
    FOREIGN KEY (account_id) REFERENCES account(id),
    FOREIGN KEY (role_id) REFERENCES role(id)
);
INSERT INTO account_role (account_id, role_id)     
VALUES (1, 1), (2, 2);