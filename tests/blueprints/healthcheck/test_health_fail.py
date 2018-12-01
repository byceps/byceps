"""
:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from tests.base import AbstractAppTestCase, CONFIG_FILENAME_TEST_ADMIN


class HealthcheckFailTest(AbstractAppTestCase):

    def setUp(self):
        # Test against an admin app because that doesn't require setup
        # of brand and party.
        # After all, both admin and party apps should react the same.
        super().setUp(config_filename=CONFIG_FILENAME_TEST_ADMIN)

        self.original_database_uri = self.app.config['SQLALCHEMY_DATABASE_URI']
        self.app.config['SQLALCHEMY_DATABASE_URI'] \
            = 'postgresql+psycopg2://byceps_test:WRONG_PASSWORD@127.0.0.1/byceps_test'

    def test_healthcheck_fail(self):
        expected_media_type = 'application/health+json'

        with self.client() as client:
            response = client.get('/health')

        assert response.status_code == 503
        assert response.content_type == expected_media_type
        assert response.mimetype == expected_media_type
        assert response.get_json() == {
            'status': 'ok',
            'details': {
                'rdbms': [{'status': 'fail'}],
            },
        }

    def tearDown(self):
        # Restore working database connection for post-test clean up.
        self.app.config['SQLALCHEMY_DATABASE_URI'] = self.original_database_uri
