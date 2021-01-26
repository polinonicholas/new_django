from django.shortcuts import redirect, render
from django.contrib import messages
from .forms import (UserRegisterForm, UserUpdateForm, ProfileUpdateForm, 
	Email_Login, RequestPassReset, NewPasswordForm)
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
from . commands import email_now
from django.http import HttpResponse, JsonResponse
from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings
from project.customized_classes import DivErrorList
from . variables import (expires, check_profanity, check_password_alpha, 
check_password_similarity, check_email, check_username)
from . variables import check_password_commonality as cpc
from django.views.decorators.cache import never_cache
from django.contrib.auth.views import LoginView, PasswordResetView, PasswordResetConfirmView,PasswordResetCompleteView
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _


UserModel = get_user_model()

@never_cache
def register(request):
	if request.user.is_authenticated:
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
		if score is not None:
			if score >=.9:
				recaptcha_pass = True
			elif score < .9:
				form.add_error(None, "You did not pass Google's reCAPTCHA v3, \
					please re-enter your password and complete registration using v2 checkbox:" + str(score))
		#else load v2 via jquery, blank form and check for v2 success
		else:
			if response_v2['success'] == True:
				recaptcha_pass = True
			elif response_v2['success'] != True:				
				form.add_error(None, "You did not pass Google's reCAPTCHA v3, \
					please re-enter your password and complete registration using v2 checkbox:"+ str(secret_v3))
		# save user as inactive, then send activation email. Convert UN to lower.
		if form.is_valid() and recaptcha_pass:
			user = form.save(commit=False)
			user.is_active = False
			user.username = user.username.lower()
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
			# username = form.cleaned_data.get('username')
			# # messages.success(request, f'Account created for {username}!')
			# return redirect('login')

	else:
		form = UserRegisterForm()
	return render(request, 'users/register.html', {'form': form})


def email_confirmation(request, uidb64, token):
    try:
    	uid = urlsafe_base64_decode(uidb64).decode()
    	user = UserModel._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, UserModel.DoesNotExist):
    	user = None
    if user is not None and default_token_generator.check_token(user, token):
    	user.is_active = True
    	user.save()
    	messages.success(request, "Thank you for confirming, you can now login\
    		with credentials.")
    	return redirect('login')
    elif user.is_active:
    	messages.success(request, "Your account is active, you can now login.")
    	return redirect('login')
    elif not user.is_active and not default_token_generator.check_token(user, token):
    	messages.warning(request, "Your activation link is invalid. Please \
    		change your password to activate your account.")
    	return redirect('password_reset')
    else:
    	messages.warning(request, "Your activation link is invalid.")
    	return redirect('register')



@login_required(redirect_field_name='after-login')
def profile(request):
	if request.method == 'POST':
		updated_form = UserUpdateForm(request.POST, instance =request.user)
		populated_form = ProfileUpdateForm(request.POST, request.FILES, 
			instance= request.user.profile)
		if u_form.is_valid() and p_form.is_valid():
			u_form.save()
			p_form.save()
			messages.success(request, f'Your Account Has Been Updated!')
			return redirect('profile')
	else:
		u_form = UserUpdateForm(instance =request.user)
		p_form = ProfileUpdateForm(instance= request.user.profile)

	context = {'u_form': u_form,
	'p_form': p_form}
	return render(request, 'users/profile.html', context)

def validate_registration(request):
	# for ajax requests
	username = request.GET.get('username', None)
	email = request.GET.get('email', None)
	password1 = request.GET.get('password1', None)
	password2 = request.GET.get('password2', None)

	data = {'username_taken': UserModel.objects
	.filter(username__iexact=username).exists(),
	 'email_taken': UserModel.objects
	.filter(email__iexact=email).exists(), 'email_valid': check_email(email),
	'username_valid': check_username(username), 'password_too_similar':
	check_password_similarity(password1, username, email), 'password_too_common'
	: cpc(password1),
	'password_no_alpha': check_password_alpha(password1)
	,'username_profane': check_profanity(username)}

	data['password_length_error'] = "8 or more characters, please."
	data['password_digit_error'] = "At least 1 letter, please."
	
	if not data['username_valid']:
		data['username_invalid'] = 'Only letters, digits, and underscores, please.'
	if data['username_taken']:
		data['username_error'] = 'Username taken!'
	if data['username_profane']:
		data['username_has_profanity'] = "No profanity, please."
	if not data['username_taken'] and data['username_valid'] and len(username) \
	> 0 and not data['username_profane']:
		data['username_pass'] = True

	if data['email_taken']:
		data['email_error'] = 'Email associated with existing account!'
	if not data['email_valid']:
		data['email_invalid'] = "Enter a valid email, please."
	if not data['email_taken'] and data['email_valid']:
		data['email_pass'] = True

	if data['password_too_similar']:
		data['password_error'] = 'Password is too similar to personal info.'
	if data['password_too_common']:
		data['password_common'] = 'Password is too common. Be strong, please.'
	if not data['password_too_common'] and not data['password_too_similar'] and\
	len(password1) >=8 and not data['password_no_alpha']:
		data['password_pass'] = True
	return JsonResponse(data)


class EmailLoginView(LoginView):
	def get(self, request, *args, **kwargs):
		if request.user.is_authenticated:
			return redirect('/')
		return super(EmailLoginView, self).get(request, *args, **kwargs)

	
	form_class = Email_Login


class PasswordReset(PasswordResetView):
	form_class = RequestPassReset
	success_url = reverse_lazy('email-sent')
	def get_success_url(self):
		messages.success(self.request, "Please check your email for confirmation.")
		return super().get_success_url()
		
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
					messages.info(self.request, "Password reset link was invalid, you can request a new one below.")
					return redirect('password_reset')

		# Display the "Password reset unsuccessful" page.
		return self.render_to_response(self.get_context_data())

	def get_success_url(self, *args, **kwargs):
		messages.success(self.request, "Password update successful.")
		return super().get_success_url()