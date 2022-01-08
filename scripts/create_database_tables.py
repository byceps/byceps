#!/usr/bin/env python

"""Create the initial database structure.

Existing tables will be ignored, and those not existing will be created.

:Copyright: 2006-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from importlib import import_module
from itertools import chain
from pathlib import Path
from typing import Iterator

import click

import byceps
from byceps.database import db

from _util import call_with_app_context


@click.command()
def execute() -> None:
    click.echo('Creating database tables ... ', nl=False)

    _load_dbmodels()

    db.create_all()

    click.secho('done.', fg='green')


def _load_dbmodels() -> None:
    paths = _collect_dbmodel_paths()
    module_names = map(_get_module_name_for_path, paths)
    for module_name in module_names:
        import_module(module_name)


def _collect_dbmodel_paths() -> Iterator[Path]:
    package_paths = map(Path, byceps.__path__)
    for package_path in package_paths:
        services_path = Path(package_path) / 'services'

        module_paths = chain(
            services_path.glob('**/dbmodels.py'),
            services_path.glob('**/dbmodels/*.py'),
        )

        # Obtain relative paths that can be
        # transformed into package imports.
        for module_path in module_paths:
            yield module_path.relative_to(package_path.parent)


def _get_module_name_for_path(path: Path) -> str:
    path = path.with_suffix('')

    if path.stem == '__init__':
        path = path.parent

    return str(path).replace('/', '.')


if __name__ == '__main__':
    call_with_app_context(execute)
