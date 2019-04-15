"""
:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from unittest.mock import patch

from tests.base import AbstractAppTestCase, CONFIG_FILENAME_TEST_ADMIN


class HealthcheckFailTest(AbstractAppTestCase):

    def setUp(self):
        # Test against an admin app because that doesn't require setup
        # of brand and party.
        # After all, both admin and party apps should react the same.
        super().setUp(config_filename=CONFIG_FILENAME_TEST_ADMIN)

    @patch('byceps.blueprints.healthcheck.views._is_rdbms_ok')
    def test_healthcheck_fail(self, is_rdbms_ok_mock):
        expected_media_type = 'application/health+json'

        is_rdbms_ok_mock.return_value = False

        with self.client() as client:
            response = client.get('/health')

        assert response.status_code == 503
        assert response.content_type == expected_media_type
        assert response.mimetype == expected_media_type
        assert response.json == {
            'status': 'ok',
            'details': {
                'rdbms': [{'status': 'fail'}],
            },
        }
