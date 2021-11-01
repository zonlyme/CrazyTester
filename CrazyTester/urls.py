"""CrazyTester URL Configuration

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
from CrazyTester.views import *

urlpatterns = [

    path('admin/', admin.site.urls),

    # 处理所有静态页面（除了登陆login）
    url(r'^html/(.*)$', into_html),

    url(r"^$|^login$", login),             # 登陆界面,已经登陆过会跳到主页页面，
    url(r"^login_verify$", login_verify),   # 页面登陆验证
    url(r"accounts/login/", login),     # 用django自带的登陆验证，如果没有登陆，会跳转到登陆页面
    url(r"accounts/logout", logout),     # 用django自带的登陆验证，如果没有登陆，会跳转到登陆页面
    url(r"get_user_info", get_user_info),  # 用django自带的登陆验证，如果没有登陆，会跳转到登陆页面

    url(r'^api/', include('api.urls')),  # 接口相关

    # url(r'', not_found_api)  # 不存在的接口

]
