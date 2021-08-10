#!/usr/bin/env python

"""Copy a snippet (in its latest version) from one site to another.

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import click

from byceps.services.snippet.dbmodels.snippet import SnippetVersion
from byceps.services.snippet import service as snippet_service
from byceps.services.snippet.transfer.models import Scope, SnippetType

from _util import call_with_app_context
from _validators import validate_site


@click.command()
@click.pass_context
@click.argument('source_site', callback=validate_site)
@click.argument('target_site', callback=validate_site)
@click.argument('snippet_names', nargs=-1, required=True)
def execute(ctx, source_site, target_site, snippet_names) -> None:
    source_scope = Scope.for_site(source_site.id)
    target_scope = Scope.for_site(target_site.id)

    snippet_versions = [
        get_snippet_version(source_scope, name) for name in snippet_names
    ]

    for snippet_version in snippet_versions:
        copy_snippet(target_scope, snippet_version, ctx)

    click.secho('Done.', fg='green')


def get_snippet_version(source_scope: Scope, snippet_name: str) -> SnippetVersion:
    snippet_version = snippet_service.find_current_version_of_snippet_with_name(
        source_scope, snippet_name
    )

    if snippet_version is None:
        raise click.BadParameter(
            f'Snippet "{snippet_name}" not found '
            f'in scope "{scope_as_string(source_scope)}".'
        )

    return snippet_version


def copy_snippet(target_scope: Scope, snippet_version: SnippetVersion, ctx) -> None:
    snippet_type = snippet_version.snippet.type_

    if snippet_type == SnippetType.document:
        create_document(target_scope, snippet_version)
    elif snippet_type == SnippetType.fragment:
        create_fragment(target_scope, snippet_version)
    else:
        ctx.fail(f"Unknown snippet type '{snippet_type}'.")

    click.secho(
        f'Copied snippet "{snippet_version.snippet.name}" '
        f'to scope "{scope_as_string(target_scope)}".',
        fg='green',
    )


def create_document(target_scope: Scope, snippet_version: SnippetVersion) -> None:
    snippet_service.create_document(
        target_scope,
        snippet_version.snippet.name,
        snippet_version.creator_id,
        snippet_version.title,
        snippet_version.body,
        head=snippet_version.head,
        image_url_path=snippet_version.image_url_path,
    )


def create_fragment(target_scope: Scope, snippet_version: SnippetVersion) -> None:
    snippet_service.create_fragment(
        target_scope,
        snippet_version.snippet.name,
        snippet_version.creator_id,
        snippet_version.body,
    )


def scope_as_string(scope: Scope) -> str:
    return f'{scope.type_}/{scope.name}'


if __name__ == '__main__':
    call_with_app_context(execute)
