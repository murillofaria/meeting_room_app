from django.contrib import admin

from meeting_room_app.models import Reuniao, Sala

admin.site.register(Sala)
admin.site.register(Reuniao)