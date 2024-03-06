from django.contrib import admin
from.models import Room,Topic,Message
# Register your models here.
#User model is registered by default
admin.site.register(Room)
admin.site.register(Topic)
admin.site.register(Message)