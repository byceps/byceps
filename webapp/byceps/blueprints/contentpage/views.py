# -*- coding: utf-8 -*-

"""
byceps.blueprints.contentpage.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2014 Jochen Kupperschmidt
"""

import sys
import traceback
import warnings

from flask import abort, g, redirect, render_template, request, url_for
from jinja2 import FunctionLoader, TemplateNotFound
from jinja2.sandbox import ImmutableSandboxedEnvironment

from ...database import db
from ...util.framework import create_blueprint, flash_error, flash_success
from ...util.templating import templated

from .forms import CreateForm, UpdateForm
from .models import ContentPage, ContentPageVersion


blueprint = create_blueprint('contentpage', __name__)


def add_routes_for_pages(app):
    """Register routes for pages with the application."""
    blueprint_name = 'contentpage'
    pages = ContentPage.query.all()
    for page in pages:
        endpoint = '{}.{}'.format(blueprint_name, page.name)
        view_func = view_latest_by_name
        defaults = {'name': page.name}
        app.add_url_rule(page.url, endpoint, view_func, defaults=defaults)


@blueprint.route('/')
@templated
def index():
    """List pages."""
    pages = ContentPage.query.all()
    return {'pages': pages}


def view_latest_by_name(name):
    """Show the latest version of the page with the given name."""
    try:
        template = _create_env(load_func=_load_template_by_name).get_template(name)
        title, current_page = _extract_metadata(name, template)
        body = template.render()
        context = {
            'title': title,
            'current_page': current_page,
            'body': body,
        }
        return render_template('contentpage/view.html', **context)
    except TemplateNotFound:
        abort(404)
    except Exception as e:
        print('Error in content page markup:', e, file=sys.stderr)
        traceback.print_exc()
        context = {
            'message': str(e),
        }
        return render_template('contentpage/error.html', **context), 500


@blueprint.route('/versions/<id>')
def view_version(id):
    """Show the page with the given id."""
    try:
        template = _create_env(load_func=_load_template_by_version).get_template(id)
        title, current_page = _extract_metadata(id, template)
        body = template.render()
        context = {
            'title': title,
            'current_page': current_page,
            'body': body,
        }
        return render_template('contentpage/view.html', **context)
    except TemplateNotFound:
        abort(404)
    except Exception as e:
        print('Error in content page markup:', e, file=sys.stderr)
        traceback.print_exc()
        context = {
            'message': str(e),
        }
        return render_template('contentpage/error.html', **context), 500


def _create_env(load_func):
    loader = FunctionLoader(load_func)
    env = ImmutableSandboxedEnvironment(
        loader=loader,
        autoescape=True,
        trim_blocks=True)

    env.globals['url_for'] = url_for

    return env


def _load_template_by_name(name):
    page = find_page(name)
    return page.get_latest_version().body


def _load_template_by_version(id):
    version = ContentPageVersion.query.get_or_404(id)
    return version.body


def _extract_metadata(id, template):
    try:
        title = template.module.title
        current_page = template.module.current_page
    except AttributeError:
        warnings.warn(
            'No title and/or current page set for page "{}".'.format(id))
        title = ''
        current_page = None
    return title, current_page


@blueprint.route('/<name>/history')
@templated
def history(name):
    page = find_page(name)
    versions = page.get_versions()

    return {
        'name': page.name,
        'url': page.url,
        'versions': versions,
    }


@blueprint.route('/create')
@templated
def create_form():
    """Show form to create a page."""
    form = CreateForm()
    return {
        'form': form,
    }


@blueprint.route('/', methods=['POST'])
def create():
    """Create a page."""
    form = CreateForm(request.form)

    name = form.name.data.strip()
    url = form.url.data.strip()
    if not url.startswith('/'):
        abort(400, 'URL path must start with a slash.')

    page = ContentPage(
        name=name,
        url=url)
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


@blueprint.route('/<name>/update')
@templated
def update_form(name):
    """Show form to update a page."""
    page = find_page(name)
    latest_version = page.get_latest_version()

    form = UpdateForm(
        obj=page,
        title=latest_version.title,
        body=latest_version.body)

    return {
        'form': form,
        'page': page,
    }


@blueprint.route('/<name>', methods=['POST'])
def update(name):
    """Update a page."""
    form = UpdateForm(request.form)

    page = find_page(name)

    version = ContentPageVersion(
        page=page,
        creator=g.current_user,
        title=form.title.data,
        body=form.body.data)
    db.session.add(version)
    db.session.commit()

    flash_success('Die Seite "{}" wurde aktualisiert.', page.name)
    return redirect(url_for('.view_version', id=version.id))


def find_page(name):
    return ContentPage.query.get_or_404(name)
