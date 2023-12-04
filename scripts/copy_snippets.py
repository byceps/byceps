#!/usr/bin/env python

"""Copy a snippet (in its latest version) from one site to another.

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import click

from byceps.services.snippet import snippet_service
from byceps.services.snippet.models import SnippetScope
from byceps.services.user import user_service

from _util import call_with_app_context
from _validators import validate_site


@click.command()
@click.pass_context
@click.argument('source_site', callback=validate_site)
@click.argument('target_site', callback=validate_site)
@click.argument('language_code')
@click.argument('snippet_names', nargs=-1, required=True)
def execute(
    ctx, source_site, target_site, language_code: str, snippet_names
) -> None:
    source_scope = SnippetScope.for_site(source_site.id)
    target_scope = SnippetScope.for_site(target_site.id)

    for name in snippet_names:
        copy_snippet(source_scope, target_scope, name, language_code, ctx)

    click.secho('Done.', fg='green')


def copy_snippet(
    source_scope: SnippetScope,
    target_scope: SnippetScope,
    name: str,
    language_code: str,
    ctx,
) -> None:
    version = snippet_service.find_current_version_of_snippet_with_name(
        source_scope, name, language_code
    )
    if version is None:
        click.secho(
            f'Snippet "{name}" ({language_code}) '
            f'not found in scope "{scope_as_string(source_scope)}".',
            fg='red',
        )
        return None

    creator = user_service.get_user(version.creator_id)

    snippet_service.create_snippet(
        target_scope,
        version.snippet.name,
        version.snippet.language_code,
        creator,
        version.body,
    )

    click.secho(
        f'Copied snippet "{version.snippet.name}" ({language_code}) '
        f'to scope "{scope_as_string(target_scope)}".',
        fg='green',
    )


def scope_as_string(scope: SnippetScope) -> str:
    return f'{scope.type_}/{scope.name}'


if __name__ == '__main__':
    call_with_app_context(execute)
