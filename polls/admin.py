from django.contrib import admin
from .models import Note_set, Questions
admin.site.register(Note_set) # tells django that note_set object as admin interface
admin.site.register(Questions)