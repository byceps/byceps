# -*- coding: utf-8 -*-

from setuptools import setup


setup(
    name='BYCEPS',
    version='0.0',
    description='the Bring-Your-Computer Event Processing System',
    author='Jochen "Y0Gi" Kupperschmidt',
    author_email='homework@nwsnet.de',
    url='http://homework.nwsnet.de/',
    license='Modified BSD',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Flask',
        'Intended Audience :: Developers',
        'Intended Audience :: Other Audience',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: German',
        'Programming Language :: JavaScript',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Communications',
        'Topic :: Games/Entertainment',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content :: Message Boards',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content :: News/Diary',
    ],
    packages=['byceps'],
    tests_require=['nose2'],
    test_suite='nose2.collector.collector',
)
