#!/usr/bin/env python

"""Search in (the latest versions of) snippets.

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import click

from byceps.services.snippet import service as snippet_service
from byceps.services.snippet.transfer.models import Scope
from byceps.util.system import get_config_filename_from_env_or_exit

from _util import app_context
from _validators import validate_site


def validate_site_if_given(ctx, param, value):
    if value is None:
        return None

    return validate_site(ctx, param, value)


@click.command()
@click.pass_context
@click.argument('search_term')
@click.option('--site', callback=validate_site_if_given)
@click.option('-v', '--verbose', is_flag=True)
def execute(ctx, search_term, site, verbose):
    scope = None
    if site is not None:
        scope = Scope.for_site(site.id)

    if verbose:
        if scope is not None:
            scope_label = 'scope "{}"'.format(format_scope(scope))
        else:
            scope_label = 'any scope'
    else:
        scope_label = '<unknown>'

    matches = snippet_service.search_snippets(search_term, scope=scope)

    if not matches:
        if verbose:
            click.secho(
                f'No matching snippets for {scope_label} '
                f'and search term "{search_term}".',
                fg='yellow',
            )
        return

    for version in matches:
        snippet = version.snippet
        click.secho('{}\t{}'.format(format_scope(snippet.scope), snippet.name))

    if verbose:
        click.secho(
            '\n{:d} matching snippet(s) for {} and search term "{}".'.format(
                len(matches), scope_label, search_term
            ),
            fg='green',
        )


def format_scope(scope):
    return f'{scope.type_}/{scope.name}'


if __name__ == '__main__':
    config_filename = get_config_filename_from_env_or_exit()
    with app_context(config_filename):
        execute()
