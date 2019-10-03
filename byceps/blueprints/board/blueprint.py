"""
byceps.blueprints.board.blueprint
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from ...services.text_markup.service import render_html
from ...util.framework.blueprint import create_blueprint

from ..authorization.registry import permission_registry

from .authorization import (
    BoardPermission,
    BoardPostingPermission,
    BoardTopicPermission,
)


blueprint = create_blueprint('board', __name__)


blueprint.add_app_template_filter(render_html, 'bbcode')


permission_registry.register_enum(BoardPermission)
permission_registry.register_enum(BoardTopicPermission)
permission_registry.register_enum(BoardPostingPermission)
