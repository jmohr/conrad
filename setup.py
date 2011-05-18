from setuptools import setup, find_packages
import conrad

setup(
    name = 'conrad',
    description = 'A simple ODBC ORM for Python.',
    author = 'Justin Mohr',
    author_email = 'jmohr@bytepulse.net',
    packages = find_packages(exclude=['*.test.*', '*.test']),
    version = '.'.join(map(str,conrad.version)),
    install_requires = ['pyodbc', 'jinja2'],
    license = 'BSD',
    url = 'http://github.com/jmohr/conrad',
    package_data = {'':['README.md','LICENSE','TODO']},
)
