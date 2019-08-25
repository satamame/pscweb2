from django.contrib import admin
from .models import Facility, Place, Rehearsal, Scene, Actor, Character,\
    Attendance, Appearance

admin.site.register(Facility)
admin.site.register(Place)
admin.site.register(Rehearsal)
admin.site.register(Scene)
admin.site.register(Actor)
admin.site.register(Character)
admin.site.register(Attendance)
admin.site.register(Appearance)
