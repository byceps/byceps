# -*- coding: utf-8 -*-

"""
byceps.blueprints.news.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2015 Jochen Kupperschmidt
"""

from ...util.framework import create_blueprint
from ...util.templating import templated

from .service import get_items_paginated


blueprint = create_blueprint('news', __name__)


ITEMS_PER_PAGE = 4


@blueprint.route('/', defaults={'page': 1})
@blueprint.route('/pages/<int:page>')
@templated
def index(page):
    """Show a page of news items."""
    items = get_items_paginated(page, ITEMS_PER_PAGE)
    return {
        'items': items,
        'page': page,
    }
