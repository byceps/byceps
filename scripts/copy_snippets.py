#!/usr/bin/env python

"""Copy a snippet (in its latest version) from one site to another.

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import click

from byceps.services.snippet.dbmodels import DbSnippetVersion
from byceps.services.snippet.models import Scope
from byceps.services.snippet import snippet_service

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
    source_scope = Scope.for_site(source_site.id)
    target_scope = Scope.for_site(target_site.id)

    versions = [
        get_version(source_scope, name, language_code) for name in snippet_names
    ]

    for version in versions:
        copy_snippet(target_scope, version, ctx)

    click.secho('Done.', fg='green')


def get_version(
    source_scope: Scope, snippet_name: str, language_code: str
) -> DbSnippetVersion:
    version = snippet_service.find_current_version_of_snippet_with_name(
        source_scope, snippet_name, language_code
    )

    if version is None:
        raise click.BadParameter(
            f'Snippet "{snippet_name}" with language code "{language_code}" '
            f'not found in scope "{scope_as_string(source_scope)}".'
        )

    return version


def copy_snippet(target_scope: Scope, version: DbSnippetVersion, ctx) -> None:
    snippet_service.create_snippet(
        target_scope,
        version.snippet.name,
        version.snippet.language_code,
        version.creator_id,
        version.body,
    )

    click.secho(
        f'Copied snippet "{version.snippet.name}" '
        f'to scope "{scope_as_string(target_scope)}".',
        fg='green',
    )


def scope_as_string(scope: Scope) -> str:
    return f'{scope.type_}/{scope.name}'


if __name__ == '__main__':
    call_with_app_context(execute)
