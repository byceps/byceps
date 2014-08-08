# -*- coding: utf-8 -*-

"""
byceps.blueprints.contentpage_admin.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2014 Jochen Kupperschmidt
"""

from flask import abort, g, redirect, request, url_for

from ...database import db
from ...util.framework import create_blueprint, flash_success
from ...util.templating import templated

from ..authorization.decorators import permission_required
from ..authorization.registry import permission_registry
from ..contentpage.models import ContentPage, ContentPageVersion
from ..contentpage.templating import render_page

from .authorization import ContentPagePermission
from .forms import CreateForm, UpdateForm


blueprint = create_blueprint('contentpage_admin', __name__)


permission_registry.register_enum('content_page', ContentPagePermission)


@blueprint.route('/')
@permission_required(ContentPagePermission.list)
@templated
def index():
    """List pages."""
    pages = ContentPage.query.for_current_party().all()
    return {'pages': pages}


@blueprint.route('/versions/<id>')
@permission_required(ContentPagePermission.view_history)
def view_version(id):
    """Show the page with the given id."""
    version = find_version(id)
    return render_page(version)


@blueprint.route('/<id>/history')
@permission_required(ContentPagePermission.view_history)
@templated
def history(id):
    page = find_page_by_id(id)
    return {
        'page': page,
    }


@blueprint.route('/create')
@permission_required(ContentPagePermission.create)
@templated
def create_form():
    """Show form to create a page."""
    form = CreateForm()
    return {
        'form': form,
    }


@blueprint.route('/', methods=['POST'])
@permission_required(ContentPagePermission.create)
def create():
    """Create a page."""
    form = CreateForm(request.form)

    name = form.name.data.strip()
    url_path = form.url_path.data.strip()
    if not url_path.startswith('/'):
        abort(400, 'URL path must start with a slash.')

    page = ContentPage(
        name=name,
        party=g.party,
        url_path=url_path)
    db.session.add(page)

    version = ContentPageVersion(
        page=page,
        creator=g.current_user,
        title=form.title.data,
        body=form.body.data)
    db.session.add(version)

    db.session.commit()

    flash_success('Die Seite "{}" wurde angelegt.', page.name)
    return redirect(url_for('.view_version', id=version.id))


@blueprint.route('/<id>/update')
@permission_required(ContentPagePermission.update)
@templated
def update_form(id):
    """Show form to update a page."""
    page = find_page_by_id(id)
    latest_version = page.get_latest_version()

    form = UpdateForm(
        obj=page,
        title=latest_version.title,
        body=latest_version.body)

    return {
        'form': form,
        'page': page,
    }


@blueprint.route('/<id>', methods=['POST'])
@permission_required(ContentPagePermission.update)
def update(id):
    """Update a page."""
    form = UpdateForm(request.form)

    page = find_page_by_id(id)

    version = ContentPageVersion(
        page=page,
        creator=g.current_user,
        title=form.title.data,
        body=form.body.data)
    db.session.add(version)
    db.session.commit()

    flash_success('Die Seite "{}" wurde aktualisiert.', page.name)
    return redirect(url_for('.view_version', id=version.id))


def find_page_by_id(id):
    return ContentPage.query.get_or_404(id)


def find_version(id):
    return ContentPageVersion.query.get_or_404(id)
