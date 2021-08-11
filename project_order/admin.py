from django.contrib import admin
from . import models

# Register your models here.

admin.site.register(models.SalePerson)
admin.site.register(models.PayType)
admin.site.register(models.ProjectOrder)