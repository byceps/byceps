"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import byceps.services.email.service as email_service


def test_delete_config(email_admin_client, make_brand):
    config_id = 'kann-weg'

    brand = make_brand('acme-delete', 'ACME deletion test')

    assert email_service.create_config(
        config_id, brand.id, 'noreply@acme.example'
    )
    assert email_service.find_config(config_id) is not None

    url = f'/admin/email/configs/{config_id}'
    response = email_admin_client.delete(url)

    assert email_service.find_config(config_id) is None
