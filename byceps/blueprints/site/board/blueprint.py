"""
byceps.blueprints.site.board.blueprint
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from ....permissions.board import (
    BoardPermission,
    BoardPostingPermission,
    BoardTopicPermission,
)
from ....services.text_markup.service import render_html
from ....util.authorization import register_permission_enum
from ....util.framework.blueprint import create_blueprint


blueprint = create_blueprint('board', __name__)


blueprint.add_app_template_filter(render_html, 'bbcode')


register_permission_enum(BoardPermission)
register_permission_enum(BoardTopicPermission)
register_permission_enum(BoardPostingPermission)
