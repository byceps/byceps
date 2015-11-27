# -*- coding: utf-8 -*-

"""
bootstrap.board
~~~~~~~~~~~~~~~

:Copyright: 2006-2015 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.blueprints.board.models import Category
from byceps.blueprints.board import service

from .util import add_to_database


@add_to_database
def create_category(brand, position, slug, title, description):
    return Category(brand, position, slug, title, description)


def get_first_category(brand):
    return Category.query.filter_by(brand=brand).filter_by(position=1).one()


def create_topic(category, creator, title, body):
    return service.create_topic(category, creator, title, body)


def create_posting(topic, creator, body):
    return service.create_posting(topic, creator, body)
