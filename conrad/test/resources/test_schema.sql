-- This is a total hack, but each statement must be on exactly one line.
-- Check out the setup() method in test/units/test_query.py to see why.
DROP TABLE IF EXISTS test_data;
CREATE TABLE test_data (id integer primary key, name string, age integer, birthdate date, active boolean, address text, email string);
INSERT INTO test_data (name, age, birthdate, active, address, email) VALUES ('Test Guy 1', 20, '2/2/1991', 1, '123 Test St\nTesterton, TE', 'testguy1@example.com');
INSERT INTO test_data (name, age, birthdate, active, address, email) VALUES ('Test Guy 2', 30, '2/2/1981', 0, '234 Fake Ave\nFaketon, FA', 'testguy2@example.co.uk');
-- Create some foreign key joy
DROP TABLE IF EXISTS artist;
DROP TABLE IF EXISTS album;
CREATE TABLE artist (id integer primary key, name string);
CREATE TABLE album (id integer primary key, name string, artist_id integer, FOREIGN KEY(artist_id) REFERENCES artist(id));
INSERT INTO artist (name) VALUES ('Billy Joel');
INSERT INTO artist (name) VALUES ('Fugazi');
INSERT INTO artist (name) VALUES ('Foo Fighters');
INSERT INTO album (name, artist_id) VALUES ('Glass Houses', (SELECT id FROM artist WHERE name = 'Billy Joel'));
INSERT INTO album (name, artist_id) VALUES ('Instrument', (SELECT id FROM artist WHERE name = 'Fugazi'));
INSERT INTO album (name, artist_id) VALUES ('The Colour And The Shape', (SELECT id FROM artist WHERE name = 'Foo Fighters'));