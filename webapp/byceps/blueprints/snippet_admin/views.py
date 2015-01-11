# -*- coding: utf-8 -*-

"""
byceps.blueprints.snippet_admin.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2014 Jochen Kupperschmidt
"""

from operator import attrgetter

from flask import abort, g, request, url_for

from ...database import db
from ...util.framework import create_blueprint, flash_success
from ...util.templating import templated
from ...util.views import redirect_to, respond_no_content_with_location

from ..authorization.decorators import permission_required
from ..authorization.registry import permission_registry
from ..party.models import Party
from ..snippet.models import Mountpoint, Snippet, SnippetVersion
from ..snippet.templating import render_snippet_as_page

from .authorization import MountpointPermission, SnippetPermission
from .forms import MountpointCreateForm, MountpointUpdateForm, \
    SnippetCreateForm, SnippetUpdateForm


blueprint = create_blueprint('snippet_admin', __name__)


permission_registry.register_enum(MountpointPermission)
permission_registry.register_enum(SnippetPermission)


@blueprint.route('/')
@permission_required(SnippetPermission.list)
@templated
def index():
    """List parties to choose from."""
    parties = Party.query.all()
    return {'parties': parties}


@blueprint.route('/<party_id>')
@permission_required(SnippetPermission.list)
@templated
def index_for_party(party_id):
    """List snippets for that party."""
    party = Party.query.get_or_404(party_id)
    snippets = Snippet.query.for_party(party).all()
    mountpoints = Mountpoint.query.for_party(party).all()
    return {
        'party': party,
        'snippets': snippets,
        'mountpoints': mountpoints,
    }


@blueprint.route('/versions/<id>')
@permission_required(SnippetPermission.view_history)
def view_version(id):
    """Show the snippet with the given id."""
    version = find_version(id)
    return render_snippet_as_page(version)


@blueprint.route('/<id>/history')
@permission_required(SnippetPermission.view_history)
@templated
def history(id):
    snippet = find_snippet_by_id(id)
    return {
        'snippet': snippet,
        'versions': snippet.get_versions(),
        'latest_version': snippet.get_latest_version(),
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
        body=form.body.data.strip())
    db.session.add(version)

    db.session.commit()

    flash_success('Das Snippet "{}" wurde angelegt.', snippet.name)
    return redirect_to('.view_version', id=version.id)


@blueprint.route('/snippets/<id>/update')
@permission_required(SnippetPermission.update)
@templated
def update_snippet_form(id):
    """Show form to update a snippet."""
    snippet = find_snippet_by_id(id)
    latest_version = snippet.get_latest_version()

    form = SnippetUpdateForm(
        obj=latest_version,
        name=latest_version.snippet.name)

    return {
        'form': form,
        'snippet': latest_version.snippet,
    }


@blueprint.route('/snippets/<id>', methods=['POST'])
@permission_required(SnippetPermission.update)
def update_snippet(id):
    """Update a snippet."""
    form = SnippetUpdateForm(request.form)

    snippet = find_snippet_by_id(id)

    version = SnippetVersion(
        snippet=snippet,
        creator=g.current_user,
        title=form.title.data.strip(),
        body=form.body.data.strip())
    db.session.add(version)
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


@blueprint.route('/mountpoints/<id>', methods=['DELETE'])
@permission_required(MountpointPermission.delete)
@respond_no_content_with_location
def delete_mountpoint(id):
    """Delete a mountpoint."""
    mountpoint = Mountpoint.query.get_or_404(id)

    url_path = mountpoint.url_path
    party = mountpoint.snippet.party

    db.session.delete(mountpoint)
    db.session.commit()

    flash_success('Der Mountpoint für "{}" wurde entfernt.'.format(url_path))
    return url_for('.index_for_party', party_id=party.id)


def find_snippet_by_id(id):
    return Snippet.query.get_or_404(id)


def find_version(id):
    return SnippetVersion.query.get_or_404(id)
