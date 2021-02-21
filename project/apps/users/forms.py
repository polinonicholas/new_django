from django.conf import settings
from django import forms
from django.contrib.auth.forms import (UserCreationForm, AuthenticationForm,
ValidationError, PasswordResetForm, SetPasswordForm)
# from . models import Profile
from django.contrib.auth import get_user_model, authenticate, password_validation
from . variables import (check_username, check_profanity,
	InvalidLoginAttemptsCache, FIELD_NAME_MAPPING)
from project.customized_classes import DivErrorList
from django.utils.translation import ugettext, ugettext_lazy as _
import arrow
import mailer
#not sure what this does
from django.template import loader
from django.core.mail import EmailMultiAlternatives
from . commands import email_now
from django.contrib.auth.forms import _unicode_ci_compare
import re

UserModel = get_user_model()

class Email_Login(AuthenticationForm):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.error_class=DivErrorList
		#Set placeholders
		self.fields['username'].widget.attrs.update({'placeholder': 'Email', 'id': 'email',
			'autocomplete':'username email', 'type':'text'})
		self.fields['password'].widget.attrs.update({'placeholder': 'Password', 'id': 'password'})
		#labels
		self.fields['username'].label = "Email"
		# iterate all fields, add common class
		for fname, f in self.fields.items():
			for fname, f in self.fields.items():
					if fname == 'password':
						f.widget.attrs['class'] = 'login_field password'
					else:
						f.widget.attrs['class'] = 'login_field'
	error_messages = {
        'invalid_login': _("Invalid credentials."),
        'inactive': _("Please confirm your email address. If you need a new link, use the Reset Password link below."), 
        'locked': _("As a security measure, this account is locked."),
    }
	def clean(self):
		# try:
		# 	self.cleaned_data["username"] = UserModel.\
		# 	objects.get(email__iexact=self.data["username"]).email
		# except (UserModel.DoesNotExist):
		# 	self.cleaned_data["username"] = self.cleaned_data["username"]
		email = self.cleaned_data.get('username')
		password = self.cleaned_data.get('password')
		if email and password:
			self.user_cache = authenticate(email=email, password=password)
			locked_out = False
			cache_results = InvalidLoginAttemptsCache.get(email)
			lockout_timestamp = None
			now = arrow.utcnow()
			invalid_attempt_timestamps = cache_results['invalid_attempt_timestamps'] if cache_results else []
			invalid_attempt_timestamps = [timestamp for timestamp in invalid_attempt_timestamps if timestamp > now.shift(minutes=-15).timestamp]
			if cache_results and cache_results.get('lockout_start'):
				lockout_start = arrow.get(cache_results.get('lockout_start'))
				locked_out = lockout_start >= arrow.utcnow().shift(minutes=-15)
				if not locked_out:
					InvalidLoginAttemptsCache.delete(email, domain_id)
				else:
					raise forms.ValidationError(self.error_messages['locked'],code='locked')
			else:
				if self.user_cache is None and len(invalid_attempt_timestamps) < 5:
					invalid_attempt_timestamps.append(now.timestamp)
					InvalidLoginAttemptsCache.set(email, invalid_attempt_timestamps, lockout_timestamp)
				
					raise forms.ValidationError(self.error_messages['invalid_login'],code='invalid_login')
				elif len(invalid_attempt_timestamps) >= 5:
					lockout_timestamp = now.timestamp
					raise forms.ValidationError(self.error_messages['locked'],code='locked')
				elif not self.user_cache.is_active: 
					raise forms.ValidationError(self.error_messages['inactive'],code='inactive')
				else:
					self.confirm_login_allowed(self.user_cache)
		return super(Email_Login, self).clean()	


class UserRegisterForm(UserCreationForm):
	
	email = forms.EmailField(widget=forms.EmailInput(attrs={
		'placeholder': 'Email', 'id':'email', 'autocomplete':'username email'}))
	def add_prefix(self, field_name):
		# look up field name; return original if not found
		field_name = FIELD_NAME_MAPPING.get(field_name, field_name)
		return super(UserRegisterForm, self).add_prefix(field_name)
	def clean_email(self):
		email = self.cleaned_data.get('email')
		# Check to see if any users already exists with this email.
		try:
			match = UserModel.objects.get(email=email)
		except (UserModel.DoesNotExist):
		# Unable to find a user, this is fine.
			return email
		# A user was found with this as a username, raise an error.
		raise forms.ValidationError("Please use a different email.")
	def clean_username(self):
		username = self.cleaned_data.get('username')
		if not check_username(username):
			raise forms.ValidationError( "Letters, digits, and underscores only, please.")
		if check_profanity(username):
			raise forms.ValidationError( "No, profanity please.")
		if not len(username) > 2 or not re.search('[A-Za-z]', username):
			raise forms.ValidationError("At least 3 characters and 1 letter, please.")
		return username
	class Meta: 
		model = UserModel
		fields = ['email','username', 'password1']
	
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		del self.fields['password2']
		#Set placeholders
		self.fields['username'].widget.attrs.update({'placeholder': 'Display Name',
			'autocomplete':'name', 'id':'username', 'maxlength':'25'})
		self.fields['password1'].widget.attrs.update({'placeholder': 'Password',
			'id':'password'})
		#Set help texts
		self.fields['username'].help_text = 'Letters, digits and following \
		characters: @.+-_ only. Will be converted to lowercase.'
		self.fields['email'].help_text = 'Will be used to confirm account, \
		never shared.'
		self.fields['password1'].help_text = '8 characters minimum, not all digits.'
		#labels
		self.fields['username'].label = "Public name"
		self.fields['email'].label = "Email (login key):"
		# iterate all fields, add common class
		for fname, f in self.fields.items():
			if fname == 'password1':
				f.widget.attrs['class'] = 'register_field password'
			else:
				f.widget.attrs['class'] = 'register_field'





class UserUpdateForm(forms.ModelForm):
	error_messages = {
	'profanity': _("No profanity, please."),

	}

	class Meta: 
		model = UserModel
		fields = ['bio']
		widgets = {'bio': forms.Textarea(attrs={'rows': 2, 'placeholder': '...'})}
		labels = {'bio': 'What do you say?'}
		
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.error_class=DivErrorList
	def clean_bio(self):
		bio = self.cleaned_data['bio']
		if check_profanity(bio):
			raise ValidationError(
				self.error_messages['profanity'],
				code='profanity',
				)
		return bio
class UserFileForm(forms.ModelForm):
	error_messages = {
        'invalid_image': _(
            "Select a valid image, please."
        ),
    }
	class Meta:
		model = UserModel
		fields = ['image']
		widgets = {'image': forms.FileInput({"height":"10em", "width":"10em"})}
		labels = {'image': 'Update image:'}
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		# self.fields['image'] = forms.ImageField(label=_('Profile Image'), required=False, 
		# 	error_messages={'invalid':("Only images, please")}, widget=forms.FileInput({}))
		self.error_class=DivErrorList
		self.fields['image'].error_messages = self.error_messages





class RequestPassReset(PasswordResetForm):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.error_class=DivErrorList
		self.fields['email'].widget.attrs.update({'placeholder': 'Email', 'id':'email', 'autofocus':'autofocus'})
	def send_mail(self, subject_template_name, email_template_name,
                  context, from_email, to_email, html_email_template_name=None):
       
		subject = loader.render_to_string(subject_template_name, context)
		# Email subject *must not* contain newlines
		subject = ''.join(subject.splitlines())
		body = loader.render_to_string(email_template_name, context)
		mailer.send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [to_email])
		email_now()


	def get_users(self, email):
		email_field_name = UserModel.get_email_field_name()
		existing_users = UserModel._default_manager.filter(**{
		'%s__iexact' % email_field_name: email,
		})
		admin = UserModel._default_manager.filter(**{
		'%s__iexact' % email_field_name: settings.DEFAULT_FROM_EMAIL,
		})
		if len(existing_users) > 0:
			return (u for u in existing_users
			    if u.has_usable_password() and
			    _unicode_ci_compare(email, getattr(u, email_field_name))
			)
		return (admin)

class NewPasswordForm(SetPasswordForm):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.error_class=DivErrorList
		del self.fields['new_password2']
		self.fields['new_password1'].widget.attrs.update({'placeholder': 
			'New Password', 'id':'password', 'class': 'password', 
			'id': 'password'})

	def clean_new_password1(self):
		password1 = self.cleaned_data.get('new_password1')
		password_validation.validate_password(password1, self.user)
		return password1
	def save(self, commit=True):
	    password = self.cleaned_data["new_password1"]
	    self.user.set_password(password)
	    self.user.is_active = True
	    if commit:
	        self.user.save()
	    return self.user
class ChangePasswordForm(NewPasswordForm):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.fields['username'].label = ''
		self.fields['username'].required = False
		initial = kwargs.get('initial', {})

	error_messages = {**NewPasswordForm.error_messages,
	'password_incorrect': _("Please enter your current password."),
	'identical_password':_("You cannot use your current password."),
	}
	current_password = forms.CharField(
	label=_("Current password"),
	strip=False,
	widget=forms.PasswordInput(attrs={'autocomplete': 'current-password', 
		'autofocus': True,'id':'current_password', 'placeholder': 'Current Password'}),
	)

	username = forms.CharField(widget=forms.TextInput(attrs={"id":"username",
			"autocomplete":"username email", "disabled":True, "class":"hide"}))
	field_order = ['username','current_password','new_password1']

	def clean_current_password(self):
	    current_password = self.cleaned_data["current_password"]
	    if not self.user.check_password(current_password):
	        raise ValidationError(
	            self.error_messages['password_incorrect'],
	            code='password_incorrect',
	        )
	    return current_password
	def clean_new_password1(self):
		password1 = self.cleaned_data.get('new_password1')
		password_validation.validate_password(password1, self.user)
		if self.user.check_password(password1):
			raise ValidationError(
				self.error_messages['identical_password'],
				code='identical_password')
		return password1