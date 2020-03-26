from django.contrib import admin
# Register your models here.

from interface import models
admin.site.register(models.NavNode)
admin.site.register(models.APIData)
admin.site.register(models.CaseData)
admin.site.register(models.TestReport)