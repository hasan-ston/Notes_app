from django.contrib import admin
from .models import Note_set, Questions


@admin.register(Note_set)
class NoteSetAdmin(admin.ModelAdmin):
    list_display = ("title", "subject", "uploaded_at")
    search_fields = ("title", "subject")


@admin.register(Questions)
class QuestionsAdmin(admin.ModelAdmin):
    list_display = ("question_text", "note_set", "reviewed", "creation_date")
    list_filter = ("reviewed", "note_set")
