from django.shortcuts import render, redirect


def login(req):
    """
        :param req:
        :return: 先验证登陆用户，登陆过转动接口页面，没有转到登陆界面
    """
    s = req.session.get("user", None)
    if s:
        return redirect("/interface")
    return render(req, "login.html")


