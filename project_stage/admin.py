from django.contrib import admin
from . import models

# Register your models here.

admin.site.register(models.SampleType)
admin.site.register(models.MachineTime)
admin.site.register(models.SampleQuality)
admin.site.register(models.AdditionalItem)
admin.site.register(models.ProjectType)
admin.site.register(models.SampleRecord)
admin.site.register(models.OperatePerson)
admin.site.register(models.SampleStatus)
admin.site.register(models.ProjectInterrupt)
admin.site.register(models.Machine)
