from setuptools import setup, find_packages

setup(
    name='conrad',
    description='A simple ODBC ORM for Python.',
    long_description='Conrad is a simple, magic-free ORM for Python. See http://github.com/jmohr/conrad for details.',
    author='Justin Mohr',
    author_email='jmohr@bytepulse.net',
    packages=find_packages(exclude=['*.test.*', '*.test']),
    version=':versiontools:conrad:',
    install_requires=['pyodbc', 'restkit', 'versiontools'],
    setup_requires=['setuptools'],
    tests_require=['nose', 'flask'],
    license='BSD',
    url='http://github.com/jmohr/conrad',
    package_data={'': ['README.md', 'LICENSE', 'TODO']},
    classifiers=['Intended Audience :: Developers',
                 'Development Status :: 4 - Beta',
                 'License :: OSI Approved :: BSD License',
                 'Operating System :: OS Independent',
                 'Programming Language :: Python :: 2.7',
                 'Topic :: Database']
)
