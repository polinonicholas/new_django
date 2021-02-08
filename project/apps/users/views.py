from django.shortcuts import redirect, render
from django.contrib import messages
from . forms import (UserRegisterForm, UserUpdateForm, UserFileForm, 
	Email_Login, RequestPassReset, NewPasswordForm, ChangePasswordForm)
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.decorators import login_required
import requests, json
from django.conf import settings
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.core.mail import send_mail
import mailer
from django.http import HttpResponse, JsonResponse
from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings
from project.customized_classes import DivErrorList
from . variables import (expires, check_profanity, check_password_alpha, 
check_password_similarity, check_email, check_username, check_password_commonality)
from django.views.decorators.cache import never_cache
from django.contrib.auth.views import (LoginView, PasswordResetView, 
	PasswordResetConfirmView,PasswordResetCompleteView)
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.utils.crypto import get_random_string
from django.contrib.auth import update_session_auth_hash
import re
UserModel = get_user_model()


# all_success_messages = [msg.message for msg in list(messages.get_messages(request)) if msg.level_tag == 'success']
# if len(all_success_messages) == 0
#      messages.add_message(request, messages.WARNING, 'testing')





@never_cache
def register(request):
	if request.user.is_authenticated:

		messages.success(request, f"You are logged in as '{request.user.username}'.")
		return redirect('/')
	if request.method == 'POST':
		# grecaptcha v2/v3
		form = UserRegisterForm(request.POST, error_class=DivErrorList)
		token = request.POST.get('g-recaptcha-response')
		url = 'https://www.google.com/recaptcha/api/siteverify'
		secret_v3 = settings.RECAPTCHA_PRIVATE_KEY_V3
		secret_v2 = settings.RECAPTCHA_PRIVATE_KEY_V2
		data_v3 = {"secret": secret_v3, "response": token}
		data_v2 = {"secret": secret_v2, "response": token}
		response_v3 = requests.post(url, data=data_v3).json()
		response_v2 = requests.post(url, data=data_v2).json()
		recaptcha_pass = False
		#check for v3 score, then check if > .9
		score = response_v3.get("score", None)
		if score != None:
			if score >=.9:
				recaptcha_pass = True
			elif score < .9:
				form.add_error(None, "You did not pass Google's reCAPTCHA v3, \
					please complete registration using v2 checkbox.")
		#else load v2 via jquery, blank form and check for v2 success
		else:
			if response_v2['success'] == True:
				recaptcha_pass = True
			elif response_v2['success'] != True:				
				form.add_error(None, "You did not pass Google's reCAPTCHA v3, \
					please complete registration using v2 checkbox.")
		# save user as inactive, then send activation email. Convert UN to lower.
		if not form.is_valid():
			form.add_error('password1', 'Re-enter a strong password, please.')
		if form.is_valid() and recaptcha_pass:
			user = form.save(commit=False)
			user.is_active = False
			user.save()
			current_site = get_current_site(request)
			mail_subject = 'Please activate your account.'
			# https://docs.djangoproject.com/en/3.1/topics/templates/#django.template.loader.render_to_string
			message = render_to_string('users/email_confirmation.html', {
				'user': user,
				'domain': current_site.domain,
				'uid': urlsafe_base64_encode(force_bytes(user.pk)),
				'token': default_token_generator.make_token(user),
				'expiration': expires(2)
				})
			recipient = form.cleaned_data.get('email')
			email = EmailMessage(mail_subject, message, to=[recipient])
			send_mail(mail_subject, message, settings.DEFAULT_FROM_EMAIL, 
				[recipient])
			messages.success(request, "Account created, please click link \
				in activation email within 48 hours to login.")
			return redirect('login')
	else:
		form = UserRegisterForm()
	return render(request, 'users/register.html', {'form': form})


def email_confirmation(request, uidb64, token):
    try:
    	uid = urlsafe_base64_decode(uidb64).decode()
    	user = UserModel._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, UserModel.DoesNotExist):
    	user = None

    if user != None:
	    if user is not None and default_token_generator.check_token(user, token) and not user.is_active:
	    	user.is_active = True
	    	user.save()
	    	messages.success(request, "Thank you for confirming, you can now login\
	    		with credentials.")
	    	return redirect('login')

	    elif user.is_active:
	    	if not request.user.is_authenticated:
	    		messages.success(request, "Your account is active, you can now login.")
	    		return redirect('login')
	    	else:
	    		messages.success(request, f"Your account is active and you \
	    			are logged in as '{request.user.username}'.")
	    		return redirect('/')

	    elif not default_token_generator.check_token(user, token):
	    	messages.warning(request, "Your activation link is invalid. Please \
	    		change your password to activate your account.")
	    	return redirect('password_reset')

    else:
    	if not request.user.is_authenticated:
    		messages.warning(request, f"Requested user '{uid}' does not exist.")
    		return redirect('register')
    	else:
    		messages.success(request, f"You are logged in as '{request.user.username}'")
    		return redirect ('/')




    	# if 1 == 1:
    	# 	pass
    	# if not request.user.is_authenticated:
	    # 	messages.warning(request, "Requested user does not exist.")
	    # 	return redirect('register')
	    # else:
	    # 	messages.success(request, f"You are logged in as '{request.user.username}'")




@login_required()
def profile(request):
	if request.method == 'POST':
		user_form = UserUpdateForm(request.POST, instance=request.user)
		user_file_form = UserFileForm(request.POST, request.FILES, 
			instance= request.user)
		if user_form.is_valid() and user_file_form.is_valid():
			user_form.save()
			user_file_form.save()
			messages.success(request, f'Update successful, thank you.')
			return redirect('private-profile')
	else:
		user_form = UserUpdateForm(instance =request.user)
		user_file_form = UserFileForm(instance= request.user)

	context = {'u_form': user_form,
	'p_form': user_file_form}
	return render(request, 'users/profile.html', context)

def validate_registration(request):
	username = request.GET.get('username', None)
	email = request.GET.get('email', None)
	password = request.GET.get('password', None)
	data = {
	'username_taken': UserModel.objects.filter(username__iexact=username).exists(),
	# 'email_taken': UserModel.objects.filter(email__iexact=email).exists(),
	'email_valid': check_email(email),
	'username_valid': check_username(username),
	'password_too_similar':check_password_similarity(password, username, email), 
	'password_too_common':check_password_commonality(password),
	'password_no_alpha': check_password_alpha(password),
	'username_profane': check_profanity(username),
	'username_length': len(username) >=3,
	'password_length': len(password) >=8,
	'username_null': len(username) == 0,
	'email_null': len(email) == 0,
	'password_null': len(password) == 0
	}
	if username != None and not data['username_null']:
		if not data['username_length'] or not re.search('[A-Za-z]', username):
			data['username_error'] = "At least 3 characters and 1 letter, please."
		elif not data['username_valid']:
			data['username_error'] = 'Only letters, digits, and underscores, please.'
		elif data['username_taken']:
			data['username_error'] = 'Username is taken.'
		elif data['username_profane']:
			data['username_error'] = "No profanity, please."
		else:
			data['username_pass'] = True
	if email != None and not data['email_null']:
		if not data['email_valid']:
			data['email_error'] = "Enter a valid email, please."
		else:
			data['email_pass'] = True
	if password != None and not data['password_null']:
		if not data['password_length']:
			data['password_error'] = "8 or more characters, please."
		elif data['password_no_alpha']:
			data['password_error'] = "Please don't use all digits."
		elif data['password_too_similar']:
			data['password_error'] = 'Password is too similar to personal info.'
		elif data['password_too_common']:
			data['password_error'] = 'Password is too common. Be strong, please.'
		else: 
			data['password_pass'] = True
	return JsonResponse(data)




def validate_pw_change(request):
	password = request.GET.get('password', None)
	current_password = request.GET.get('current_password', None)
	email = request.user.email
	username = request.user.username
	
	data = {
	'password_too_similar':check_password_similarity(password, username, email), 
	'password_too_common': check_password_commonality(password),
	'password_no_alpha': check_password_alpha(password),
	'password_correct': request.user.check_password(current_password),
	'password_identical': request.user.check_password(password),
	'password_length': len(password) >= 8,
	'password_null': len(password) == 0,
	'current_password_null': len(current_password) == 0,

	}
	if password != None and not data['password_null']:
		if not data['password_length']:
			data['password_error'] = "At least 8 characters please."
		elif data['password_no_alpha']:
			data['password_error'] = "At least 1 letter, please."
		elif data['password_too_similar']:
			data['password_error'] = 'Password is too similar to personal info.'
		elif data['password_too_common']:
			data['password_error'] = 'Password is too common. Be strong, please.'
		elif data['password_identical']:
			data['password_error'] = "You cannot use the same password."
		else:
			data['password_pass'] = True
	if current_password != None and not data['current_password_null']:
		if not data['password_correct']:
			data['wrong_password'] = "You didn't enter your current password."
		else:
			data['current_password_pass'] = True
	return JsonResponse(data)















class EmailLoginView(LoginView):
	def get(self, request, *args, **kwargs): 
		if request.user.is_authenticated:
			messages.success(request, f"You are logged in as {request.user.username}.")
			return redirect('/')
		return super(EmailLoginView, self).get(request, *args, **kwargs)

	
	form_class = Email_Login


class PasswordReset(PasswordResetView):
	form_class = RequestPassReset
	success_url = reverse_lazy('email-sent')
	def get_success_url(self):
		messages.success(self.request, "Please check your email for confirmation.")
		return super().get_success_url()
	def get (self, request, *args, **kwargs):
		if request.user.is_authenticated:
			return redirect('password_change')
		return super(PasswordReset, self).get(request, *args, **kwargs)

		
from django.views.decorators.debug import sensitive_post_parameters
from django.utils.decorators import method_decorator
INTERNAL_RESET_SESSION_TOKEN = '_password_reset_token'
class PasswordResetConfirm(PasswordResetConfirmView):
	form_class = NewPasswordForm
	reset_url_token = 'set-password'
	success_url = reverse_lazy('login')

	@method_decorator(sensitive_post_parameters())
	@method_decorator(never_cache)
	def dispatch(self, *args, **kwargs):
		assert 'uidb64' in kwargs and 'token' in kwargs
		self.validlink = False
		self.user = self.get_user(kwargs['uidb64'])
		if self.user is not None:
			token = kwargs['token']
			if token == self.reset_url_token:
				session_token = self.request.session.get(INTERNAL_RESET_SESSION_TOKEN)
				if self.token_generator.check_token(self.user, session_token):

				# If the token is valid, display the password reset form.
					self.validlink = True
					return super().dispatch(*args, **kwargs)
			else:
				if self.token_generator.check_token(self.user, token):
					# Store the token in the session and redirect to the
					# password reset form at a URL without the token. That
					# avoids the possibility of leaking the token in the
					# HTTP Referer header.
					self.request.session[INTERNAL_RESET_SESSION_TOKEN] = token
					redirect_url = self.request.path.replace(token, self.reset_url_token)
					return redirect(redirect_url)

				else:
					messages.warning(self.request, "Password reset link was \
						invalid, you can request a new one below.")
					return redirect('password_reset')

		# Display the "Password reset unsuccessful" page.
		else:
			messages.warning(self.request, "Password reset link was \
				invalid, you can request a new one below.")
			return redirect('password_reset')

		# return self.render_to_response(self.get_context_data())

	def get_success_url(self, *args, **kwargs):
		messages.success(self.request, "Password update successful.")
		return super().get_success_url()


def password_change(request):
	if not request.user.is_authenticated:
		messages.info(request, "Please first login to change your password.")
		return redirect('login')
	if request.method == 'POST':
		form = ChangePasswordForm(request.user, request.POST, initial={'username': request.user.email})
		if form.is_valid():
			user = form.save()
			update_session_auth_hash(request, user)
			messages.success(request, 'Password successfully updated.')
			return redirect('/')
		else:
			messages.warning(request, "Unable to authenticate.")
			return render(request,'users/password_change.html', {'form': form})
	else:
		form = ChangePasswordForm(request.user, initial={'username': request.user.email})
		return render(request, 'users/password_change.html', {'form': form})









            
         
            
            
        
   