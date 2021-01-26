from django import forms
from django.contrib.auth.forms import (UserCreationForm, AuthenticationForm,
ValidationError, PasswordResetForm, SetPasswordForm)
from . models import Profile
from django.contrib.auth import get_user_model, authenticate, password_validation
from . variables import check_username, check_profanity, InvalidLoginAttemptsCache
from project.customized_classes import DivErrorList
from django.utils.translation import ugettext, ugettext_lazy as _
import arrow
UserModel = get_user_model()

class Email_Login(AuthenticationForm):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.error_class=DivErrorList
		#Set placeholders
		self.fields['username'].widget.attrs.update({'placeholder': 'Username/Email'})
		self.fields['password'].widget.attrs.update({'placeholder': 'Password'})
		# iterate all fields, add common class
		for fname, f in self.fields.items():
			f.widget.attrs['class'] = 'login_field'
	error_messages = {
        'invalid_login': _("Invalid credentials. If you have not confirmed your email, please do so."),
        'inactive': _("Account is inactive."), 
        'locked': _("As a security measure, this account is locked."),
    }
	def clean(self):
		try:
			self.cleaned_data["username"] = UserModel.\
			objects.get(email__iexact=self.data["username"])
		except (UserModel.DoesNotExist):
			self.cleaned_data["username"] = self.cleaned_data["username"]
			# return super(Email_Login, self).clean()
		username = self.cleaned_data.get('username')
		password = self.cleaned_data.get('password')
		if username and password:
			self.user_cache = authenticate(username=username, password=password)
			locked_out = False
			cache_results = InvalidLoginAttemptsCache.get(username)
			lockout_timestamp = None
			now = arrow.utcnow()
			invalid_attempt_timestamps = cache_results['invalid_attempt_timestamps'] if cache_results else []
			invalid_attempt_timestamps = [timestamp for timestamp in invalid_attempt_timestamps if timestamp > now.shift(minutes=-15).timestamp]
			if cache_results and cache_results.get('lockout_start'):
				lockout_start = arrow.get(cache_results.get('lockout_start'))
				locked_out = lockout_start >= arrow.utcnow().shift(minutes=-15)
				if not locked_out:
					InvalidLoginAttemptsCache.delete(username, domain_id)
				else:
					raise forms.ValidationError(self.error_messages['locked'],code='locked')
			else:
				if self.user_cache is None and len(invalid_attempt_timestamps) < 5:
					invalid_attempt_timestamps.append(now.timestamp)
					InvalidLoginAttemptsCache.set(username, invalid_attempt_timestamps, lockout_timestamp)
					raise forms.ValidationError(self.error_messages['invalid_login'],code='invalid_login')
				elif len(invalid_attempt_timestamps) >= 5:
					lockout_timestamp = now.timestamp
					raise forms.ValidationError(self.error_messages['locked'],code='locked')
				else:
					self.confirm_login_allowed(self.user_cache)
		return super(Email_Login, self).clean()				
				
class UserRegisterForm(UserCreationForm):
	email = forms.EmailField(widget=forms.EmailInput(attrs={
		'placeholder': 'Valid Email Address', 'disabled': True, 'autocomplete':'off'}))
	def clean_email(self):
		email = self.cleaned_data.get('email')
		# Check to see if any users already exists with this email.
		try:
			match = UserModel.objects.get(email=email)
		except (UserModel.DoesNotExist):
		# Unable to find a user, this is fine.
			return email
		# A user was found with this as a username, raise an error.
		raise forms.ValidationError( "Provided email already in use, please\
			use another.")
	def clean_username(self):
		username = self.cleaned_data.get('username')
		if not check_username(username):
			raise forms.ValidationError( "Letters, digits, and underscores only, please.")
		if check_profanity(username):
			raise forms.ValidationError( "No, profanity please.")
		return username
	class Meta: 
		model = UserModel
		fields = ['username', 'email', 'password1']
	
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		del self.fields['password2']
		#Set placeholders
		self.fields['username'].widget.attrs.update({'placeholder': 'Username',
			'autocomplete':'off'})
		self.fields['password1'].widget.attrs.update({'placeholder': 'Password',
			'disabled': True,'autocomplete':'off'})
		#Set help texts
		self.fields['username'].help_text = 'Letters, digits and following \
		characters: @.+-_ only. Will be converted to lowercase.'
		self.fields['email'].help_text = 'Will be used to confirm account, \
		never shared.'
		self.fields['password1'].help_text = '8 characters minimum, not all digits.'
		# iterate all fields, add common class
		for fname, f in self.fields.items():
			f.widget.attrs['class'] = 'register_field'
class UserUpdateForm(forms.ModelForm):
	email = forms.EmailField()
	class Meta: 
		model = UserModel
		fields = ['username', 'email']
class ProfileUpdateForm(forms.ModelForm):
	class Meta:
		model = Profile
		fields = ['image', 'bio']

class RequestPassReset(PasswordResetForm):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.fields['email'].widget.attrs.update({'placeholder': 'Email'})

class NewPasswordForm(SetPasswordForm):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		del self.fields['new_password2']
		self.fields['new_password1'].widget.attrs.update({'placeholder': 'New Password'})

	def clean_new_password1(self):
		password1 = self.cleaned_data.get('new_password1')
		password_validation.validate_password(password1, self.user)
		return password1

		