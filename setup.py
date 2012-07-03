#!/usr/bin/env python

from distutils.core import setup

setup(
    name='Ennepe',
    version='0.12',
    description='Static blog generation system',
    author='Decklin Foster',
    author_email='decklin@red-bean.com',
    url='http://www.red-bean.com/decklin/ennepe/',
    classifiers=[
        'Intended Audience :: Advanced End Users',
        'Development Status :: 4 - Beta',
        'License :: MIT/X Consortium License',
        'Internet :: WWW/HTTP :: Dynamic Content :: News/Diary',
        'Operating System :: POSIX',
        'Environment :: Console (Text Based)',
        'Programming Language :: Python',
        ],
    package_dir = {'': 'lib'},
    packages = ['ennepe'],
    scripts = ['ennepe'],
    data_files=[
        # ('share/man1', ['ennepe.1', 'etc...']),
        ],
    )
