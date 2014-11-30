# -*- coding: utf-8 -*-

from byceps.blueprints.brand.models import Brand


def create_brand(*, id='acme', title='Acme Entertainment Convention'):
    return Brand(id=id, title=title)
