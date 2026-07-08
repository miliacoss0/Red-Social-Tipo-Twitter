from django.contrib import admin
from .models import Tweet, HashTag

admin.site.register(Tweet)
admin.site.register(HashTag)