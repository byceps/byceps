"""
:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.services.brand import service as brand_service
from byceps.services.user_message import service as user_message_service

from tests.base import AbstractAppTestCase


class CreateUserMessageTest(AbstractAppTestCase):

    def setUp(self):
        super().setUp()

        self.create_brand_and_party()

        self.set_brand_email_sender_address(self.brand.id, 'noreply@example.com')

        self.user_alice = self.create_user('Alice', email_address='alice@example.com')
        self.user_bob = self.create_user('Bob', email_address='bob@example.com')

    def test_create_message_without_brand_contact_address(self):
        sender = self.user_alice
        recipient = self.user_bob
        text = '''\
Hi Bob,

please don't forget to take out the trash.

kthxbye,
Alice
'''
        sender_contact_url = 'https://www.example.com/user_messages/to/user-id-of-{}/create' \
            .format(sender.screen_name)

        with self.app.app_context():
            message = user_message_service.create_message(sender.id,
                                                          recipient.id, text,
                                                          sender_contact_url,
                                                          self.brand.id)

        assert message.sender == 'noreply@example.com'
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

Du kannst Alice hier antworten: https://www.example.com/user_messages/to/user-id-of-Alice/create

-- 
Diese Mitteilung wurde über die Website der Acme Entertainment Convention gesendet.\
'''

    def test_create_message_with_brand_contact_address(self):
        brand_service.create_setting(self.brand.id, 'contact_email_address',
                                     'info@example.com')

        sender = self.user_bob
        recipient = self.user_alice
        text = '''\
Hey Alice,

nice to hear from you.

Best,
Bob
'''
        sender_contact_url = 'https://www.example.com/user_messages/to/user-id-of-Bob/create' \
            .format(sender.screen_name)

        with self.app.app_context():
            message = user_message_service.create_message(sender.id,
                                                          recipient.id, text,
                                                          sender_contact_url,
                                                          self.brand.id)

        assert message.sender == 'noreply@example.com'
        assert message.recipients == ['alice@example.com']
        assert message.subject == 'Mitteilung von Bob'
        assert message.body == '''\
Hallo Alice,

Bob möchte dir folgende Mitteilung zukommen lassen:

---8<-------------------------------------

Hey Alice,

nice to hear from you.

Best,
Bob

---8<-------------------------------------

Du kannst Bob hier antworten: https://www.example.com/user_messages/to/user-id-of-Bob/create

-- 
Diese Mitteilung wurde über die Website der Acme Entertainment Convention gesendet.
Bei Fragen konktaktiere uns bitte per E-Mail an: info@example.com\
'''
