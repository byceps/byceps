"""
byceps.blueprints.site.board.blueprint
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from ....services.text_markup.service import render_html
from ....util.framework.blueprint import create_blueprint


blueprint = create_blueprint('board', __name__)


blueprint.add_app_template_filter(render_html, 'bbcode')
