from importlib import import_module

def load(name):
    """Loads the given adapter by name, and returns the module."""
    if not name.startswith('conrad'):
        imp = 'conrad.db.{}'.format(name.lower())
    mod = import_module(imp)
    return getattr(mod, name)

from adapter import Adapter
from odbc import ODBC

database = ODBC()