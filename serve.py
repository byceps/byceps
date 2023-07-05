"""
Create and initialize the application using a configuration specified by
an environment variable.

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""


from byceps.application import get_app_factory


app_factory = get_app_factory()
app = app_factory()
