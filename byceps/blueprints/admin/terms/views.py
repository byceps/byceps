"""
byceps.blueprints.admin.terms.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from flask import abort

from ....services.terms import consent_service as terms_consent_service
from ....services.terms import document_service as terms_document_service
from ....services.terms import version_service as terms_version_service
from ....services.user import service as user_service
from ....util.framework.blueprint import create_blueprint
from ....util.framework.templating import templated

from ...authorization.decorators import permission_required
from ...authorization.registry import permission_registry

from .authorization import TermsPermission


blueprint = create_blueprint('terms_admin', __name__)


permission_registry.register_enum(TermsPermission)


@blueprint.route('/documents/<document_id>')
@permission_required(TermsPermission.view)
@templated
def view_document(document_id):
    """Show the document's attributes and versions."""
    document = terms_document_service.find_document(document_id)
    if document is None:
        abort(404)

    versions = terms_version_service.get_versions(document.id)

    _add_version_creators(versions)

    consent_counts_by_version_id = terms_consent_service \
        .count_consents_for_document_versions(document.id)

    for version in versions:
        version.consent_count = consent_counts_by_version_id[version.id]

    document = terms_document_service.find_document(document.id)

    return {
        'document': document,
        'versions': versions,
    }


def _add_version_creators(versions):
    creator_ids = {v.snippet_version.creator_id for v in versions}
    creators = user_service.find_users(creator_ids, include_avatars=True)
    creators_by_id = user_service.index_users_by_id(creators)

    for version in versions:
        version.creator = creators_by_id[version.snippet_version.creator_id]


@blueprint.route('/versions/<uuid:version_id>')
@permission_required(TermsPermission.view)
@templated
def view_version(version_id):
    """Show the version."""
    version = _get_version_or_404(version_id)

    return {
        'version': version,
    }


@blueprint.route('/versions/<uuid:version_id>/body.html')
@permission_required(TermsPermission.view)
@templated
def view_version_body_html(version_id):
    """Show the version's HTML body."""
    version = _get_version_or_404(version_id)

    return version.body


def _get_version_or_404(version_id):
    version = terms_version_service.find_version(version_id)

    if version is None:
        abort(404)

    return version
