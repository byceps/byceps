"""Search in (the latest versions of) snippets.

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import click

from byceps.services.site.models import Site
from byceps.services.snippet import snippet_service
from byceps.services.snippet.models import SnippetScope

from _util import call_with_app_context
from _validators import validate_site


def validate_site_if_given(ctx, param, site_id_value: str) -> Site:
    if site_id_value is None:
        return None

    return validate_site(ctx, param, site_id_value)


@click.command()
@click.pass_context
@click.argument('search_term')
@click.option('--site', callback=validate_site_if_given)
@click.option('-v', '--verbose', is_flag=True)
def execute(ctx, search_term, site, verbose) -> None:
    scope = None
    if site is not None:
        scope = SnippetScope.for_site(site.id)

    scope_label = get_scope_label(verbose, scope)

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
        click.secho(f'{format_scope(snippet.scope)}\t{snippet.name}')

    if verbose:
        click.secho(
            f'\n{len(matches):d} matching snippet(s) '
            f'for {scope_label} and search term "{search_term}".',
            fg='green',
        )


def get_scope_label(verbose: bool, scope: SnippetScope | None) -> str:
    if not verbose:
        return '<unknown>'

    if scope is None:
        return 'any scope'

    return f'scope "{format_scope(scope)}"'


def format_scope(scope: SnippetScope) -> str:
    return f'{scope.type_}/{scope.name}'


if __name__ == '__main__':
    call_with_app_context(execute)
