"""
Create and initialize the application using a configuration specified by
an environment variable.

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from byceps.application import create_app


app = create_app()
