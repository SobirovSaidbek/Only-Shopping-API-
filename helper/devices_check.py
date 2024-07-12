import threading

from decouple import config
from django.core.mail import send_mail
from twilio.rest import Client

from conf.settings import EMAIL_HOST


def send_code_email(email, code):
    def send_in_thread():
        send_mail(
            from_email=EMAIL_HOST,
            recipient_list=[email],
            subject='Will be sent Code',
            message = f'Your Code is {code}'
        )

    thread = threading.Thread(target=send_in_thread)
    thread.start()

    return True


def send_code_phone(phone_number, code):
    def send_in_thread():
        account_sid = config('TWILIO_ID')
        auth_token = config('TWILIO_KEY')
        client = Client(account_sid, auth_token)

        message = client.messages.create(
            from_='+12073877090',
            to=phone_number,
            body=f'Your Code is {code}'
        )

    thread = threading.Thread(target=send_in_thread)
    thread.start()

    return True
