from django.shortcuts import render
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect, FileResponse, StreamingHttpResponse
from django.forms.models import model_to_dict
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.conf import settings
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
from .models import *
import random
import hashlib
import time
import datetime
import os
import copy
import requests


def test_self(req):

    # 1 给所有asserts里的assert加上assert["assert_status"] = "1"
    # 2 判断所有assert里的断言方式,如果是15,则改成1
    def func2():
        case_list = CaseData.m.filter()
        for case in case_list:
            if case.asserts:  # 不为空
                asserts = json.loads(case.asserts)
                if asserts:  # 转换成字典后如果有数据
                    for assert1 in asserts:
                        if assert1["assert_method"] == "15":  # 2
                            assert1["assert_method"] = "1"  # 2
                            assert2 = json.dumps(asserts)
                            assert2 = assert2.replace("\"", "\\\"").replace("\'", "\\\'")
                            # assert2 = '[{"assert_method": "1", "assert_status": "1", "assert_key": "[\"result\"][\"state\"]", "assert_expect_value": "601"}]'
                            CaseData.m.filter(id=case.id).update({"asserts":assert2})
                            print("更改", case.id)
    return JsonResponse("ok", safe=False)


# 主页
@login_required
def interface(req):
    user_name = req.session.get("user", "账户异常")
    return render(req, "interface/interface.html", {"user_name":user_name})


# 获取测试环境数据
def get_env(req):
    env_datas = EnvData.m.filter()
    env_info = []
    for i in env_datas:
        env_info.append(model_to_dict(i))
    return JsonResponse(json.dumps(env_info), safe=False)


# post方式根据入参验证用户身份
def login_verify(req):
    if req.method == "POST":
        user = req.POST.get("user", None)
        pw = req.POST.get("pw", None)
        u = auth.authenticate(username=user, password=pw)   # 引用django中的管理用户账号, 若有效则返回代表该用户的user对象, 若无效则返回None。

        # print(user, pw, type(u), u)
        if u:
            auth.login(req, u)                              # django记录登陆
            req.session["user"] = user                      # 将session记录到浏览器
            r_data = {"ret":True}
        else:
            r_data = {"ret":False, "erro_msg": "用户名或密码错误！"}
        r_data = {"ret": True}
        return JsonResponse(json.dumps(r_data), safe=False)


# get方式或缓存验证用户身份
def verify_user(req):
    """
    :param req: test_api 可能通过session携带用户信息，也可能是通过url参数携带账号密码
    :return:
    """

    # 先查看url地址有没有携带用户名密码
    try:
        user = req.GET.get("user", None)
        pw = req.GET.get("pw", None)
    except:
        # 在查看session有没有用户信息
        return get_info_for_session(req)
    else:
        user = auth.authenticate(username=user, password=pw)  # 引用django中的管理用户账号, 若有效则返回代表该用户的user对象, 若无效则返回None。
        if user:
            return str(user)
        else:
            return get_info_for_session(req)


# 从session中获取信息，默认用户信息，返回用户名
def get_info_for_session(req, info="user"):
    return str(req.session.get(info, None))


@login_required
def logout(request):
    # 删除当前会话数据并删除会话的Cookie
    request.session.flush()
    return HttpResponseRedirect('/login')


# 只限ｐａｒａｍｓ　ｋｖ格式转成ｊｓｏｎ格式
def switch_json(req):
    data = {}
    try:
        param_keys = req.POST.getlist("param_key", None)
        param_values = req.POST.getlist("param_value", None)
        # print(1, param_keys, param_values)
        data["warning"] = []

        # 将kv格式的参数转换成字典
        kv_params = kv_switch_dict(param_keys, param_values, data["warning"])
        # print(kv_params)
        # 在转成json格式
        data["data"] = json.dumps(kv_params, indent=4, ensure_ascii=False)
        data["ret"] = True
    except Exception as e:
        data["ret"] = False
        data["erro"] = "{}".format(e)

    data["warning"] = ",".join(data["warning"])
    return JsonResponse(json.dumps(data), safe=False)


# 只限ｐａｒａｍｓ　ｊｓｏｎ格式转成ｋｖ格式
def switch_kv(req):
    data = {}
    jp = req.POST["json_params"]
    try:
        data["ret"] = True
        data["data"] = json.loads(jp)

    except:
        data["ret"] = False
        data["erro"] = "json格式数据有错误或者为空！"

    return JsonResponse(json.dumps(data), safe=False)


# f12 粘贴的数据格式转换成ｊｓｏｎ格式
def F12_p_to_json(req):
    data = {}
    try:
        params = req.POST["params"]
        dict_params = {i.split(": ")[0]: i.split(": ", 1)[-1] for i in params.split("\n") if i}

        data["ret"] = True
        data["data"] = json.dumps(dict_params, ensure_ascii=False, indent=4)

    except Exception as e:
        data["ret"] = False
        data["erro"] = "{}".format(e)

    return JsonResponse(json.dumps(data), safe=False)


# 将从表单获取的kv形式的param和header转换成字典
def kv_switch_dict(k, v, warning):
    # 将单个的param key，value组成小列表，添加到item["param"]大列表中,最后在转换成json格式
    temp = {}
    if k:
        for i in range(len(k)):
            if k[i].strip():
                try:
                    temp[k[i]] = v[i]
                except:
                    warning.append("param或者header名称为:'{}'的部分有错误！".format(k[i]))
            else:
                warning.append("param或者header名称为空或者为空白的已被略过！")
    temp = temp if temp else None

    return temp


# 验证非空
def verify_not_is_None(item, fileds):
    """
    :param item: 字典格式数据
    :param fileds: 要验证的字段
    :return: 如果是空的字段，返回字段名，
                所有字段都不为空，返回None
    """
    for i in fileds:
        if not item[i]:
            return i
    else:
        return None


# 验证是否为json格式
def verify_is_json(item, fileds):
    """
    :param item: 字典格式数据
    :param fileds: 字典里面要验证的字段
    :return: 是josn格式，返回None，否则返回错误信息
    """
    for i in fileds:
        # 如果值不为None
        if item[i]:
            try:
                j = json.loads(item[i])
                if type(j) == str:
                    return "{}不是json格式:{}".format(i, type(j))
            except:
                return "{}不是json格式".format(i)


# json转换字典
def json_to_dict(item, fileds):
    for i in fileds:
        if item[i]:
            try:
                item[i] = json.loads(item[i])
            except:
                pass
                # print(item[i])


# 字典转换json
def dict_to_json(item, fileds):
    for i in fileds:
        if item[i]:
            item[i] = json.dumps(item[i])
        else:
            item[i] = ""


# 字典转换json并格式化
def dict_to_json_and_fromat(item, fileds):
    for i in fileds:
        if item[i]:
            item[i] = json.dumps(item[i], ensure_ascii=False, indent=4)
        else:
            item[i] = ""


# 添加时间戳
def add_sign(req):
    """
        获取cookies值,转换成字典格式,将字典中sign的值赋为当前时间戳
    """
    data = {}
    try:
        cookies = req.POST["cookies"]
        if cookies:
            dict_cookies = json.loads(cookies)
        else:
            dict_cookies = {}

        timestamp = str(int(time.time() * 1000))
        dict_cookies['sign'] = timestamp

        data["ret"] = True
        data["data"] = json.dumps(dict_cookies, ensure_ascii=False, indent=4)

    except Exception as e:
        data["ret"] = False
        data["erro"] = "{}".format(e)

    return JsonResponse(json.dumps(data), safe=False)


# 多线程
class Futures:

    def __init__(self, max_workers):
        self.executor = ThreadPoolExecutor(max_workers=max_workers) # 线程池，执行器
        self.tasks = []                                             # 线程集合

    def submit(self, func, arg, *args, **kwargs):
        task = self.executor.submit(func, arg, *args, **kwargs)
        self.tasks.append(task)
        return task

    def as_completed(self):
        """
            :return: 阻塞主进程,直到所有线程完成任务
        """
        for future in as_completed(self.tasks):
            # print("等待...{}".format(len(self.tasks)))
            future.result()


def download(req,fp):
    file_path = os.path.join(settings.MEDIA_ROOT_VIRTUAL, fp)
    if not os.path.exists(file_path):
        return HttpResponse("文件不存在：{}".format(fp))

    file = open(file_path, 'rb')
    response = FileResponse(file)
    response['Content-Type'] = 'application/octet-stream'
    # response['Content-Type'] = 'application/vnd.ms-excel'  # 注意格式
    response['Content-Disposition'] = 'attachment;filename="{}"'.format(file_path.rsplit("/")[-1])

    return response


# 属于 中数测试环境和生产环境的要在header里加上这些
def getheader(env_params):
    UID = ""
    SECURITY_KEY = ""
    x_appid = ""
    if env_params:
        for i in env_params:
            if i["key"] == "UID":
                UID = i["value"]
            if i["key"] == "SECURITY_KEY":
                SECURITY_KEY = i["value"]
            if i["key"] == "X-Appid":
                x_appid = i["value"]

    return get_headmap(UID, SECURITY_KEY, x_appid)


def get_headmap(UID, SECURITY_KEY, x_appid):
	"自定义头"
    return ""