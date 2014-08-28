# -*- coding: utf-8 -*-

"""
byceps.blueprints.terms_admin.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2014 Jochen Kupperschmidt
"""

from ...util.framework import create_blueprint
from ...util.templating import templated

from ..authorization.decorators import permission_required
from ..authorization.registry import permission_registry
from ..terms.models import TermsVersion

from .authorization import TermsPermission


blueprint = create_blueprint('terms_admin', __name__)


permission_registry.register_enum(TermsPermission)


@blueprint.route('/')
@permission_required(TermsPermission.list)
@templated
def index():
    """List terms versions."""
    versions = TermsVersion.query.all()
    return {'versions': versions}
