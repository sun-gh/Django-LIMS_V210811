from django.contrib import admin
from . import models

# Register your models here.


class SampleRecordAdmin(admin.ModelAdmin):
    list_display = ('project_num', 'sample_amount', 'sample_type', 'sample_sender')


admin.site.register(models.SampleType)
admin.site.register(models.MachineTime)
admin.site.register(models.SampleQuality)
admin.site.register(models.AdditionalItem)
admin.site.register(models.ProjectType)
admin.site.register(models.SampleRecord, SampleRecordAdmin)
admin.site.register(models.OperatePerson)
admin.site.register(models.SampleStatus)
admin.site.register(models.ProjectInterrupt)
admin.site.register(models.Machine)
