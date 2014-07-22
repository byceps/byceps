# -*- coding: utf-8 -*-

"""
byceps.blueprints.contentpage.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2014 Jochen Kupperschmidt
"""

import sys
import warnings

from flask import abort, g, redirect, render_template, request, url_for
from jinja2 import FunctionLoader, TemplateNotFound
from jinja2.sandbox import ImmutableSandboxedEnvironment

from ...database import db
from ...util.framework import create_blueprint, flash_error, flash_success, \
    get_blueprint_views_module
from ...util.templating import templated

from .forms import CreateForm, UpdateForm
from .models import ContentPage


blueprint = create_blueprint('contentpage', __name__)


@blueprint.route('/')
@templated
def index():
    """List pages."""
    pages = ContentPage.query.all()
    return {'pages': pages}


def add_urls_for_pages():
    blueprint_name = 'contentpage'
    pages = ContentPage.query.all()
    for page in pages:
        # Copy the value into the closure.
        views_module = get_blueprint_views_module(blueprint_name)
        view_func = getattr(views_module, 'view')
        #view_func = lambda endpoint=endpoint: view(page.name)
        endpoint = '{}.{}'.format(blueprint_name, page.name)
        app.add_url_rule(page.url, endpoint=endpoint, view_func=view_func)


@blueprint.route('/<id>')
def view(id):
    """Show the page."""
    try:
        template = _create_env().get_template(id)
        title, current_page = _extract_metadata(template)
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
        context = {
            'message': str(e),
        }
        return render_template('contentpage/error.html', **context), 500


def _create_env():
    env = ImmutableSandboxedEnvironment(
        loader=_loader,
        autoescape=True,
        trim_blocks=True)

    env.globals['url_for'] = url_for

    return env


def _load_template(name):
    content_page = _fetch_latest_content_page(name)
    if content_page is None:
        return None
    return content_page.body


_loader = FunctionLoader(_load_template)


def _fetch_latest_content_page(id):
    return ContentPage.query \
        .filter_by(id=id) \
        .order_by(ContentPage.created_at.desc()) \
        .first()


def _extract_metadata(template):
    try:
        title = template.module.title
        current_page = template.module.current_page
    except AttributeError:
        warnings.warn(
            'No title and/or current page set for page "{}".'.format(id))
        title = ''
        current_page = None
    return title, current_page


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

    page = ContentPage(
        creator=g.current_user,
        name=form.name.data,
        url=form.url.data,
        body=form.body.data)
    db.session.add(page)
    db.session.commit()

    flash_success('Die Seite "{}" wurden angelegt.', page.name)
    return redirect(url_for('.index'))


@blueprint.route('/<id>/update')
@templated
def update_form(id):
    """Show form to update a page."""
    page = find_page(id)
    form = UpdateForm(obj=page)
    return {
        'form': form,
        'page': page,
    }


@blueprint.route('/<id>', methods=['POST'])
def update(id):
    """Update a page."""
    page = find_page(id)

    form = UpdateForm(request.form)
    page.body = form.body.data
    db.session.commit()

    flash_success('Die Seite "{}" wurden aktualisiert.', page.name)
    return redirect(url_for('.view', id=page.id))


def find_page(id):
    return ContentPage.query.filter_by(id=id).first_or_404()
