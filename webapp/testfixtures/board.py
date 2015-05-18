# -*- coding: utf-8 -*-

from byceps.blueprints.board.models import Category, Topic

from .brand import create_brand


def create_category(*, brand=None, number=1, position=None, slug=None,
                    title=None):
    if brand is None:
        brand = create_brand()

    if position is None:
        position = number

    if slug is None:
        slug = 'category-{}'.format(number)

    if title is None:
        title = 'Kategorie {}'.format(number)

    return Category(
        brand=brand,
        position=position,
        slug=slug,
        title=title)


def create_topic(category, creator, *, number=1, title=None, body=None):
    if title is None:
        title = 'Thema {}'.format(number)

    if body is None:
        body = 'Inhalt von Thema {}'.format(number)

    return Topic.create(category, creator, title, body)
