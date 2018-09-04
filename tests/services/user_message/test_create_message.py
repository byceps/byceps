"""
:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.services.user_message import service

from tests.base import AbstractAppTestCase


class CreateUserMessageTest(AbstractAppTestCase):

    def setUp(self):
        super().setUp()

        self.create_brand_and_party()

        self.set_brand_email_sender_address(self.brand.id, 'orga@example.com')

    def test_create_message(self):
        sender = self.create_user('Alice', email_address='alice@example.com')
        recipient = self.create_user('Bob', email_address='bob@example.com')
        text = '''\
Hi Bob,

please don't forget to take out the trash.

kthxbye,
Alice
'''

        with self.app.app_context():
            message = service.create_message(sender.id, recipient.id, text,
                                             self.brand.id)

        assert message.sender == 'orga@example.com'
        assert message.recipients == ['bob@example.com']
        assert message.subject == 'Mitteilung von Alice'
        assert message.body == '''\
Hallo Bob,

Alice möchte dir folgende Mitteilung zukommen lassen:

---8<-------------------------------------

Hi Bob,

please don't forget to take out the trash.

kthxbye,
Alice

---8<-------------------------------------

-- 
Diese Mitteilung wurde über die Website der Acme Entertainment Convention gesendet.\
'''
