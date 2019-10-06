import codecs

from setuptools import setup


def read_lines_from_file(filename):
    with codecs.open(filename, encoding='utf-8') as f:
        return [line.rstrip('\n') for line in f]


requirements = read_lines_from_file('requirements.txt')
requirements_dev = read_lines_from_file('requirements-development.txt')


setup(
    name='BYCEPS',
    version='0.0',
    description='the Bring-Your-Computer Event Processing System',
    author='Jochen "Y0Gi" Kupperschmidt',
    author_email='homework@nwsnet.de',
    url='https://byceps.nwsnet.de/',
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
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Communications',
        'Topic :: Games/Entertainment',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content :: Content Management System',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content :: Message Boards',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content :: News/Diary',
    ],
    packages=['byceps'],
    install_requires=requirements,
    setup_requires=['pytest-runner'],
    tests_require=requirements_dev,
)
