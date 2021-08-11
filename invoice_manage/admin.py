from django.contrib import admin
from . import models

# Register your models here.

admin.site.register(models.InvoiceRequire)
admin.site.register(models.InvoiceInfo)
admin.site.register(models.ApplyInvoice)
admin.site.register(models.VoidRedInfo)
