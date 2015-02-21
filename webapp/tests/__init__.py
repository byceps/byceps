# -*- coding: utf-8 -*-

from unittest import TestCase

from byceps.application import create_app
from byceps.database import db

from testfixtures.brand import create_brand
from testfixtures.party import create_party


class AbstractAppTestCase(TestCase):

    def setUp(self, env='test'):
        self.app = create_app(env, initialize=False)

        self.db = db
        db.app = self.app

        db.drop_all()
        db.create_all()

        self.create_brand_and_party()

        self.client = self.app.test_client()

    def create_brand_and_party(self):
        self.brand = create_brand()
        db.session.add(self.brand)

        self.party = create_party(brand=self.brand)
        db.session.add(self.party)

        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def enrich_session_for_user(self, user):
        with self.client.session_transaction() as session:
            session['user_id'] = str(user.id)
            session['user_auth_token'] = str(user.auth_token)
