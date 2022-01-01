#!/usr/bin/env python

"""Export roles and their assigned permissions as TOML to STDOUT.

:Copyright: 2006-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import click

from byceps.services.authorization import impex_service

from _util import call_with_app_context


@click.command()
def execute() -> None:
    print(impex_service.export())


if __name__ == '__main__':
    call_with_app_context(execute)
