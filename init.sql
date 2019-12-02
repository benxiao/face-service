CREATE DATABASE faces;

use faces;

create table person (
    id serial primary key,
    name VARCHAR(100) unique not null,
    encoding json not null
)