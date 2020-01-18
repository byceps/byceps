"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""


def set_up_database(db):
    # Learn about all tables to also drop old ones no longer
    # defined in models.
    db.reflect()

    db.drop_all()

    db.create_all()


def tear_down_database(db):
    db.session.remove()
    db.drop_all()
