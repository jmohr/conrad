import os, os.path
import sqlite3
import sys
import tempfile

test_dir = os.path.abspath(os.path.dirname(__file__))
resource_dir = os.path.join(test_dir, 'resources')

def resource(name, *args):
    """Returns a file handle to the requested resource."""
    return open(os.path.join(resource_dir, name), *args)

test_databases = []

def create_test_database():
    db_file = tempfile.mkstemp()[1]
    cxn = sqlite3.connect(db_file)
    cxn.executescript(resource('test_schema.sql').read())
    cxn.close()
    return db_file

