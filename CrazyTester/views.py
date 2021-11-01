from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.http import HttpResponseRedirect
from api.extensions.custom_response import *
from django.contrib import auth
from django.template.exceptions import TemplateDoesNotExist


@login_required
@require_http_methods(["GET"])
def into_html(req, html_path):
    """
        2021年9月26日：
        :param html_path: 页面路径
        :return:  index_flag == 1 根据页面路径返回对应页面，没有则提示
        :return:  index_flag != 1 时固定返回index页面，前端处理路径并加载页面到iframe里
    """

    index_flag = req.GET.get("index_flag", "")
    try:
        if index_flag == "1":
            return render(req, "index.html")
        return render(req, "{}.html".format(html_path))

    except TemplateDoesNotExist:
        return response_404("不存在的页面！", path=html_path)


@require_http_methods(["GET"])
def login(req):
    """
        进去登陆页面，先验证登陆用户，登陆过跳转到主页页面，未登录跳转登陆界面
    """
    s = req.session.get("user", None)
    if s:
        return redirect("html/api/welcome?index_flag=1")
    return render(req, "login.html")


@require_http_methods(["POST"])
@login_required
def get_user_info(req):

    user_name = str(req.session.get("user", None))

    if user_name:
        return response_200(user_name=user_name)
    else:
        return response_400("获取用户信息失败!")


@require_http_methods(["POST"])
# post方式根据入参验证用户身份
def login_verify(req):

    user = req.POST.get("user", None)
    pw = req.POST.get("pw", None)

    u = auth.authenticate(username=user, password=pw)   # 引用django中的管理用户账号, 若有效则返回代表该用户的user对象, 若无效则返回None。

    if u:
        auth.login(req, u)                              # django记录登陆
        req.session["user"] = user                      # 将session记录到浏览器
        return response_200()

    else:
        return response_400("用户名或密码错误!")


@login_required
@require_http_methods(["GET"])
def logout(request):
    try:
        # 删除当前会话数据并删除会话的Cookie
        request.session.flush()
        return response_200()
    except Exception as e:
        return response_500("退出登陆失败！{}".format(e))


def not_found_api(req):
    return response_404("不存在的接口路径！", path=req.path)



