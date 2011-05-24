from setuptools import setup, find_packages
from conrad import __version_str__ as conrad_version
from conrad import __doc__ as conrad_doc

setup(
    name = 'conrad',
    description = 'A simple ODBC ORM for Python.',
    long_description = conrad_doc,
    author = 'Justin Mohr',
    author_email = 'jmohr@bytepulse.net',
    packages = find_packages(exclude=['*.test.*', '*.test']),
    version = conrad_version,
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
