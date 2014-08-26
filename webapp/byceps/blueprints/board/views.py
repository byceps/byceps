# -*- coding: utf-8 -*-

"""
byceps.blueprints.board.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2014 Jochen Kupperschmidt
"""

from ...util.framework import create_blueprint
from ...util.templating import templated

from ..authorization.registry import permission_registry

from .authorization import BoardPostingPermission, BoardTopicPermission
from .models import Category, Topic


blueprint = create_blueprint('board', __name__)


permission_registry.register_enum(BoardTopicPermission)
permission_registry.register_enum(BoardPostingPermission)


@blueprint.route('/categories')
@templated
def category_index():
    """List categories."""
    categories = Category.query.for_current_brand().all()
    return {'categories': categories}


@blueprint.route('/categories/<id>')
@templated
def category_view(id):
    """List latest topics in the category."""
    category = Category.query.get_or_404(id)
    return {'category': category}


@blueprint.route('/topics/<id>')
@templated
def topic_view(id):
    """List postings for the topic."""
    topic = Topic.query.get_or_404(id)
    return {'topic': topic}
