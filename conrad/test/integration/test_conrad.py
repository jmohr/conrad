import os

from conrad.test import resource, create_test_database
from conrad import Database


class TestDatabase(object):

    def setup(self):
        self.test_db = create_test_database()
        self.dsn = 'DRIVER={{SQLite3}};DATABASE={}'.format(self.test_db)

    def teardown(self):
        os.unlink(self.test_db)

    def test_usage(self):
        db = Database(self.dsn)
        all_artists = db['artist'].all()
        assert len(all_artists) != 0
        my_artist = db['artist'].create(name='Randoman')
        assert my_artist in db['artist'].all()
        my_artist['name'] = 'Genericat'
        assert my_artist.save_required
        my_artist_again = db['artist'].get(my_artist.pk)
        assert my_artist_again['name'] == 'Randoman'
        len_before = len(db['album'].all())
        for i in range(10):
            db['album'].create(title='Album {}'.format(i), artist_id=my_artist.pk)
        len_after = len(db['album'].all())
        assert len_after - len_before == 10
