"""Search in (the latest versions of) pages.

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import click

from byceps.services.page import page_service
from byceps.services.site.models import Site

from _util import call_with_app_context
from _validators import validate_site


def validate_site_if_given(ctx, param, site_id_value: str) -> Site | None:
    if site_id_value is None:
        return None

    return validate_site(ctx, param, site_id_value)


@click.command()
@click.pass_context
@click.argument('search_term')
@click.option('--site', callback=validate_site_if_given)
@click.option('-v', '--verbose', is_flag=True)
def execute(ctx, search_term, site, verbose) -> None:
    site_id = site.id if site else None

    matches = page_service.search_pages(search_term, site_id=site_id)

    if not matches:
        if verbose:
            click.secho(
                'No matching pages for '
                + (f'site ID {site_id} and ' if site_id else '')
                + f'search term "{search_term}".',
                fg='yellow',
            )
        return

    for page in matches:
        click.secho(f'{page.site_id}/{page.name}')

    if verbose:
        click.secho(
            f'\n{len(matches):d} matching page(s) for '
            + (f'site ID {site_id} and ' if site_id else '')
            + f'search term "{search_term}".',
            fg='green',
        )


if __name__ == '__main__':
    call_with_app_context(execute)
