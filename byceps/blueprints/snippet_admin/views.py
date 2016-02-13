# -*- coding: utf-8 -*-

"""
byceps.blueprints.snippet_admin.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from difflib import HtmlDiff
from operator import attrgetter

from flask import abort, g, render_template, request, url_for

from ...database import db
from ...util.dateformat import format_datetime_short
from ...util.framework import create_blueprint, flash_success
from ...util.iterables import pairwise
from ...util.templating import templated
from ...util.views import redirect_to, respond_no_content_with_location

from ..authorization.decorators import permission_required
from ..authorization.registry import permission_registry
from ..party.models import Party
from ..snippet.models.mountpoint import Mountpoint
from ..snippet.models.snippet import CurrentVersionAssociation, Snippet, \
    SnippetVersion
from ..snippet.templating import get_snippet_context

from .authorization import MountpointPermission, SnippetPermission
from .forms import MountpointCreateForm, MountpointUpdateForm, \
    SnippetCreateForm, SnippetUpdateForm
from . import service


blueprint = create_blueprint('snippet_admin', __name__)


permission_registry.register_enum(MountpointPermission)
permission_registry.register_enum(SnippetPermission)


@blueprint.route('/')
@permission_required(SnippetPermission.list)
@templated
def index():
    """List parties to choose from."""
    parties_with_snippet_counts = service.get_parties_with_snippet_counts()

    return {
        'parties_with_snippet_counts': parties_with_snippet_counts,
    }


@blueprint.route('/<party_id>')
@permission_required(SnippetPermission.list)
@templated
def index_for_party(party_id):
    """List snippets for that party."""
    party = Party.query.get_or_404(party_id)

    snippets = Snippet.query \
        .for_party(party) \
        .options(
            db.joinedload('current_version_association').joinedload('version')
        ) \
        .all()

    mountpoints = Mountpoint.query.for_party(party).all()

    return {
        'party': party,
        'snippets': snippets,
        'mountpoints': mountpoints,
    }


@blueprint.route('/versions/<uuid:id>')
@permission_required(SnippetPermission.view_history)
def view_version(id):
    """Show the snippet with the given id."""
    version = find_version(id)

    try:
        snippet_context = get_snippet_context(version)

        context = {
            'party': version.snippet.party,
            'snippet_title': snippet_context['title'],
            'snippet_head': snippet_context['head'],
            'snippet_body': snippet_context['body'],
        }

        return render_template('snippet_admin/view_version.html', **context)
    except Exception as e:
        context = {
            'party': version.snippet.party,
            'error_message': str(e),
        }

        return render_template('snippet_admin/view_version_error.html',
                               **context), \
               500


@blueprint.route('/difference/from/<uuid:from_version_id>/to/<uuid:to_version_id>')
@permission_required(SnippetPermission.view_history)
@templated
def view_difference(from_version_id, to_version_id):
    """Show the difference between two snippet versions."""
    from_version = find_version(from_version_id)
    to_version = find_version(to_version_id)

    # TODO: Diff title, head, and image path, too.

    from_lines = from_version.body.split('\n')
    to_lines = to_version.body.split('\n')

    from_description = format_datetime_short(from_version.created_at)
    to_description = format_datetime_short(to_version.created_at)

    html_diff = HtmlDiff().make_table(from_lines, to_lines,
                                      from_description, to_description,
                                      context=True, numlines=3)

    return {
        'diff': html_diff,
    }


@blueprint.route('/<uuid:id>/history')
@permission_required(SnippetPermission.view_history)
@templated
def history(id):
    snippet = find_snippet_by_id(id)

    versions = snippet.get_versions()
    versions_pairwise = list(pairwise(versions + [None]))

    return {
        'snippet': snippet,
        'versions_pairwise': versions_pairwise,
    }


@blueprint.route('/for_party/<party_id>/create')
@permission_required(SnippetPermission.create)
@templated
def create_snippet_form(party_id):
    """Show form to create a snippet."""
    party = Party.query.get_or_404(party_id)

    form = SnippetCreateForm()

    return {
        'party': party,
        'form': form,
    }


@blueprint.route('/for_party/<party_id>', methods=['POST'])
@permission_required(SnippetPermission.create)
def create_snippet(party_id):
    """Create a snippet."""
    party = Party.query.get_or_404(party_id)
    form = SnippetCreateForm(request.form)

    name = form.name.data.strip().lower()

    snippet = Snippet(name=name, party=party)
    db.session.add(snippet)

    version = SnippetVersion(
        snippet=snippet,
        creator=g.current_user,
        title=form.title.data.strip(),
        head=form.head.data.strip(),
        body=form.body.data.strip(),
        image_url_path=form.image_url_path.data.strip())
    db.session.add(version)

    current_version_association = CurrentVersionAssociation(
        snippet=snippet,
        version=version)
    db.session.add(current_version_association)

    db.session.commit()

    flash_success('Das Snippet "{}" wurde angelegt.', snippet.name)
    return redirect_to('.view_version', id=version.id)


@blueprint.route('/snippets/<uuid:id>/update')
@permission_required(SnippetPermission.update)
@templated
def update_snippet_form(id):
    """Show form to update a snippet."""
    snippet = find_snippet_by_id(id)
    current_version = snippet.current_version

    form = SnippetUpdateForm(
        obj=current_version,
        name=snippet.name)

    return {
        'form': form,
        'snippet': snippet,
    }


@blueprint.route('/snippets/<uuid:id>', methods=['POST'])
@permission_required(SnippetPermission.update)
def update_snippet(id):
    """Update a snippet."""
    form = SnippetUpdateForm(request.form)

    snippet = find_snippet_by_id(id)

    version = SnippetVersion(
        snippet=snippet,
        creator=g.current_user,
        title=form.title.data.strip(),
        head=form.head.data.strip(),
        body=form.body.data.strip(),
        image_url_path=form.image_url_path.data.strip())
    db.session.add(version)

    snippet.current_version = version

    db.session.commit()

    flash_success('Das Snippet "{}" wurde aktualisiert.', snippet.name)
    return redirect_to('.view_version', id=version.id)


@blueprint.route('/mointpoints/for_party/<party_id>/create')
@permission_required(MountpointPermission.create)
@templated
def create_mountpoint_form(party_id):
    """Show form to create a mountpoint."""
    party = Party.query.get_or_404(party_id)

    snippets = Snippet.query.for_party(party).order_by(Snippet.name).all()
    snippet_choices = list(map(attrgetter('id', 'name'), snippets))

    form = MountpointCreateForm()
    form.snippet_id.choices = snippet_choices

    return {
        'party': party,
        'form': form,
    }


@blueprint.route('/mountpoints/for_party/<party_id>', methods=['POST'])
@permission_required(MountpointPermission.create)
def create_mountpoint(party_id):
    """Create a mountpoint."""
    party = Party.query.get_or_404(party_id)
    form = MountpointCreateForm(request.form)

    endpoint_suffix = form.endpoint_suffix.data.strip()
    url_path = form.url_path.data.strip()
    if not url_path.startswith('/'):
        abort(400, 'URL path must start with a slash.')

    snippet_id = form.snippet_id.data.strip().lower()
    snippet = find_snippet_by_id(snippet_id)

    mountpoint = Mountpoint(
        endpoint_suffix=endpoint_suffix,
        url_path=url_path,
        snippet=snippet)
    db.session.add(mountpoint)
    db.session.commit()

    flash_success('Der Mountpoint für "{}" wurde angelegt.',
                  mountpoint.url_path)
    return redirect_to('.index_for_party', party_id=party.id)


@blueprint.route('/mountpoints/<uuid:id>', methods=['DELETE'])
@permission_required(MountpointPermission.delete)
@respond_no_content_with_location
def delete_mountpoint(id):
    """Delete a mountpoint."""
    mountpoint = Mountpoint.query.get_or_404(id)

    url_path = mountpoint.url_path
    party = mountpoint.snippet.party

    db.session.delete(mountpoint)
    db.session.commit()

    flash_success('Der Mountpoint für "{}" wurde entfernt.', url_path)
    return url_for('.index_for_party', party_id=party.id)


def find_snippet_by_id(id):
    return Snippet.query.get_or_404(id)


def find_version(id):
    return SnippetVersion.query.get_or_404(id)
