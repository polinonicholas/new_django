from django import forms
from django.contrib.auth.forms import (UserCreationForm, AuthenticationForm,
ValidationError)
from . models import Profile
from django.contrib.auth import get_user_model
from . variables import check_username, check_profanity
UserModel = get_user_model()
#add ability to login with user.email, in addition to username.
class Email_Login(AuthenticationForm):
	def clean(self):
		try:
			self.cleaned_data["username"] = UserModel().\
			objects.get(email__iexact=self.data["username"])
		except (UserModel.DoesNotExist):
			return super(Email_Login, self).clean()
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

    	


		