from django.contrib import admin
from . import models

# Register your models here.

admin.site.register(models.SampleType)
admin.site.register(models.DemandType)
admin.site.register(models.FollowUpRecord)
admin.site.register(models.ClinicIntention)

