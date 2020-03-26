"""SoftwareTest URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls import url, include
from .views import *

urlpatterns = [
    path('admin/', admin.site.urls),

    url(r"^$|^login$", login),             # 登陆界面,已经登陆过会跳到接口页面，
    url(r"accounts/login/", login),     # 用django自带的登陆验证，如果没有登陆，会跳转到登陆页面

    url(r'^interface/', include('interface.urls')), # 接口页面

]
