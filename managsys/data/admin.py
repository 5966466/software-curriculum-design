from django.contrib import admin

# Register your models here.
from .models import App, FilesApp

admin.site.register(App)
admin.site.register(FilesApp)
