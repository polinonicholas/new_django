from django.apps import AppConfig


class UsersConfig(AppConfig):
    name = 'project.apps.users'
    # django.db.models.signals.class_prepared
    def ready(self): 
    	import project.apps.users.signals



