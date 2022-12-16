from django.contrib import admin

# Register your models here.
from swapi.models import File


class AdminFile(admin.ModelAdmin):
    list_display = ("id", "filename", "count_of_people", "datetime")


admin.site.register(File, AdminFile)
