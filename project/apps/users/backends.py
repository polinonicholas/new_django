from django.contrib.auth import backends

class CustomModelBackend(backends.ModelBackend):
	def user_can_authenticate(self, user):
		return True