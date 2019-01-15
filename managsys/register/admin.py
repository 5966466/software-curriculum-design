from django.contrib import admin

# Register your models here.
from .models import Acc, IPaddr, FilesAcc

admin.site.register(Acc)
admin.site.register(IPaddr)
admin.site.register(FilesAcc)