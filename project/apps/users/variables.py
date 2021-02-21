import os, random
from django.core.exceptions import ValidationError
import re
from difflib import SequenceMatcher
import logging
from django.core.cache import cache
from django.contrib import messages
#format used for randomly select default profile image.
image_format = '.PNG'
#total files in default profile image folder.
DEFAULT_IMAGE_COUNT = len([file for file in os.scandir('media/default_pics') 
	if file.path.endswith(image_format)])
#maximum length of a user's profile bio field.
MAX_BIO_LENGTH = 150

FIELD_NAME_MAPPING = {
    'username': 'public_id',
    'email': 'username'
    }
#generate random file name from MEDIA_ROOT/default_pics
def random_image():
	return f'default_pics/default_\
{random.choice(range(1, DEFAULT_IMAGE_COUNT + 1))}{image_format}'
#expiration function
import datetime
def expires(days):
	expiration = datetime.datetime.strftime(datetime.datetime.now() + 
	datetime.timedelta(days=days), "%Y-%m-%d %H:%M:%S")
	return expiration
#check password against top 1000 used passwords
from django.contrib.staticfiles.storage import staticfiles_storage

def check_password_commonality(password):
		if password is not None:
			import os
			import gzip
			password_list_path = staticfiles_storage.path('users/files/common-passwords.txt.gz') 
			try:
				with gzip.open(password_list_path) as f:
					common_passwords_lines = f.read().decode().splitlines()
			except IOError:
				with open(password_list_path) as f:
					common_passwords_lines = f.readlines()
			passwords = {p.strip() for p in common_passwords_lines}
			if password.lower().strip() in passwords:
				return True
		return False
def check_profanity(string):
	if string is not None:
		import os
		import gzip
		profanity_list = staticfiles_storage.path('users/files/list.txt')
		try:
			with gzip.open(profanity_list) as f:
				profanity_lines = f.read().decode().splitlines()
		except IOError:
			with open(profanity_list) as f:
				profanity_lines = f.read().splitlines()
		profanity = {p for p in profanity_lines}
		words = string.split()
		for word in words:
			for bad_word in profanity:
				if bad_word in word:
					return True
	return False
# return true if password is all digits
def check_password_alpha(password):
	if password != None:
		return password.isdigit()
	return False
# check if email input meets Django's default validation
def check_email(email):
	from django.core.validators import validate_email
	try:
		validate_email(email)
		email_valid = True
	except ValidationError:
		email_valid = False
	return email_valid
# check if username input meets Django's default validation
def check_username(username):
	if username != None and len(username) != 0:
		allowed = "_"
		return all(c in allowed or c.isalpha() or c.isdigit() for c in username)
	return False
#check if password input is too similar to personal information
def check_password_similarity(password, username, email):
		password_too_similar = False
		if password != None:
			ATTRIBUTES = (username, email)
			for attribute in ATTRIBUTES:
				if not attribute:
					continue
				attribute_parts = re.split(r'\W+', attribute) + [attribute]
				for part in attribute_parts:
					if SequenceMatcher(a=password.lower(), 
						b=part.lower()).quick_ratio() >= .7:
						password_too_similar = True
		return password_too_similar
logger = logging.getLogger(__name__)
class InvalidLoginAttemptsCache(object):
    @staticmethod
    def _key(username):
        return 'invalid_login_attempt_{}'.format(username)

    @staticmethod
    def _value(lockout_timestamp, timebucket):
        return {
            'lockout_start': lockout_timestamp,
            'invalid_attempt_timestamps': timebucket
        }

    @staticmethod
    def delete(username):
        try:
            cache.delete(InvalidLoginAttemptsCache._key(username))
        except Exception as e:
            logger.exception(e.message)
            messages.success(request, str(logger.exception(e.message)))

    @staticmethod
    def set(username, timebucket, lockout_timestamp=None):
        try:
            key = InvalidLoginAttemptsCache._key(username)
            value = InvalidLoginAttemptsCache._value(lockout_timestamp, timebucket)
            cache.set(key, value)
        except Exception as e:
            logger.exception(e.message)
            messages.success(request, str(logger.exception(e.message)))

    @staticmethod
    def get(username):
        try:
            key = InvalidLoginAttemptsCache._key(username)
            return cache.get(key)
        except Exception as e:
            logger.exception(e.message)
            messages.success(request, str(logger.exception(e.message)))

def data_password(password, data):
	if password != None and not data.get('password_null', False):
		if not data.get('password_length', True):
			data['password_error'] = "8 or more characters, please."
		elif data.get('password_no_alpha', False):
			data['password_error'] = "Please don't use all digits."
		elif data.get('password_too_similar', False):
			data['password_error'] = 'Password is too similar to personal info.'
		elif data.get('password_too_common', False):
			data['password_error'] = 'Password is too common. Be strong, please.'
		else: 
			data['password_pass'] = True
	return data

def data_username(username, data):
	if username != None and not data.get('username_null', False):
		if not data.get('username_length', True) or not re.search('[A-Za-z]', username):
			data['username_error'] = "At least 3 characters and 1 letter, please."
		elif not data.get('username_valid', True):
			data['username_error'] = 'Only letters, digits, and underscores, please.'
		elif data.get('username_taken', False):
			data['username_error'] = 'Username is taken.'
		elif data.get('username_profane', False):
			data['username_error'] = "No profanity, please."
		else:
			data['username_pass'] = True
	return data

def data_email(email, data):
	if email != None and not data.get('email_null', False):
		if not data.get('email_valid', True):
			data['email_error'] = "Enter a valid email, please."
		else:
			data['email_pass'] = True
	return data