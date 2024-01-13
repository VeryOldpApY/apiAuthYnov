DROP TABLE IF EXISTS account;

create table account
(
    id       integer not null
        constraint account_pm
            primary key autoincrement,
    username TEXT    not null
        constraint account_pk
            unique,
    password TEXT    not null,
    token    text    not null
);