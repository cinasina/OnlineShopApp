from django.contrib import admin
from .forms import *
from django.contrib.auth.models import Group


# Register the new UserAdmin...
admin.site.register(MyUser, UserAdmin)
admin.site.unregister(Group)
