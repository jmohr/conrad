CREATE TABLE artist (
    id INTEGER PRIMARY KEY,
    name STRING NOT NULL
);

CREATE TABLE album (
    id INTEGER PRIMARY KEY,
    title STRING NOT NULL,
    artist_id INTEGER,
    FOREIGN KEY(artist_id) REFERENCES artist(id)
);

-- Insert some artists
INSERT INTO artist (name) VALUES ('James Brown');
INSERT INTO artist (name) VALUES ('Richard D. James');
INSERT INTO artist (name) VALUES ('Fugazi');
INSERT INTO artist (name) VALUES ('Dinosaur Jr.');

-- Insert some albums
INSERT INTO album (title, artist_id) VALUES ('I Got You', 
        (SELECT id FROM artist WHERE name = 'James Brown'));
INSERT INTO album (title, artist_id) VALUES ('Richard D. James Album', 
        (SELECT id FROM artist WHERE name = 'Richard D. James'));
INSERT INTO album (title, artist_id) VALUES ('Instrument', 
        (SELECT id FROM artist WHERE name = 'Fugazi'));
INSERT INTO album (title, artist_id) VALUES ('13 Songs', 
        (SELECT id FROM artist WHERE name = 'Fugazi'));
INSERT INTO album (title, artist_id) VALUES ('Youre Living All Over Me', 
        (SELECT id FROM artist WHERE name = 'Dinosaur Jr.'));

