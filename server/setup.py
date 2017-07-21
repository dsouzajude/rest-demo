#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='myshop-server',
    description='A REST server for myshop.',
    version='0.0.1',
    packages=find_packages(),
    include_package_data=True,
    data_files=[
        ('myshop/certs', ['certs/server.pem', 'certs/server.key']),
        ('myshop/data', ['data/myshop.db'])
    ],
    install_requires=[
        'passlib',
        'bottle',
        'gunicorn>=0.17.0',
        'SQLAlchemy',
        'webtest',
        'nose',
        'mock',
        'jsonschema',
    ],
    entry_points={
        'console_scripts': [
            'myshop-server = myshop.server:main',
        ],
    },
    zip_safe=False,
)
