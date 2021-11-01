from django.contrib import admin
from api import models
# from django.contrib.auth.admin import UserAdmin
from django.forms.models import BaseInlineFormSet
from django.contrib import messages
import json


class GustomAmdin(admin.ModelAdmin):

    ordering = ('title',)  # 按字段排序 -表示降序
    exclude = ('id', 'isDelete', 'create_user', 'create_user_id',
               'latest_update_user', 'latest_update_user_id')     # 不可见字段
    # list_display = ('title', 'host')  # 可见字段
    # list_filter = ('project',)  # 筛选
    # search_fields = ('title', )  # 搜索条件
    # list_editable = ('host',)  # 可编辑字段


class GlobalAmdin1(GustomAmdin):
    list_filter = ('project',)  # 筛选
    list_display = ('title', 'host')  # 可见字段


class GlobalAmdin2(GustomAmdin):
    list_filter = ('project',)  # 筛选
    list_display = ('title', 'params')  # 可见字段


class ReportAmdin(GustomAmdin):
    list_display = ('title', 'params')  # 可见字段


class ProjectAmdin(GustomAmdin):
    list_display = ('title', 'desc', 'version', 'users',)
                    # 'global_host', 'global_variable', 'global_header', 'global_cookie')  # 可见字段


class WorkWXApplyAdmin(GustomAmdin):
    list_display = ('title', 'desc', 'corpid', 'corpsecret', 'agentid', 'token')  # 可见字段


class ApiUserAdmin(GustomAmdin):
    list_display = ('type_id', 'type', 'users_id', 'users')  # 可见字段
    ordering = ('type_id',)  # 按字段排序 -表示降序


class GlobalEnvAdmin(GustomAmdin):
    list_filter = ('project',)  # 筛选
    list_display = ('title', 'project', 'default_uses',
                    'global_host', 'global_variable', 'global_header', 'global_cookie')  # 可见字段


class ReportFormAdmin(GustomAmdin):
    pass
    # list_filter = ('project',)  # 筛选
    list_display = ('title', 'start_line', 'sql', 'config')  # 可见字段


# 项目
admin.site.register(models.ApiProject, ProjectAmdin)
# admin.site.register(models.ApiGroup)
# admin.site.register(models.ApiApi)
# admin.site.register(models.ApiCase)

# 环境
admin.site.register(models.GlobalEnv, GlobalEnvAdmin)
admin.site.register(models.GlobalHost, GlobalAmdin1)
admin.site.register(models.GlobalVariable, GlobalAmdin2)
admin.site.register(models.GlobalHeader, GlobalAmdin2)
admin.site.register(models.GlobalCookie, GlobalAmdin2)

# 接收配置
admin.site.register(models.WorkWxUserGroup, ReportAmdin)
admin.site.register(models.WorkWxGroupChat, ReportAmdin)
admin.site.register(models.WorkWXApply, WorkWXApplyAdmin)
admin.site.register(models.EmailUserGroup, ReportAmdin)

# 任务与报告
# admin.site.register(models.TestTask)
# admin.site.register(models.TestReport)
# admin.site.register(models.TestReportDetail)

admin.site.register(models.ApiUser, ApiUserAdmin)
# admin.site.register(models.User, UserAdmin)

# 报表自动化对比
admin.site.register(models.ReportForm, ReportFormAdmin)