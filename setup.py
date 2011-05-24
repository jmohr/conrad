from setuptools import setup, find_packages
import conrad

setup(
    name = 'conrad',
    description = 'A simple ODBC ORM for Python.',
    long_description = conrad.__doc__,
    author = 'Justin Mohr',
    author_email = 'jmohr@bytepulse.net',
    packages = find_packages(exclude=['*.test.*', '*.test']),
    version = conrad.__version_str__,
    install_requires = ['pyodbc', 'jinja2'],
    license = 'BSD',
    url = 'http://github.com/jmohr/conrad',
    package_data = {'':['README.md','LICENSE','TODO']},
    classifiers = ['Intended Audience :: Developers',
                   'Development Status :: 4 - Beta',
                   'License :: OSI Approved :: BSD License',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python :: 2.7',
                   'Topic :: Database']
)
