from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from . forms import UserRegisterForm
from . models import User

class CustomUserAdmin(UserAdmin):
    add_form = UserRegisterForm
    model = User
    list_display = ('email', 'is_staff', 'is_active', 'joined')
    list_filter = ('email', 'is_staff', 'is_active',)
    fieldsets = (
        (None, {'fields': ('email', 'password', 'username', 'image', 'bio')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username','password1', 'is_staff', 'is_active')}
        ),
    )
    search_fields = ('email',)
    ordering = ('email',)


admin.site.register(User, CustomUserAdmin)