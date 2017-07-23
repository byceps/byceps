"""
:Copyright: 2006-2017 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from nose2.tools import params

from testfixtures.user import create_user_with_detail


@params(
    (None,          None    , None                ),
    ('Giesbert Z.', None    , 'Giesbert Z.'       ),
    (None,          'Blümli', 'Blümli'            ),
    ('Giesbert Z.', 'Blümli', 'Giesbert Z. Blümli'),
)
def test_full_name(first_names, last_name, expected):
    user = create_user_with_detail(first_names=first_names,
                                   last_name=last_name)

    assert user.detail.full_name == expected
