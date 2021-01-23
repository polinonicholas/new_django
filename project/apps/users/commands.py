from django.core import management

#send queued emails with django-mailer.
def email_now():
	management.call_command('send_mail')