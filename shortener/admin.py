from django.contrib import admin

from .models import Link


@admin.register(Link)
class LinkAdmin(admin.ModelAdmin):
    list_display = ("key", "url", "is_active", "created_at", "last_visit", "clicks")
