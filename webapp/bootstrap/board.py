# -*- coding: utf-8 -*-

"""
bootstrap.board
~~~~~~~~~~~~~~~

:Copyright: 2006-2015 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.blueprints.board.models import Category, Posting, Topic

from .util import add_to_database


@add_to_database
def create_category(brand, position, slug, title, description):
    return Category(brand=brand, position=position, slug=slug, title=title,
                    description=description)


def get_first_category(brand):
    return Category.query.filter_by(brand=brand).filter_by(position=1).one()


@add_to_database
def create_topic(category, creator, title, body):
    return Topic.create(category, creator, title, body)


@add_to_database
def create_posting(topic, creator, body):
    return Posting.create(topic, creator, body)
