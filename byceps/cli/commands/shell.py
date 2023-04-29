"""
byceps.cli.command.shell
~~~~~~~~~~~~~~~~~~~~~~~~

Run an interactive Python shell in the context of the BYCEPS application.

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from platform import python_version

import bpython
import click
from flask import current_app
from flask.cli import with_appcontext


@click.command()
@with_appcontext
def shell() -> None:
    """Run interactive Python shell."""
    ctx = current_app.make_shell_context()
    banner = (
        f'Welcome to the interactive BYCEPS shell on Python {python_version()}!'
    )

    bpython.embed(locals_=ctx, banner=banner)
