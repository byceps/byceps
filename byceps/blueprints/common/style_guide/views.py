"""
byceps.blueprints.common.style_guide.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import xml.etree.ElementTree as ET

from flask import current_app

from ....util.framework.blueprint import create_blueprint
from ....util.framework.templating import templated


blueprint = create_blueprint('style_guide', __name__)


ICONS_FILENAME = 'static/style/icons.svg'


@blueprint.get('/')
@templated
def index():
    """Show style guide."""
    icon_names = list(sorted(_get_icon_names()))

    return {
        'icon_names': icon_names,
    }


def _get_icon_names():
    """Extract icon names from SVG file."""
    with current_app.open_resource(ICONS_FILENAME) as f:
        tree = ET.parse(f)

    svg_namespace = 'http://www.w3.org/2000/svg'
    symbol_elems = tree.iterfind('.//{%s}symbol' % svg_namespace)
    return {elem.get('id') for elem in symbol_elems}
