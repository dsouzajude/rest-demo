#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='myshop-ui',
    description='A web client for the myshop REST API server.',
    version='0.0.1',
    packages=find_packages(),
    include_package_data=True,
    data_files=[
        ('myshop_ui/certs', ['certs/server.pem', 'certs/server.key']),
        ('myshop_ui/templates', [
            'templates/layout.mako',
            'templates/index.mako',
            'templates/register.mako',
            'templates/login.mako',
            'templates/welcome.mako'
        ])
    ],
    install_requires=[
        'bottle',
        'requests>=2.11.1',
        'gunicorn>=0.17.0',
        'webtest',
        'nose',
        'mock',
        'mako',
    ],
    entry_points={
        'console_scripts': [
            'myshop-ui = myshop_ui.server:main',
        ],
    },
    zip_safe=False,
)
