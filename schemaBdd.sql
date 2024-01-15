DROP TABLE IF EXISTS account;
DROP TABLE IF EXISTS role;
DROP TABLE IF EXISTS account_role;

create table account
(
    id       integer not null
        constraint account_pm
            primary key autoincrement,
    username text    not null
        constraint account_pk
            unique,
    password text    not null,
    token    text    not null,
    dateExpire_Token     text    not null,
    refresh_token    text    not null,
    dateExpire_RefreshToken     text    not null,
    countErrorLogin integer default 0,
    dateExpire_ErrorLogin     text    not null,
    status text not null,   
    dateExpire_Status     text,
    "from"    text
);
INSERT INTO account (uid, username, password, token, dateExpire_Token, refresh_token, dateExpire_RefreshToken, countErrorLogin, dateExpire_ErrorLogin, status, )
VALUES ('uid1', 'account_admin', 'password', 'token1', to_char(sysdate+1), 'refresh_token?', to_char(sysdate+1), 'dateExpire_ErrorLogin?', 'opened'),
('uid2', 'account_user', 'password', 'token2', to_char(sysdate+1), 'refresh_token?', to_char(sysdate+1), 'dateExpire_ErrorLogin?', 'opened');

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