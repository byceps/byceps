# -*- coding: utf-8 -*-

from argparse import ArgumentParser
from itertools import count, islice

from byceps.database import db


def get_config_name_from_args():
    parser = ArgumentParser()
    parser.add_argument('config_name', metavar='<config name>')
    args = parser.parse_args()
    return args.config_name


def add_to_database(f):
    def decorated(*args, **kwargs):
        entity = f(*args, **kwargs)
        db.session.add(entity)
        return entity
    return decorated


def add_all_to_database(f):
    def decorated(*args, **kwargs):
        entities = f(*args, **kwargs)
        for entity in entities:
            db.session.add(entity)
        return entities
    return decorated


def generate_positive_numbers(n):
    return islice(count(1), n)
