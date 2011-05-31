#!/usr/bin/env python

import flask


artist_map = {
    1: {
        'id': 1,
        'name': 'James Brown',
    },
    2: {
        'id': 2,
        'name': 'Richard D. James',
    },
    3: {
        'id': 3,
        'name': 'Fugazi',
    },
    4: {
        'id': 4,
        'name': 'Dinosaur Jr.',
    },
}


app = flask.Flask('conrad_test')

@app.route('/api/artist/<int:id>')
def get_artist(id):
    if not artist_map.has_key(id):
        flask.abort(404)
    return flask.jsonify(artist_map[id])

@app.route('/api/artist', methods=['POST'])
def create_artist():
    id = max(artist_map.keys()) + 1
    artist_map[id] = {
        'id': id,
        'name': flask.request.form['name'],
    }
    return flask.jsonify(artist_map[id])

@app.route('/api/artist/<int:id>', methods=['PUT'])
def update_artist(id):
    if not artist_map.has_key(id):
        flask.abort(404)
    artist_map[id] = {
        'id': id,
        'name': flask.request.form['name'],
    }
    return flask.jsonify(artist_map[id])

@app.route('/api/artist/<int:id>', methods=['DELETE'])
def delete_artist(id):
    if not artist_map.has_key(id):
        flask.abort(404)
    del artist_map[id]
    return flask.jsonify({})

@app.route('/api/artists')
def list_artists():
    return flask.jsonify(artist_map)

if __name__ == '__main__': app.run()
