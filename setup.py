#!/usr/bin/env python
from setuptools import setup


requirements = [
    'kombu',
    'pika',
    'gevent',
    'click',
    'coid',
    'click',
    'kafka-python',  # should use pykafka
    'kazoo',
    'pyes',
    'redis',
    'sqlalchemy',
    'psycopg2',
    'pilo',
]


setup(
    name='msgr',
    version='0.0.1',
    url='https://www.github.com/cieplak/msgr',
    author='patrick cieplak',
    author_email='patrick.cieplak@gmail.com',
    description='broker agnostic messaging library',
    packages=['msgr'],
    license=open('LICENSE').read(),
    include_package_data=True,
    install_requires=requirements,
    tests_require=['nose'],
    scripts=['bin/msgr']
)
