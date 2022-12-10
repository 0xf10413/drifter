from django.contrib import admin

from .models import MachType, Phase, Server

admin.site.register(MachType)
admin.site.register(Phase)
admin.site.register(Server)
