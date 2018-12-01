"""
:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from tests.base import AbstractAppTestCase, CONFIG_FILENAME_TEST_ADMIN


class HealthcheckTest(AbstractAppTestCase):

    def setUp(self):
        # Test against an admin app because that doesn't require setup
        # of brand and party.
        # After all, both admin and party apps should react the same.
        super().setUp(config_filename=CONFIG_FILENAME_TEST_ADMIN)

    def test_healthcheck_endpoint(self):
        expected_media_type = 'application/health+json'

        with self.client() as client:
            response = client.get('/health')

        assert response.status_code == 200
        assert response.content_type == expected_media_type
        assert response.mimetype == expected_media_type
        assert response.get_json() == {
            'status': 'ok',
        }
