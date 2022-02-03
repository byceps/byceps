#!/usr/bin/env python

"""Export roles and their assigned permissions as TOML to STDOUT.

:Copyright: 2006-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import click
from flask.cli import with_appcontext

from byceps.services.authorization import impex_service


@click.command()
@with_appcontext
def execute() -> None:
    print(impex_service.export())


if __name__ == '__main__':
    execute()
