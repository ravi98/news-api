from django.contrib import admin
from django.contrib.auth import get_user_model
from apiApp.models import *
# Register your models here.


admin.site.register(get_user_model())
admin.site.register(Article)
admin.site.register(SearchTable)