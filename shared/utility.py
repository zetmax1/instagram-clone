from rest_framework.exceptions import ValidationError
import re
import threading
import phonenumbers
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from decouple import config
from twilio.rest import Client

email_regex = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
phone_regex = re.compile(r"^(\+[0-9]+\s*)?(\([0-9]+\))?[\s0-9\-]+[0-9]+")

def check_email_or_phone(email_or_phone):
    phone_number = phonenumbers.parse(email_or_phone)
    if re.fullmatch(email_regex, email_or_phone):
        email_or_phone = 'email'

    elif phonenumbers.is_valid_number(phone_number):
        email_or_phone = 'phone'

    else:
        data = {
            'success': False,
            'message': 'email or phone number was wrong entered'
        }
        raise ValidationError(data)

    return email_or_phone

class EmailThread(threading.Thread):

    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        self.email.send()

class Email:

    @staticmethod
    def send_email(data):
        email = EmailMessage(
            subject=data['subject'],
            body= data['body'],
            to= [data['to_email']]
        )

        if data.get('content_type') == 'html':
            email.content_subtype = 'html'
        EmailThread(email).start()
        
def send_email(email, code):
    html_content = render_to_string(
        'email/authentication/activate_account.html',
        {'code': code}
    )

    Email.send_email({
        'subject': 'Authentication',
        'to_email': email,
        'body': html_content,
        'content_type': 'html'
    }    
    )

def send_phone_code(phone, code):
    account_sid = config('account_sid')
    auth_token = config('auth_token')
    client = Client(account_sid, auth_token)
    client.messages.create(
        body= f'your confirmation code is {code}\n',
        from_='+998772501326', #is taken from twilio
        to=f'{phone}'
    )

