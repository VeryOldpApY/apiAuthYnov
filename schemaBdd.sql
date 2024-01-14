DROP TABLE IF EXISTS account;

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