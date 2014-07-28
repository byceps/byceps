# -*- coding: utf-8 -*-

"""
byceps.blueprints.contentpage.templating
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2014 Jochen Kupperschmidt
"""

import sys
import traceback
import warnings

from flask import abort, render_template, url_for
from jinja2 import FunctionLoader, TemplateNotFound
from jinja2.sandbox import ImmutableSandboxedEnvironment

from .models import ContentPage


def render_page(page):
    """Render the page, or an error page if that fails."""
    try:
        context = get_page_context(page)
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


def get_page_context(page):
    """Return the page context to insert into the outer template."""
    template = create_env().get_template(page.name)

    current_page = extract_variable(template, 'current_page')
    title = page.get_latest_version().title
    body = template.render()

    return {
        'title': title,
        'current_page': current_page,
        'body': body,
    }


def create_env():
    """Create a sandboxed environment that uses the given function to
    load templates.
    """
    loader = FunctionLoader(load_template)
    env = ImmutableSandboxedEnvironment(
        loader=loader,
        autoescape=True,
        trim_blocks=True)

    env.globals['url_for'] = url_for

    return env


def load_template(name):
    """Return the body of the page's latest version."""
    page = ContentPage.query.get_or_404(name)
    return page.get_latest_version().body


def extract_variable(template, name):
    """Try to extract a variable's value from the template, or return
    `None` if the variable is not defined.
    """
    try:
        return getattr(template.module, name)
    except AttributeError:
        return None
