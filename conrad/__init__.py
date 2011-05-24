"""
Conrad is a simple, magic-free ORM for Python.
See http://github.com/jmohr/conrad for details.
"""

__version__ = (2, 0, 0)
__version_str__ = '.'.join(map(str, __version__))

import query
import adapter
from database import Database
