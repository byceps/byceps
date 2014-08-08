# -*- coding: utf-8 -*-

"""
byceps.blueprints.contentpage.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2014 Jochen Kupperschmidt
"""

from ...util.framework import create_blueprint

from .models import ContentPage
from .templating import render_page


blueprint = create_blueprint('contentpage', __name__)


def view_latest_by_name(name):
    """Show the latest version of the page with the given name."""
    page = ContentPage.query \
        .for_current_party() \
        .filter_by(name=name) \
        .one()
    return render_page(page.get_latest_version())
