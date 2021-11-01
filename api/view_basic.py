from django.http import JsonResponse, FileResponse
from django.views.decorators.http import require_http_methods
from django.forms.models import model_to_dict
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.conf import settings
from concurrent.futures import ThreadPoolExecutor, as_completed
from django.db import connection, close_old_connections
from api.extensions.custom_response import *
from queue import Queue
from api.models import *
import json
import time
import datetime
import os
import base64


# @require_http_methods(["GET"])
def test(req):
    if req.user.is_superuser:
        print("是")
    else:
        print("不是")

def task_count():
    tasks = TestTask.m.filter()
    all_count = 0
    for task in tasks:
        count = len(str_to_list(task.case_ids))
        print(task.id, count)
        all_count += count

    print(all_count)
    return response_200()


# 发送邮件调试
def test2(req):
    wwx = WorkWXApply(2)
    # response_400(data={"a":1}, raise_flag=True)
    if not wwx.msg:
        textcard = {
            "description": "接口测试平台主页：\n<a href=\"http://10.112.16.6/home\">http://10.112.16.6/home</a>",
            "title": "测试任务-测试报告",
            "btntxt": "查看详情",
            "url": "http://10.112.16.6/home"
        }
        wwx.send_msg("guojing02", textcard)
        if wwx.msg:
            return response_400(wwx.msg)
        else:
            return response_200()
    else:
        return response_400(wwx.msg)

    # item = {
    #     "body": str(req.body),
    #     "GET": dict(req.GET),
    #     "POST": dict(req.POST),
    #     "user": req.POST.get("user", None)
    # }
    return response_200(item)


def get_now_time():
    return datetime.datetime.now()


def json_dumps(data):
    return json.dumps(data, ensure_ascii=False)


def json_dumps_indent4(data):
    return json.dumps(data, ensure_ascii=False, indent=4)


def page_handel(req, raw_data, model_to_dict_handle=True):
    item = {
        "page": None,
        "page_size": None,
        "count": len(raw_data),
        "data": [],
    }
    page = req.GET.get("page", "1")
    page_size = req.GET.get("page_size", "10")
    # page_size为-1表示要所有数据不分页
    if page_size == "-1":
        data = raw_data
    else:
        # page 如果只包含正整数并且不为0 则 int(), 否则为1
        page = int(page) if page.isdigit() and page != "0" else 1
        page_size = int(page_size) if page_size.isdigit() and page_size != "0" else 10

        data = raw_data[((page - 1) * page_size):((page - 1) * page_size) + page_size]

        item["page"] = page
        item["page_size"] = page_size

    if model_to_dict_handle:
        for i in data:
            item["data"].append(model_to_dict(i))
    else:
        item["data"] = data

    return item


def get_user_info_for_session(req, item=None, create=False):
    """
    从用户信息
    :param req:
    :param create: 是否为创建
    :param item: 如果传了item，会把用户信息user_info update到item中，
    :return: user_info
    """
    try:
        user = str(req.session.get("user"))
        user_id = req.session.get('_auth_user_id')
        # print(req.session)
    except Exception as e:
        response_400_raise_exception("获取用户名，用户id时出错：{}".format(e))
    else:
        c_time = str(get_now_time())
        user_info = {
            "latest_update_user": user,
            "latest_update_user_id": user_id,
            "u_date": c_time,
        }
        if create:
            user_info["create_user"] = user
            user_info["create_user_id"] = user_id
            user_info["c_date"] = c_time

        if item:
            item.update(user_info)

        return user_info


@login_required
@require_http_methods(["POST"])
def excel_json_auto_switch(req):
    sample_data_raw = req.POST.get("sample_data", "")
    sample_data = None

    if not sample_data_raw:
        return response_400("样例数据为空！")

    try:
        sample_data_json = json.loads(sample_data_raw)

    except:
        sample_data = sample_data_wsitch_json(sample_data_raw)

    else:
        if type(sample_data_json) == str:
            sample_data = sample_data_wsitch_json(sample_data_raw)
        elif type(sample_data_json) == list:
            sample_data = sample_data_wsitch_excel(sample_data_json)
        else:
            return response_400("样例数据格式有误，请检查修改！")

    return response_200(sample_data=sample_data)


def sample_data_wsitch_excel(sample_data_json):
    lines = []
    if not sample_data_json:
        return ""
    try:
        headers = sample_data_json[0].keys()
        lines.append("\t".join(headers))

        for i in sample_data_json:
            item = []
            for h in headers:
                item.append(i[h])
            lines.append("	".join(item))

        sample_data_str = "\n".join(lines)
        return sample_data_str

    except Exception as e:
        return response_400("样例数据格式有误，请检查修改！")


def sample_data_wsitch_json(sample_data_raw):
    sample_data_json = []

    try:
        sample_data_list = [i.split("\t") for i in sample_data_raw.strip(" ").split("\n") if i]

        row = len(sample_data_list[0])
        cos = len(sample_data_list)

        if cos == 1:
            response_400_raise_exception("测试样例数据有误1,请检查!（至少两行数据）")

        for c in range(1, cos):
            sample_data_item = {}
            for r in range(row):
                sample_data_item[sample_data_list[0][r]] = sample_data_list[c][r]
            sample_data_json.append(sample_data_item)

        sample_data_json = json_dumps_indent4(sample_data_json)
        return sample_data_json

    except Exception as e:
        response_400_raise_exception("测试样例数据有误2,请检查!\r\n{}".format(e))


# 分割逗号
def str_to_list(strs, flag=","):
    """
        :param strs: 字符串
        :param flag: 分隔符
        :return: 字符串以分隔符分割，并且每个元素strip并且不要空的
                "1,2 ,2 ,3,   ," ==> ['1', '2', '2', '3']
    """
    strs = strs or ""
    return [i.strip() for i in strs.strip().split(flag) if i.strip()]


@require_http_methods(["POST"])
# 只限params, kv格式转成json格式
def switch_json(req):
    param_keys = req.POST.getlist("param_key", [])
    param_values = req.POST.getlist("param_value", [])
    try:

        warning = []
        params = {}
        # 键值对格式转换成dict格式
        for i in range(len(param_keys)):
            if param_keys[i].strip():
                params[param_keys[i]] = param_values[i]
            else:
                warning.append("params名称为空的参数已被忽略！")
        # print(params)

        warning = ",".join(warning)
        return response_200(data=params, warning=warning)

    except Exception as e:
        return response_400("出错:{}".format(e))


@require_http_methods(["POST"])
def switch_kv(req):
    jp = req.POST.get("json_params", "")
    try:
        data = json.loads(jp)
        return response_200(data=data)

    except:
        return response_400("json格式数据有错误或者为空！")


@require_http_methods(["POST"])
# f12 粘贴的数据格式转换成json格式
def F12_p_to_json(req):
    params = req.POST.get("params", "")

    try:
        dict_params = {i.split(": ")[0]: i.split(": ", 1)[-1] for i in params.split("\n") if i}
        data = json_dumps_indent4(dict_params)

        return response_200(data=data)

    except Exception as e:

        return response_400("出错:{}".format(e))


# 将从表单获取的kv形式的param和header转换成字典
def kv_switch_dict(k, v):
    """
    k,v 皆为长度一样的列表,返回{k[i]:v[i]...}
    """

    item = {}
    warning = []

    for i in range(len(k)):
        if k[i].strip():
            item[k[i]] = v[i]
        else:
            warning.append("名称为空的参数已被忽略！")

    return {
        "temp": item,
        "warning": warning,
    }


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
def verify_is_json_and_switch(item, fileds, switch=True):
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
                if type(j) == str or type(j) == int:
                    return "{}必须为json格式,当前为字符串或数字格式!".format(i)
                if switch:
                    item[i] = j
            except:
                return "{}必须为json格式".format(i)
            else:
                if type(j) == str:
                    return "{}必须为json格式".format(i)


# 字典转换json
def dict_to_json(item, fileds):
    for i in fileds:
        if item[i]:
            item[i] = json_dumps(item[i])
        else:
            item[i] = ""


@require_http_methods(["POST"])
# 添加时间戳
def add_sign(req):
    """
        获取cookies值,转换成字典格式,将字典中sign的值赋为当前时间戳
    """
    try:
        cookies = req.POST["cookies"]
        if cookies:
            dict_cookies = json.loads(cookies)
        else:
            dict_cookies = {}

        timestamp = str(int(time.time() * 1000))
        dict_cookies['sign'] = timestamp

        data = json_dumps_indent4(dict_cookies)
        return response_200(data=data)

    except Exception as e:
        return response_400("错误:{}".format(e))


# 多线程
class Futures:

    def __init__(self, max_workers):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)  # 线程池，执行器
        self.tasks = []  # 线程集合

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


@require_http_methods(["GET"])
def download(req, file_path):
    file_path_real = os.path.join(settings.MEDIA_ROOT_VIRTUAL, file_path)
    if not os.path.exists(file_path_real):
        return response_404("文件不存在：{}！".format(file_path))

    file = open(file_path_real, 'rb')
    response = FileResponse(file)
    response['Content-Type'] = 'application/octet-stream'
    # response['Content-Type'] = 'application/vnd.ms-excel'  # 注意格式
    response['Content-Disposition'] = 'attachment;filename="{}"'.format(file_path_real.rsplit("/")[-1])

    return response


def customer_get_list(model, filter_item=None, order_by=None):
    """
    :param model: 模型类对象
    :param filter_item: 字典
    :param order_by: 元祖，传入 () 时不排序
    :return:
    """

    filter_item = filter_item or {}
    order_by = order_by or ("title", ) if order_by != -1 else ()
    datas = []

    try:
        infos = model.m.filter(**filter_item).order_by(*order_by)

        for i in infos:
            datas.append(model_to_dict_custom(i))

    except Exception as e:
        return response_400("错误信息：{}".format(e))

    return response_200(data=datas)


def model_to_dict_custom(model):

    data = model_to_dict(model, exclude=["isDelete", "c_date", "u_date"])
    data["c_date"] = model.c_date.strftime('%Y-%m-%d %H:%M:%S')
    data["u_date"] = model.u_date.strftime('%Y-%m-%d %H:%M:%S')

    return data


def api_ids_handle(item):
    """
    :param item: 根据item中的project_id, group_ids,api_ids获取对应所有api_id
        会在item中补充group_title_list,api_title_list字段
    :return:  返回 msg(错误信息)和api_id_list
    """
    api_id_list = None

    def set_msg_and_return(msg=""):
        if msg:
            item["msg"] = msg
            item["isValid"] = False
            # item["group_title_list"] = json_dumps(['测试内容失效!:{}'.format(msg)])
            # item["api_title_list"] = json_dumps(['测试内容失效!:{}'.format(msg)])
            item["group_title_list"] = ""
            item["api_title_list"] = ""
        return msg, api_id_list

    if not item["group_ids"] and not item["api_ids"]:
        return set_msg_and_return("未填写分组id或接口id！")

    # 验证project_id
    if item["project_id"]:
        try:
            pro_data = ApiProject.m.get(id=item["project_id"])
        except:
            return set_msg_and_return("不存在的项目id:{}".format(item["project_id"]))
        else:
            item["project_title"] = pro_data.title
    else:
        return set_msg_and_return("未填写项目id！")

    # 获取group_id_list， group_title_list
    group_id_list = []
    group_title_list = []

    if item["group_ids"] == "all":
        group_list = ApiGroup.m.filter(project=item["project_id"])
        for i in group_list:
            group_id_list.append(i.id)
            group_title_list.append(i.title)
    else:
        # 判断所有group_id是否存在
        group_id_list = str_to_list(item["group_ids"])
        for group_id in group_id_list:
            try:
                group_data = ApiGroup.m.get(id=int(group_id))
            except:
                return set_msg_and_return("不存在的分组id:{}".format(group_id))
            else:
                group_title_list.append("分组:{} -- {}".format(group_data.id, group_data.title))

    # 获取api_id_list， api_title_list
    api_id_list = str_to_list(item["api_ids"])
    api_title_list = []
    # 判断所有api_id是否存在
    for api_id in api_id_list:
        try:
            api_data = ApiApi.m.get(id=int(api_id))
        except:
            return set_msg_and_return("不存在的接口id:{}".format(api_id))
        else:
            api_title_list.append("接口:{} -- {}".format(api_data.id, api_data.title))

    # 解析group下的所有api,放到api_id_list中
    for group_id in group_id_list:
        apis = ApiApi.m.filter(group=int(group_id))
        for api in apis:
            api_id_list.append(str(api.id))

    api_id_list = list(set(api_id_list))  # 去重,防止group下的api和api重复
    if not api_id_list:
        return set_msg_and_return("分组id与接口id 清洗后没有符合的数据！")

    item["group_title_list"] = json_dumps(group_title_list) if group_title_list else ""
    item["api_title_list"] = json_dumps(api_title_list) if api_title_list else ""
    # return group_id_list, api_id_list
    return set_msg_and_return()


def case_ids_handle(item):
    def set_msg_and_return(msg=""):
        if msg:
            item["msg"] = msg
            item["isValid"] = False
            # item["case_title_list"] = json_dumps(['测试内容失效!:{}'.format(msg)])
            item["case_title_list"] = ""
        return msg, case_id_list

    case_title_list = []
    case_id_list = str_to_list(item["case_ids"])
    for case_id in case_id_list:
        try:
            case_data = ApiCase.m.get(id=int(case_id))
            case_title_list.append("用例:{} -- {}".format(case_data.id, case_data.title))
        except:
            return set_msg_and_return("不存在的用例id:{}".format(case_id))

    if not case_title_list:
        return set_msg_and_return("没有填写用例！")

    item["case_title_list"] = json_dumps(case_title_list) if case_title_list else ""
    return set_msg_and_return()


def get_all_projects(filter_item=None, **kwargs):
    if filter_item is None:
        filter_item = {}
        filter_item.update(kwargs)
    return ApiProject.m.filter(**filter_item).order_by("title")


# 每个项目 分组 接口 用例 统计 柱形图
def staticitem_project(req):
    # data = []
    project_title_list = []
    group_count_list = []
    api_count_list = []
    case_count_list = []

    cursor = connection.cursor()
    case_sql = "SELECT api_id, count(*) FROM api_case WHERE isDelete=false group by api_id;"
    cursor.execute(case_sql)
    cases = cursor.fetchall()

    projects = get_all_projects()
    for project in projects:
        project_title_list.append(project.title)
        groups = ApiGroup.m.filter(project_id=project.id)
        group_count = len(groups)
        api_count = 0
        case_count = 0
        for gourp in groups:
            apis = ApiApi.m.filter(group_id=gourp.id)
            api_count += len(apis)
            for api in apis:
                for case in cases:
                    if case[0] == api.id:
                        case_count += case[1]
        group_count_list.append(group_count)
        api_count_list.append(api_count)
        case_count_list.append(case_count)
        # data.append({project.title: [group_count, api_count, case_count]})
        # print("{}： 分组：{}个，接口{}个，用例{}个\n".format(
        #     project.title, group_count, api_count, case_count))
    # print("总计{}个用例".format(len(ApiCase.m.filter())))

    return response_200(
        project_title_list=project_title_list,
        group_count_list=group_count_list,
        api_count_list=api_count_list,
        case_count_list=case_count_list,
        all_count=len(ApiCase.m.filter()))


# 项目下任务数量统计、任务中包含总用例数量统计
def staticitem_task(req):
    data = []
    projects = get_all_projects()
    for project in projects:
        task_count = TestTask.m.filter(project_id=project.id).count()
        data.append({"name": project.title, "value": task_count})

    tasks = TestTask.m.filter()
    case_count_for_task = 0
    for task in tasks:
        count = len(str_to_list(task.case_ids))
        case_count_for_task += count

    return response_200(data=data, task_count=TestTask.m.filter().count(),
                        case_count_for_task=case_count_for_task)


# 每个项目 最近100次、10次成功情况/最近七天成功失败次数
def staticitem_recent(req):
    # 最近七天成功失败次数
    project_id = req.GET.get("project_id", "")
    filter_item = {}
    if project_id:
        filter_item["id"] = project_id

    days = []  # 最近七天  datetime时间格式，需要str才能得到 2021-07-02
    today = datetime.date.today()    # 获得今天的日期
    for i in range(7):
        day = today - datetime.timedelta(days=i)
        days.insert(0, day)

    colors = ["#5470c6", "#91cc75", "#fac858", "#ee6666",
              "#73c0de", "#3ba272", "#fc8452", "#9a60b4",
              "#ea7ccc", "#f173ac", "#f05b72",
              "#fdb933", "#f26522", "#ef5b9c"]
    colors_q = Queue()
    for color in colors:
        colors_q.put(color)

    titles = []
    series = []
    cursor = connection.cursor()
    projects = get_all_projects(filter_item)
    username = str(req.session.get("user"))
    for project in projects:
        if username not in str_to_list(project.users or ""):
            continue

        if colors_q.empty():
            for color in colors:
                colors_q.put(color)
        title_succeed = "{} - 成功数量".format(project.title)
        titles.append(title_succeed)
        title_fail = "{} - 失败数量".format(project.title)
        titles.append(title_fail)

        temp_succeed = {
            "name": title_succeed,
            "type": 'bar',
            "stack": project.title,
            "emphasis": {
                "focus": 'series'
            },
            "data": [],
            "itemStyle": {
                "normal": {
                    "label": {
                        "show": True,
                        "position": 'middle',
                        "textStyle": {
                            "color": 'black',
                            "fontSize": 24 if project_id else 12
                        }
                    },
                    "color": "#73c0de" if project_id else colors_q.get()
                }
            }
        }
        temp_fail = {
            "name": title_fail,
            "type": 'bar',
            "stack": project.title,
            "emphasis": {
                "focus": 'series'
            },
            "data": [],
            "itemStyle": {
                "normal": {
                    "label": {
                        "show": True,
                        "position": 'top',
                        "textStyle": {
                            "color": 'red',
                            "fontSize": 24 if project_id else 14
                        }
                    },
                    "color": "#ee6666" if project_id else colors_q.get()
                }
            }
        }
        for d in days:
            cursor.execute(
                "select count(*) from api_test_report where (c_date between '{}' and '{}') and project_title = '{}' and test_ret = 1".format(
                    str(d), str(d + datetime.timedelta(days=1)), project.title
                ))
            succed_count = str(cursor.fetchone()[0])
            temp_succeed["data"].append(succed_count)

            cursor.execute(
                "select count(*) from api_test_report where (c_date between '{}' and '{}') and project_title = '{}' and test_ret = 0".format(
                    str(d), str(d + datetime.timedelta(days=1)), project.title
                ))
            fail_count = cursor.fetchone()[0]
            temp_fail["data"].append(str(fail_count))

        series.append(temp_succeed)
        series.append(temp_fail)

    return response_200(series=series, titles=titles, days=days)


# 按人员统计 用例总数，近7周增加
def staticitem_user(req):
    days_raw = []   # ["2021-07-01", "2021-07-07", ...]
    days = []      # ["2021-07-01 -- 2021-07-07", "2021-07-01 -- 2021-07-07", ...]
    # 测试组全部成员，有限使用自定义的，没有自定义的，用全部的django用户
    try:
        users = str_to_list(ApiUser.m.get(type_id="1").users or "")
    except:
        users = []
        users_raw = User.objects.filter()
        for user in users_raw:
            users.append(user.username)

    series = []

    today = datetime.date.today()  # 获得今天的日期
    # 本周第一天和最后一天
    this_week_start = today - datetime.timedelta(days=today.weekday())
    # this_week_end = today + datetime.timedelta(days=6 - today.weekday())
    days_raw.append([this_week_start, today])
    for i in range(1, 7):
        # 上周第一天和最后一天
        last_week_start = today - datetime.timedelta(days=today.weekday() + 7 * i)
        last_week_end = today - datetime.timedelta(days=today.weekday() + 1 + 7 * (i-1))
        days_raw.append([last_week_start, last_week_end])
    # print(days)

    for user in users:
        temp = {
            "name": user,
            "type": 'line',
            "data": []
        }
        series.append(temp)

    cursor = connection.cursor()
    for day in days_raw:
        days.append("{} - {}".format(str(day[0]).replace("-", "/"), str(day[1]).replace("-", "/")))
        sql = "SELECT create_user, count(*) FROM api_case WHERE (c_date between '{}' and  '{}') and isDelete=false GROUP BY create_user;".format(
                str(day[0]), str(day[1] + datetime.timedelta(days=1)))
        # print(sql)
        cursor.execute(sql)
        rets = cursor.fetchall()
        for serie in series:
            for ret in rets:
                if ret[0] == serie["name"]:
                    serie["data"].append(ret[1])
                    break
            else:
                serie["data"].append(0)

    return response_200(series=series, users=users, days=days)


# 统计每个人创建的用例数量
def staticitem_user2(req):
    series = []
    cursor = connection.cursor()
    sql = "SELECT create_user_id, count(*) FROM api_case WHERE isDelete=false group by create_user_id;"
    cursor.execute(sql)

    for line in cursor.fetchall():
        series.append({"name": User.objects.get(id=line[0]).username or "无", "value": line[1]})

    return response_200(series=series)

# def get_host_ip():
#     try:
#         s = socket.socket()
#         s.connect(("www.baidu.com", 80))
#         ip = s.getsockname()[0]
#     finally:
#         s.close()
#     return ip



def strToBase64(s):
    '''
    将字符串转换为base64字符串
    :param s:
    :return:
    '''
    strEncode = base64.b64encode(s.encode('utf8'))
    return str(strEncode, encoding='utf8')


def base64ToStr(s):
    '''
    将base64字符串转换为字符串
    :param s:
    :return:
    '''
    strDecode = base64.b64decode(bytes(s, encoding="utf8"))
    return str(strDecode, encoding='utf8')

