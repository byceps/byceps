#!/usr/bin/env python

"""Search in (the latest versions of) snippets.

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import click

from byceps.services.snippet import service as snippet_service
from byceps.services.snippet.transfer.models import Scope
from byceps.util.system import get_config_filename_from_env_or_exit

from bootstrap.util import app_context
from bootstrap.validators import validate_site


@click.command()
@click.pass_context
@click.argument('search_term')
@click.argument('site', callback=validate_site)
@click.option('-v', '--verbose', is_flag=True)
def execute(ctx, search_term, site, verbose):
    scope = Scope.for_site(site.id)

    matches = snippet_service.search_snippets(search_term, scope)

    if not matches:
        if verbose:
            click.secho(
                'No matching snippets for site "{}" and search term "{}".'
                    .format(site.id, search_term),
                fg='yellow')
        return

    for version in matches:
        click.secho(version.snippet.name)

    if verbose:
        click.secho(
            '\n{:d} matching snippet(s) for site "{}" and search term "{}".'
                .format(len(matches), site.id, search_term),
            fg='green')


if __name__ == '__main__':
    config_filename = get_config_filename_from_env_or_exit()
    with app_context(config_filename):
        execute()
