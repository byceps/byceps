"""
byceps.blueprints.style_guide.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2017 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from ...util.framework.blueprint import create_blueprint
from ...util.templating import templated


blueprint = create_blueprint('style_guide', __name__)


@blueprint.route('/')
@templated
def index():
    """Show style guide."""
