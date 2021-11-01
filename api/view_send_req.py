from django.db import close_old_connections
from api.extensions.send_email import send_email
from api.extensions.workwx import WorkWeixinApi, send_workwx_user_group
from api.view_basic import *
from api.view_case import get_case_param, case_json_filed
# from api.view_test_task import api_ids_handle, case_ids_handle
from api.view_global_env import GlobalConfig
from api.extensions.workwx import send_workwx_user_group, send_workwx_group_chat
from retry import retry
import django
import requests
import copy
import re


def get_req_item(host, api_item, case_item):
    """
    :param host: host 是 host模型对象，host.host 才是域名
    :param api_item: 接口数据
    :param case_item: 用例数据
    :return: 只在发送请求中用到的参数
    """
    req_item = dict()
    host = host.host if host else ""
    req_item["url"] = host + case_item["url"]
    if host and case_item["url"]:   # host 结尾为/ url开头为/ 的时候处理为1个/
        if host[-1] == "/" and case_item["url"][0] == "/":
            req_item["url"] = host + case_item["url"][1:]

    req_item["method"] = api_item["method"]
    req_item["params"] = case_item["params"] or {}
    req_item["data"] = case_item["data"] or {}
    req_item["sample_data"] = case_item["sample_data"] or ""
    req_item["headers"] = case_item["headers"] or {}
    req_item["cookies"] = case_item["cookies"] or {}
    req_item["prefix"] = case_item["prefix"] or []
    req_item["rsgv"] = case_item["rsgv"] or []
    req_item["rsgh"] = case_item["rsgh"] or []
    req_item["set_global_cookies"] = case_item["set_global_cookies"]
    req_item["clear_global_cookies"] = case_item["clear_global_cookies"]
    req_item["asserts"] = case_item["asserts"] or []
    return req_item


def db_case_info_handle(case_info):
    """ 从库中获取的用例部分数据处理成 发送请求时用的格式 """

    case_item = model_to_dict(case_info)

    # 验证用例数据必须为json的字段,并转换成字典格式
    erro_msg = verify_is_json_and_switch(case_item, case_json_filed)
    return case_item, erro_msg


@require_http_methods(["POST"])
@login_required()
def send_req(req):
    # 1.全局配置处理
    htoc = HtmlTestOneCase(req)
    r_data = htoc.test_case()
    if r_data["msg"]:
        return response_400(**r_data)

    return response_200(**r_data)


# 立即执行任务
@require_http_methods(["GET"])
@login_required
def execute_task_now(req):

    task_id = req.GET.get("task_id", "")
    global_env_id = req.GET.get("global_env_id", "")
    if not task_id or not global_env_id:
        return response_400("未选择测试任务id 或 全局环境id")

    info = execute_task(req, task_id, global_env_id, trigger_way="手动测试")

    return response_200(info=info)


# 执行任务
def execute_task(req, task_id, global_env_id=None, trigger_way=None, task_group_id=None):

    close_old_connections()     # 清除失效链接

    try:
        task_info = TestTask.m.get(id=task_id)
        print("--开始任务：任务组id：{}：任务{}:{}， 全局环境id：{}， {}，{}".format(
            task_group_id, task_id, task_info.title, global_env_id, trigger_way, get_now_time()))
    except django.db.utils.InterfaceError as e:
        erro_msg = "运行任务 {} 出错! django.db.utils.InterfaceError: {}\n\n".format(task_id, e)
        send_workwx_user_group(erro_msg*3)
        response_400_raise_exception(erro_msg)
    except django.db.utils.OperationalError as e:
        erro_msg = "运行任务 {} 出错! django.db.utils.OperationalError: {}\n\n".format(task_id, e)
        send_workwx_user_group(erro_msg*3)
        response_400_raise_exception(erro_msg)
    except:
        erro_msg = "运行任务 {} 出错! 不存在的任务!\n\n".format(task_id)
        flag, msg = send_workwx_user_group(erro_msg*3)
        response_400_raise_exception(erro_msg, flag=flag, msg=msg)
    else:

        # 手动测试时需要指定一个环境；定时任务中不传环境，用的任务中的所有环境
        # if trigger_way == "手动测试":
        if global_env_id is not None:   # 手动测试
            bt = BatchTest(req, task_info, global_env_id, trigger_way, task_group_id)
            info = bt.batch_test()
            print("--任务完成：任务组id：{}：任务{}:{}， 全局环境id：{}， {}，{}".format(
                task_group_id, task_id, task_info.title, global_env_id, trigger_way, get_now_time()))
            return info
        # if global_env_id:
        #     global_env_id_list.append(global_env_id)
        # else:
        #     global_env_id_list = str_to_list(task_info.global_env_id_list)

        # global_env_id_list = []
        # for global_env_id in global_env_id_list:
        else:
            for global_env_id in str_to_list(task_info.global_env_id_list):
                bt = BatchTest(req, task_info, global_env_id, trigger_way, task_group_id)
                info = bt.batch_test()
                print("--任务完成：任务组id：{}：任务{}:{}， 全局环境id：{}， {}，{}".format(
                    task_group_id, task_id, task_info.title, global_env_id, trigger_way, get_now_time()))
                # return info

    close_old_connections()


class TestOneCase:

    def __init__(self, case_item, req_item, global_config, warning=None, global_save_flag=True):

        self.case_item = case_item

        self.req_item_raw = req_item  # requests时用到的参数
        self.req_item_real = copy.deepcopy(self.req_item_raw)  # 参数化之后的req_item

        self.global_config = global_config
        self.case_variable_list = []  # 当前用例环境变量

        self.msg = ""  # 致命错误
        self.warning = warning or ""  # 警告错误, 一般只有页面单接口测试会用到

        self.global_save_flag = global_save_flag    # 是否保存全局配置(入库)

        self.num = 1    # 变量方法中数字自增长初始值

        self.res_part = {

            "successful_response_flag": None,  # 1.请求成功才会有下列的参数
            "fail_req_msg": None,  # 请求失败的原因

            "res_time": None,  # 响应时间
            "status_code": None,  # 响应状态码
            "res_headers": None,  # 响应头
            "res_cookies": None,  # 响应cookies
            "res_body_is_json": None,  # 2.响应体是是json格式，res_succeed才会有断言,后置
            "res_body": None,  # 响应体是json格式则为json格式,否则为text

            # asserts_flag: 此用例最终断言结果，
            # Flase的情况: 当1,2为失败; 当有一条断言是失败的则为此值为失败;
            # True的情况: 所有断言都通过
            "asserts_flag": None,

        }

    def get_r_data(self):

        return {
            "case_id": self.case_item["id"],
            "case_title": self.case_item["title"],
            "case_desc": self.case_item["desc"],

            "msg": self.msg,  # 如果请求失败ret为Flase，写入异常信息
            "warning": self.warning,  # 警告错误, 页面单接口测试才有值的字段

            "req_item_raw": self.req_item_raw,      # 未处理的参数
            "req_item_real": self.req_item_real,    # 处理后的实际参数

            "global_config": self.global_config.get_global_config_dict(),   # 全局配置信息
            "case_variable": self.case_variable_list,    # 当前用例变量

            "res_part": self.res_part               # 响应中的参数
        }

    def test_case(self):
        # 0. 样例数据和全局变量 融合到一起,再从中取出本次用到的参数

        # sample_datas = self.req_item_raw["sample_data"] or [{}]     # 没有样例数据则添加一个{},走一次循环
        try:
            self.case_variable_list = self.merge_globalVariable_and_sampleData()
            if self.msg:
                return self.get_r_data()

            for index, case_variable in enumerate(self.case_variable_list):

                # 1. 从前置中获取参数与变量,放到本轮当前用例变量中
                self.prefix_handle(case_variable)
                if self.msg:
                    return self.get_r_data()

                # 2. 全局变量 和 样例数据一起参数化
                self.parameterization_handle(case_variable)
                if self.msg:
                    return self.get_r_data()

                # 3. 全局header & 全局cookie处理
                self.global_header_handle()
                if self.msg:
                    return self.get_r_data()

                self.global_cookie_handle()
                if self.msg:
                    return self.get_r_data()

                # 4. 发送请求
                self.send_req()
                if not self.res_part["successful_response_flag"]:
                    return self.get_r_data()

                # 5. 处理断言
                self.assert_handle()

                # 6. 后置处理
                self.rsgv_handle()
                self.rsgh_handle()
                self.rsgc_handle()
                # 断言失败或到了最后一条才进行后置处理，直接返回结果
                # if not self.res_part["asserts_flag"] or index == len(case_variable_list) - 1:
                if not self.res_part["asserts_flag"]:
                    break
        except Exception as e:
            self.msg = "单用例执行时未知异常：{}".format(e)
        # 7.最终数据处理

        return self.get_r_data()

    def merge_globalVariable_and_sampleData(self):

        """
        global_variable:
            [
                {
                    "key": "id",
                    "value": [666],
                    "description": "description",
                    "enabled": true
                },
                {
                    "key": "two",
                    "value": [two1, two2, two3, two4],
                    "description": "description",
                    "enabled": true
                },
                ...
            ]

        sample_data_json:
            [
                {
                    "one": "1",
                    "two": "2",
                    "three": "3"
                },
                {
                    "one": "11",
                    "two": "22",
                    "three": "33"
                },
                {
                    "one": "",
                    "two": "",
                    "three": "333"
                },
                ...
            ]

        1/2. case_variable_dict :(全局变量与样例数据融合, 相同的key, 会优先样例数据)
            {
                "id": [666],
                "one": ["1", "1"],
                "two": ["2", "22"],
                "three": ["3", "33", "333"],
                ...(此次用不到的参数略)
            }

        3. case_variable_keys: 根据用例中用正则查找出来的变量名称
            ["id", "one", "two", "three"]

        4. 根据case_variable_keys,从case_variable_dict 取出要用到的数据
            {
                "id": [666]
                "one": ["1", "1"],
                "two": ["2", "22"],
                "three": ["3", "33", "333"],
            }
        5. case_variable_list :将case_variable_dict转换成最终格式
            1. 以长度最长的值,做为循环的次数,如样例数据中的three,循环3次
            2. 如果有变量的值的长度 小于最长长度,则补位空""
            3. 变量只有一个值的情况下,认定为固定参数,每次数据都为这个值

            [
                {
                    "id": 666,
                    "one": "1",
                    "two": "2",
                    "three": "3"
                },
                {
                    "id": 666,
                    "one": "11",
                    "two": "22",
                    "three": "33"
                },
                {
                    "id": 666,
                    "one": "",
                    "two": "",
                    "three": "333"
                }
            ]
        """

        case_variable_dict = {}
        # 1. 全局变量格式转换
        try:
            # 如果使用全局变量
            if self.global_config.variable is not None:
                for i in self.global_config.variable.params:
                    if i["enabled"]:
                        case_variable_dict[i["key"]] = copy.deepcopy(i["value"])
        except Exception as e:
            self.msg = "全局变量数据处理时出错，请检查数据是否正确！{}".format(e)

        # print(1, json_dumps_indent4(case_variable_dict))

        # 2. 样例数据格式转换
        try:
            sample_data_json = self.req_item_raw["sample_data"]
            if sample_data_json:
                keys = sample_data_json[0].keys()
                for i in keys:
                    case_variable_dict[i] = []   # 同key情况下, 样例数据覆盖全局数据

                for item in sample_data_json:
                    for i in keys:
                        case_variable_dict[i].append(item[i])

        except Exception as e:
            self.msg = "样例数据处理时出错，请检查数据是否正确！{}".format(e)

        # print(2, json_dumps_indent4(case_variable_dict))

        # 3. 取出本次用例用到的数据
        item_raw = {
            "url": self.req_item_raw["url"],
            "params": self.req_item_raw["params"],
            "data": self.req_item_raw["data"],
            # "sample_data": self.req_item_raw["sample_data"],
            "headers": self.req_item_raw["headers"],
            # "cookies": self.req_item_raw["cookies"],
            # "prefix": self.req_item_raw["prefix"],
            # "rsgv": self.req_item_raw["rsgv"],
            "asserts": self.req_item_raw["asserts"]
        }
        case_variable_keys = []
        for k, v in item_raw.items():
            parttern = re.compile(r"[{][{](.*?)[}][}]", re.S)  # 最小匹配模式
            # parttern = re.compile(r"[{][{](.*)[}][}]", re.S)     # 贪婪模式
            ret = re.findall(parttern, json_dumps(v))        # 结果为list格式
            # print(33, k, ret)
            case_variable_keys += ret
        case_variable_keys = list(set(case_variable_keys))

        # print(3, json_dumps_indent4(case_variable_keys))

        # 4. 根据case_variable_keys,从case_variable_dict 取出要用到的数据
        case_variable_real_dict = {}
        for key in case_variable_keys:
            v = case_variable_dict.get(key, "")
            if v:
                case_variable_real_dict[key] = v

        # print(4, json_dumps_indent4(case_variable_real_dict))

        # 5. case_variable_list: 将case_variable_dict转换成最终格式
        # ① 所有变量的值 都补充成最长值的长度,补充字符""
        # ② 如果这个变量值的长度为1, 则补充字符为v[0]
        case_variable_list = []
        case_variable_real_keys = case_variable_real_dict.keys()
        max_len = 0
        for v in case_variable_real_dict.values():
            if len(v) > max_len:
                max_len = len(v)
        for v in case_variable_real_dict.values():
            len_v = len(v)
            if len_v < max_len:
                for i in range(0, max_len - len(v)):
                    if len_v == 1:
                        v.append(v[0])
                    else:
                        v.append("")
        for i in range(max_len):
            item = {}
            for key in case_variable_real_keys:
                item[key] = case_variable_real_dict[key][i]
            case_variable_list.append(item)

        # print(5, json_dumps_indent4(case_variable_list))
        # print(6, json_dumps_indent4(self.global_config.variable.params))

        # 至少有一条数据循环一次
        return case_variable_list or [{}]

    def parameterization_handle(self, case_variable):
        """ 参数化 变量与变量方法 """

        def _parameterization_handle(dict1, dict2):
            new_dict1 = {}
            try:
                for k, v in dict1.items():
                    new_dict1[k] = json_dumps(v)  # 所有python格式转换成json字符串

                for i in new_dict1.keys():
                    if new_dict1[i]:

                        # 替换参数化变量:使用dict2中的key的值,替换dict1中所有values中的{{key}}"
                        for k, v in dict2.items():
                            key = "{{" + k + "}}"
                            # 含有引号时特殊处理
                            new_dict1[i] = new_dict1[i].replace(key, str(v).replace('"', '\\"'))
                        # print(0, new_dict1[i])

                        # 替换变量方法
                        key1 = "{@timestamp}"   # 当前时间戳
                        key2 = "{@date}"        # 当前日期
                        key3 = "{@num}"         # 自增长数字

                        # if key1 in new_dict1[i]:
                        new_dict1[i] = new_dict1[i].replace(key1, str(int(round(time.time() * 1000))))
                        # print(1, new_dict1[i])
                        # if key2 in new_dict1[i]:
                        day_add = re.compile(r'[{][@]date[+](\d+)[}]', re.S)
                        day_subtract = re.compile(r'[{][@]date[-](\d+)[}]', re.S)
                        day_add_nums = re.findall(day_add, new_dict1[i])
                        day_subtract_nums = re.findall(day_subtract, new_dict1[i])

                        today = datetime.date.today()  # 获得今天的日期 ==>  2021-04-12

                        # 替换今天
                        new_dict1[i] = new_dict1[i].replace(key2, str(today))
                        # print(2, new_dict1[i])
                        # 替换日期加的操作
                        for num in day_add_nums:
                            d = today + datetime.timedelta(days=int(num))
                            # print("{@date+" + num + "}")
                            new_dict1[i] = new_dict1[i].replace("{@date+" + num + "}", str(d))
                        # print(3, new_dict1[i])
                        # 替换日期减的操作
                        for num in day_subtract_nums:
                            d = today - datetime.timedelta(days=int(num))
                            # print("{@date-" + num + "}")
                            new_dict1[i] = new_dict1[i].replace("{@date-" + num + "}", str(d))
                        # print(4, new_dict1[i])

                        while key3 in new_dict1[i]:
                            new_dict1[i] = new_dict1[i].replace(key3, str(self.num), 1)
                            self.num += 1
                        # print(5, new_dict1[i])

                for k, v in new_dict1.items():
                    new_dict1[k] = json.loads(v)  # 在转换成python数据格式

                return "", new_dict1

            except Exception as e:
                return "参数化时出错:{}".format(e), ""
        item_raw = {
            "url": self.req_item_raw["url"],
            "params": self.req_item_raw["params"],
            "data": self.req_item_raw["data"],
            # "sample_data": self.req_item_raw["sample_data"],
            "headers": self.req_item_raw["headers"],
            # "cookies": self.req_item_raw["cookies"],
            # "prefix": self.req_item_raw["prefix"],
            # "rsgv": self.req_item_raw["rsgv"],
            "asserts": self.req_item_raw["asserts"]
        }

        msg, item = _parameterization_handle(item_raw, case_variable)
        if msg:
            self.msg = msg
        else:
            self.req_item_real.update(item)

    def parameterization_handle2(self, sample_data=None):
        """
        :param 将发送请求时self.req_item中所有参数{{xxx}}值都参数化
        :return: 参数化替换完成的self.req_item
        """

        def _parameterization_handle(dict1, dict2):
            """
                "使用dict2中的key的值,替换dict1中所有values中的{{key}}"
            """

            new_dict1 = {}

            try:
                for k, v in dict1.items():
                    new_dict1[k] = json_dumps(v)  # 所有python格式转换成json字符串

                for j in new_dict1.keys():
                    if new_dict1[j]:
                        for k, v in dict2.items():
                            key = "{{" + k + "}}"
                            if key in new_dict1[j]:
                                new_dict1[j] = new_dict1[j].replace(key, v)

                for k, v in new_dict1.items():
                    new_dict1[k] = json.loads(v)  # 在转换成python数据格式

                return {
                    "msg": "",
                    "item": new_dict1
                }

            except Exception as e:
                return {
                    "msg": "参数化时出错:{}".format(e),
                    "item": ""
                }

        item_raw = {
            "url": self.req_item_raw["url"],
            "params": self.req_item_raw["params"],
            "data": self.req_item_raw["data"],
            # "sample_data": self.req_item_raw["sample_data"],
            "headers": self.req_item_raw["headers"],
            # "cookies": self.req_item_raw["cookies"],
            # "prefix": self.req_item_raw["prefix"],
            # "rsgv": self.req_item_raw["rsgv"],
            # "asserts": self.req_item_raw["asserts"]
        }

        """
            global_variable:[
                        {
                            "key": "UID",
                            "value": "UNEYHDJH",
                            "description": "gj-api-勿删-UID",
                            "enabled": true
                        }
                    ]
            case_variable:{
                            "key": "UID",
                            "value": "UNEYHDJH",
                        }

            sample_data:{
                            "key": "UID",
                            "value": "UNEYHDJH",
                        }
        """
        if self.global_config.variable is not None:        # 添加环境变量到当前用例变量
            for i in self.global_config.variable.params:
                try:
                    if i["enabled"]:
                        self.case_variable[i["key"]] = i["value"]  # 这里组装成dict格式数据,有重复的key以后面的为准
                except Exception as e:
                    self.msg = "全局变量缺少enabled字段！{}".format(e)
                    return
        if sample_data:
            self.case_variable.update(sample_data)     # 同key时，用样例参数的数据

        ret = _parameterization_handle(item_raw, self.case_variable)
        if ret["msg"]:
            self.msg = ret["msg"]
        else:
            self.req_item_real.update(ret["item"])

    def prefix_handle(self, case_variable):
        """
        case_variable:{
                        key:value,
                        key:value
                        ...
                    }
        传入值：prefix_status  prefix_case_id  prefix_set_var_name prefix_key
        如果启用，需要传出的值：
            prefix_resbody：响应体,
            prefix_real_value：实际值,
            prefix_erro：错误信息"""

        # self.req_item_real["prefix"] = copy.deepcopy(self.req_item_raw["prefix"])

        # 根据case_id分类
        prefix_item = {}    # { case_id:[prefix, prefix], case_id:[prefix, prefix] }

        for prefix in self.req_item_real["prefix"]:
            if prefix["prefix_case_id"].strip():    # case_id为空的直接不要
                prefix_item.setdefault(prefix["prefix_case_id"], []).append(prefix)

        for case_id, prefixs in prefix_item.items():

            prefix_tmp = dict()
            prefix_tmp["prefix_res_body"] = None
            prefix_tmp["prefix_real_value"] = None
            prefix_tmp["prefix_erro"] = None

            # 同一个用例id如果没有启用状态的，没必要走后面流程
            prefix_status_flag = False

            for prefix in prefixs:
                if prefix["prefix_status"] == "1":  # 判断是否启用  1表示启用
                    prefix_status_flag = True

            if prefix_status_flag:

                # 获取用例数据,接口数据
                try:
                    case_data = ApiCase.m.get(pk=case_id)
                except Exception as e:
                    prefix_tmp["prefix_erro"] = "获取不到此用例:{}:{}".format(
                        case_id, e)
                else:
                    api_data = ApiApi.m.get(pk=case_data.api_id)
                    api_item = model_to_dict(api_data)

                    case_item, erro_msg = db_case_info_handle(case_data)
                    if erro_msg:
                        prefix_tmp["prefix_erro"] = erro_msg
                        continue

                    req_item = get_req_item(self.global_config.host, api_item, case_item)
                    toc = TestOneCase(case_item, req_item, self.global_config)
                    r_data = toc.test_case()

                    if not r_data["msg"]:

                        if r_data["res_part"]["successful_response_flag"]:

                            if r_data["res_part"]["res_body_is_json"]:

                                prefix_tmp["prefix_res_body"] = r_data["res_part"]["res_body"]
                                self.prefix_handle2(case_variable, r_data["res_part"]["res_body"],
                                                    prefixs, prefix_tmp)
                                # prefix_handle3里已经更新数据了，不必在走后面的更新
                                continue

                            else:
                                prefix_tmp["prefix_res_body"] = r_data["res_part"]["res_body"]
                                prefix_tmp["prefix_erro"] = "响应不为json格式，不支持处理！"

                        else:
                            prefix_tmp["prefix_erro"] = "前置错误:{}".format(r_data["res_part"]["fail_req_msg"])

                    else:
                        prefix_tmp["prefix_erro"] = "前置错误:{}".format(r_data["msg"])

            # 能走到这的都要更新prefix数据
            for prefix in prefixs:
                prefix.update(**prefix_tmp)

        # 回到原来的格式
        prefix_item2 = []
        for case_id in prefix_item:
            for prefix in prefix_item[case_id]:
                prefix_item2.append(prefix)

        self.req_item_real["prefix"] = prefix_item2

    def prefix_handle2(self, case_variable, res_body, prefixs, prefix_tmp):

        for prefix in prefixs:

            prefix_tmp = copy.deepcopy(prefix_tmp)

            if not prefix["prefix_key"]:
                prefix_tmp["prefix_erro"] = "没有填写变量键"
                prefix.update(**prefix_tmp)
                continue

            try:
                value = eval("res_body" + prefix["prefix_key"])

            except Exception as e:
                prefix_tmp["prefix_erro"] = "变量键找不到或格式有误:{}".format(e)

            else:
                if type(value) == str or \
                                type(value) == int or \
                                type(value) == float:  # 如果实际值是int，float格式就转化成str格式，方便后续判断
                    value = str(value)

                    prefix_tmp["prefix_real_value"] = value

                    case_variable[prefix["prefix_set_var_name"]] = value  # 添加到当前用例变量中

                else:
                    prefix["prefix_real_value"] = \
                        "变量值只能是数字或字符串,当前格式为:{}:{}".format(type(value), value)

            prefix.update(**prefix_tmp)

    def global_header_handle(self):
        try:
            if self.global_config.header is not None:
                global_headers = copy.deepcopy(self.global_config.header.params)
                global_headers.update(**self.req_item_real["headers"])
                self.req_item_real["headers"] = global_headers
        except Exception as e:
            self.msg = "全局请求头处理时出错，请检查全局cookie数据是否正确！{}".format(e)

    def global_cookie_handle(self):
        try:
            if self.global_config.cookie is not None:
                global_cookies = copy.deepcopy(self.global_config.cookie.params)
                global_cookies.update(self.req_item_real["cookies"])
                self.req_item_real["cookies"] = global_cookies

        except:
            self.msg = "全局cookie处理时出错，请检查全局cookie数据是否正确！"

    def send_req(self):
        method = self.req_item_real['method']
        url = self.req_item_real['url']
        params = self.req_item_real['params']  # 键值对格式入参
        data = self.req_item_real['data']  # json格式入参
        headers = self.req_item_real['headers']
        cookies = self.req_item_real['cookies']

        self.res_part["successful_response_flag"] = False
        try:
            if method.upper() == "GET":
                p = copy.deepcopy(data)
                p.update(**params)  # get方式合并params和data

                # 只有在发生请求异常(超时)的情况下重试,否则报错; tries=3:一共请求三次
                @retry(requests.exceptions.RequestException, tries=3)
                # @retry(exceptions=IOError, tries=3)
                def requests_get():
                    res = requests.get(url, params=p, headers=headers, cookies=cookies, timeout=settings.TIME_OUT)
                    return res

                self.res = requests_get()
                self.res_part["successful_response_flag"] = True

            elif method.upper() == "POST":
                Content_Type = headers.get("Content-Type", "")
                Accept = headers.get("Accept", "")

                @retry(exceptions=requests.exceptions.RequestException, tries=3)
                def requests_post():
                    if Content_Type == "application/json" or Accept == "application/json":
                        # json参数填写字典自动转换,并且响应头自动改为application/json
                         res = requests.post(
                            url, params=params, headers=headers,
                            cookies=cookies, json=data, timeout=settings.TIME_OUT)
                    else:
                        res = requests.post(
                            url, params=params, headers=headers,
                            cookies=cookies, data=data, timeout=settings.TIME_OUT)

                    return res

                self.res = requests_post()
                self.res_part["successful_response_flag"] = True

            else:

                self.res_part["asserts_flag"] = False
                self.res_part["fail_req_msg"] = "只支持Get,Post，不支持{}!".format(method)

        except requests.exceptions.MissingSchema:
            self.res_part["asserts_flag"] = False
            self.res_part["fail_req_msg"] = "http协议不正确！"

        except requests.exceptions.RequestException:
            self.res_part["asserts_flag"] = False
            self.res_part["fail_req_msg"] = "请求超时! timeout={}".format(settings.TIME_OUT)

        except Exception as e:
            self.res_part["asserts_flag"] = False
            self.res_part["fail_req_msg"] = "url:{}, 发送请求时出错:{}".format(url, e)

        else:
            if self.res_part["successful_response_flag"]:
                self.res_part["status_code"] = self.res.status_code  # 响应码
                self.res_part["time"] = str(self.res.elapsed.microseconds / 1000000) + "ms"  # 响应时间
                # res.headers是其他dict格式，需要转换成python标准dict格式
                self.res_part["res_headers"] = dict(self.res.headers)
                self.res_part["res_cookies"] = dict(self.res.cookies)
                # self.res_part["res_cookies"] = {"11": "aa", "22": "bb"}

                try:
                    self.res_part["res_body"] = self.res.json()
                    self.res_part["res_body_is_json"] = True
                except:
                    self.res_part["res_body"] = self.res.text
                    self.res_part["res_body_is_json"] = False

    def assert_handle(self):

        default_asserts = {
            "assert_status": "1",  # 断言键
            "assert_key": "",  # 断言键
            "assert_method": "0",  # 断言方式
            "assert_expect_value": "200",  # 断言期望值
        }

        # 如果有断言,判断是否有启用的断言,
        # 如果有启用断言:深拷贝所有断言信息,
        # 如果没有启用断言:则追加默认断言，判断状态码
        # 如果没有断言,则为默认断言,判断状态码
        if len(self.req_item_real['asserts']) > 0:
            for asserts in self.req_item_real['asserts']:
                if asserts["assert_status"] == "1":
                    break
            else:
                self.req_item_real["asserts"].append(default_asserts)
        else:
            self.req_item_real["asserts"].append(default_asserts)

        # 验证断言信息,并判断所有断言最终结果
        for assert_item in self.req_item_real["asserts"]:
            if assert_item["assert_status"] == "1":  # 如果断言是启用状态
                vro = VerifyResOne(assert_item, self.res)
                vro.verify_res_one()
                vro.update_item()
                if not assert_item["assert_ret"]:
                    self.res_part["asserts_flag"] = False

        if self.res_part["asserts_flag"] is None:
            self.res_part["asserts_flag"] = True

    def rsgv_handle(self):
        """
            后置操作:响应体中的参数设置到全局变量中
            {
                "rsgv_status":"1表示启用",
                "rsgv_name":"变量名称",
                "rsgv_set_method":"设置变量的方式",
                "rsgv_key":"变量路径",

                "rsgv_real_value":"变量实际值",
                "rsgv_erro_msg":"错误信息",
                "rsgv_ret":"设置结果",
            }
        """

        for rsgv in self.req_item_real["rsgv"]:

            # 判断是否启用  1表示启用
            if rsgv["rsgv_status"] == "1":

                rsgv_set_method = rsgv.get("rsgv_set_method", "1")  # 老用例可能没这个值
                rsgv["rsgv_ret"] = False  # 设置结果
                rsgv["rsgv_real_value"] = ""  # 实际值
                rsgv["rsgv_erro_msg"] = ""  # 错误信息

                if self.global_config.variable is None:
                    rsgv["rsgv_erro_msg"] = "设置失败: 未选择全局变量所以无法设置!"
                    continue

                if not rsgv["rsgv_name"]:
                    rsgv["rsgv_erro_msg"] = "设置失败:没有填写变量名!"
                    continue

                if not rsgv["rsgv_key"]:
                    rsgv["rsgv_erro_msg"] = "设置失败:没有填写变量键!"
                    continue

                if not self.res_part["successful_response_flag"]:
                    rsgv["rsgv_erro_msg"] = "设置失败:请求失败,无法设置!"
                    continue

                if not self.res_part["res_body_is_json"]:
                    rsgv["rsgv_real_value"] = "设置失败:响应体不是json格式,无法设置!"
                    continue

                elif rsgv_set_method in ["1", "2"]:
                    try:
                        rsgv["rsgv_real_value"] = eval("self.res_part['res_body']" + rsgv["rsgv_key"])
                        rsgv["rsgv_ret"] = True
                    except Exception as e:
                        rsgv["rsgv_erro_msg"] = "设置失败:变量键找不到或格式有误:{}".format(e)
                        continue

                if rsgv_set_method in ["3", "4"]:  # 代码断言

                    try:
                        # self.res.json()  # 响应信息
                        # rsgv["rsgv_ret"] = True  # 设置结果
                        # rsgv["rsgv_real_value"] = "real_valuereal_valuereal_value"  # 实际值
                        # rsgv["rsgv_erro_msg"] = "erro_msgerro_msgerro_msgerro_msg"  # 错误信息
                        exec(rsgv["rsgv_key"])

                        # print(rsgv["rsgv_ret"])
                        # print(rsgv["rsgv_real_value"])
                        # print(rsgv["rsgv_erro_msg"])
                    except Exception as e:
                        rsgv["rsgv_erro_msg"] = "{}".format(e)
                        rsgv["rsgv_ret"] = False
                        continue

                if rsgv["rsgv_ret"]:
                    # 如果实际值是int，float格式就转化成str格式，方便后续判断
                    if type(rsgv["rsgv_real_value"]) == str or type(rsgv["rsgv_real_value"]) == int or type(rsgv["rsgv_real_value"]) == float:
                        rsgv["rsgv_real_value"] = str(rsgv["rsgv_real_value"])

                        set_method = True if rsgv_set_method in ["1", "3"] else False
                        self.global_config.global_variable_append_and_save(
                            rsgv["rsgv_name"], rsgv["rsgv_real_value"], set_method, self.global_save_flag)
                    else:
                        rsgv["rsgv_erro_msg"] = "设置失败:变量值只能是数字或字符串," \
                                                  "当前格式为:{}:{}".format(
                            type(rsgv["rsgv_real_value"]), rsgv["rsgv_real_value"])

    def rsgh_handle(self):
        """
            后置操作:响应体中的参数设置到全局请求头中
            {
                "rsgh_status":"1表示启用",
                "rsgh_name":"变量名称",
                "rsgh_set_method":"设置变量的方式",
                "rsgh_key":"变量路径",

                "rsgh_real_value":"变量实际值",
                "rsgh_erro_msg":"错误信息",
                "rsgh_ret":"设置结果",
            }
        """
        for rsgh in self.req_item_real["rsgh"]:
            # 判断是否启用  1表示启用
            if rsgh["rsgh_status"] == "1":

                rsgh["rsgh_set_method"] = rsgh.get("rsgh_set_method", "1")  # 老用例可能没这个值
                rsgh["rsgh_ret"] = False  # 设置结果
                rsgh["rsgh_real_value"] = ""  # 实际值
                rsgh["rsgh_erro_msg"] = ""  # 错误信息

                if self.global_config.header is None:
                    rsgh["rsgh_erro_msg"] = "设置失败: 未选择全局请求头所以无法设置!"
                    continue

                if not rsgh["rsgh_name"]:
                    rsgh["rsgh_erro_msg"] = "设置失败:没有填写变量名!"
                    continue
                if not rsgh["rsgh_key"]:
                    rsgh["rsgh_erro_msg"] = "设置失败:没有填写变量键!"
                    continue

                if not self.res_part["successful_response_flag"]:
                    rsgh["rsgh_erro_msg"] = "设置失败:请求失败,无法设置!"
                    continue

                if not self.res_part["res_body_is_json"]:
                    rsgh["rsgh_erro_msg"] = "设置失败:响应体不是json格式,无法设置!"
                    continue

                try:
                    if rsgh["rsgh_set_method"] == "1":  # 根据变量路径找对应值
                        rsgh["rsgh_real_value"] = eval("self.res_part['res_body']" + rsgh["rsgh_key"])
                        rsgh["rsgh_ret"] = True
                    elif rsgh["rsgh_set_method"] == "2":  # 代码断言
                        try:
                            exec(rsgh["rsgh_key"])
                            # print(rsgh["rsgh_ret"])
                            # print(rsgh["rsgh_real_value"])
                            # print(rsgh["rsgh_erro_msg"])
                        except Exception as e:
                            rsgh["rsgh_erro_msg"] = "{}".format(e)
                            rsgh["rsgh_ret"] = False
                            continue
                    else:
                        rsgh["rsgh_real_value"] = "不支持的设置方式 rsgh_set_method:{}".format(rsgh["rsgh_set_method"])
                        return
                except Exception as e:
                    rsgh["rsgh_erro_msg"] = "设置失败:变量键找不到或格式有误:{}".format(e)
                else:
                    value = rsgh["rsgh_real_value"]
                    # 如果实际值是int，float格式就转化成str格式，方便后续判断
                    if type(value) == str or type(value) == int or type(value) == float:
                        self.global_config.global_header_update_and_save({rsgh["rsgh_name"]: value}, self.global_save_flag)
                    else:
                        rsgh["rsgh_ret"] = False
                        rsgh["rsgh_erro_msg"] = "设置失败:变量值只能是数字或字符串," \
                                                  "当前格式为:{}:{}".format(type(value), value)

    def rsgc_handle(self):
        """
            # 后置操作:响应cookies设置到全局cookie中
        """

        if self.res_part["successful_response_flag"]:   # 成功的请求才会有cookies

            if self.case_item["set_global_cookies"]:
                self.global_config.global_cookie_update_and_save(self.res_part['res_cookies'], self.global_save_flag)

            if self.case_item["clear_global_cookies"]:
                self.global_config.global_cookie_clear_params(self.global_save_flag)


class VerifyResOne:
    """
    # 验证每一个断言的类

    0	状态码
    1	=   15
    2	！=
    4	>=
    6	<=
    7	in
    8	not in
    20	~in
    9	len =
    10	len !=
    12	len >=
    14	len <=
    16	[]或{}中的元素in对比
    17	[]或{}中的元素~in对比
    18	[]不计较顺序对比
    19	{}中的键对比
    90	代码断言
    """
    # 一般关系
    general_handle_list = ["1", "2", "4", "6", "7", "8", "20"]
    # len关系
    len_handle_list = ["9", "10", "12", "14"]
    # 特殊关系
    specific_handle_list = ["16", "17", "18", "19", "90"]

    def __init__(self, item, res):
        """
        验证格式-->取出assert的值-->判断结果
        :param item: 用户输入的断言数据
        :param res:  响应结果， 需要相应体：res.json()
        :return:
        """
        self.assert_key = item["assert_key"].strip()  # 断言键
        self.assert_method = item["assert_method"].strip()  # 断言方式
        self.assert_expect_value = item["assert_expect_value"].strip()  # 期望值
        self.assert_real_value = None  # 实际值
        self.assert_erro = None  # 错误信息
        self.assert_ret = False  # 断言结果
        self.res = res           # 响应信息
        self.item = item

    # 验证每一个断言
    def verify_res_one(self):

        if self.assert_method == "90":  # 代码断言
            try:
                # eval(self.assert_expect_value)
                exec(self.assert_expect_value)
                # self.res.json()  # 响应信息
                # self.assert_real_value = None  # 实际值
                # self.assert_erro = None  # 错误信息
                # self.assert_ret = False  # 断言结果

                # self.assert_real_value = self.res.json()["code"]
                # self.assert_ret = True if self.assert_real_value == "200" else False
                # if not self.assert_ret:
                #     self.assert_erro = "code不等于200"
            except Exception as e:
                self.assert_erro = "{}".format(e)
            return

        if self.assert_method == "0":
            self.assert_ret = self.assert_expect_value == str(self.res.status_code)
            self.assert_real_value = self.res.status_code

        else:
            try:
                self.res.json()
            except:
                self.assert_erro = "响应体非json格式，无法使用此方法断言！"
                return
            self.get_assert_real_value()
            if self.assert_erro:
                return
            try:

                if self.assert_method == "1":

                    # 分为true，flase，null，空""和字符串四种情况
                    if self.assert_expect_value == "true":
                        self.assert_ret = self.assert_ret = self.assert_real_value == "true"
                        if not self.assert_ret:
                            self.assert_ret = self.assert_real_value == True

                    elif self.assert_expect_value == "flase":
                        self.assert_ret = self.assert_ret = self.assert_real_value == "flase"
                        if not self.assert_ret:
                            self.assert_ret = self.assert_real_value == False

                    elif self.assert_expect_value == "null":
                        self.assert_ret = self.assert_ret = self.assert_real_value == "null"
                        if not self.assert_ret:
                            self.assert_ret = self.assert_real_value is None

                    else:
                        self.assert_ret = self.assert_real_value == self.assert_expect_value

                elif self.assert_method == "2":
                    # 分为true，flase，null，空""和字符串四种情况

                    if self.assert_expect_value == "true":
                        self.assert_ret = self.assert_ret = self.assert_real_value != "true"
                        if not self.assert_ret:
                            self.assert_ret = self.assert_real_value != True

                    elif self.assert_expect_value == "flase":
                        self.assert_ret = self.assert_ret = self.assert_real_value != "flase"
                        if not self.assert_ret:
                            self.assert_ret = self.assert_real_value != False

                    elif self.assert_expect_value == "null":
                        self.assert_ret = self.assert_ret = self.assert_real_value != "null"
                        if not self.assert_ret:
                            self.assert_ret = self.assert_real_value is not None

                    else:
                        self.assert_ret = self.assert_real_value != self.assert_expect_value

                elif self.assert_method in self.general_handle_list:
                    self.general_handle()

                elif self.assert_method in self.len_handle_list:
                    self.len_handle()

                elif self.assert_method in self.specific_handle_list:
                    self.specific_handle()

                else:
                    self.assert_ret = False
                    self.assert_erro = "未选择断言方式或无效断言方式"

            except ValueError:
                self.assert_erro = "期望结果和实际结果数据类型不匹配"
            except Exception as e:
                self.assert_erro = "断言无法判断的情况:{}".format(e)

        if not self.assert_ret and not self.assert_erro:
            self.assert_erro = "期望结果与实际结果不一致"

    def update_item(self):

        try:
            # 尝试将实际结果转化成json格式
            if type(self.assert_real_value) == dict or type(self.assert_real_value) == list:
                self.assert_real_value = json_dumps(self.assert_real_value)
        except Exception as e:
            pass

        assert_item_template = {
            "assert_real_value": self.assert_real_value,  # 断言实际的值
            "assert_erro": self.assert_erro,  # 1.如果断言报错，存入错误信息   2, 如果断言结果为False但没报错，erro为结果不一致
            "assert_ret": self.assert_ret,  # 断言结果
            # "assert_key": None,           # 断言键
            # "assert_method": None,        # 断言方式
            # "assert_expect_value": None,  # 断言期望值
        }

        self.item.update(assert_item_template)

    # 获取响应中对应的实际值
    def get_assert_real_value(self):
        # 通过eval从响应结果中获取值
        try:
            # 没写断言键默认表示全部
            if not self.assert_key:
                self.assert_real_value = self.res.json(encoding="utf-8")
            else:
                dict_res = self.res.json()
                value_str = "dict_res" + self.assert_key
                arv = eval(value_str)
                if type(arv) == int or type(arv) == float:      # 如果实际值是int，float格式就转化成str格式，方便后续判断
                    arv = str(arv)
                self.assert_real_value = arv
        except KeyError:
            self.assert_erro = "断言键错误:{}".format(self.assert_key)
        except SyntaxError:
            self.assert_erro = "断言键语法错误:{}".format(self.assert_key)
        except Exception as e:
            self.assert_erro = "断言键其他错误情况:{}:{}".format(self.assert_key, e)

        # 期望值如果是json格式，转换成python数据格式
        try:
            # 中数的ID有特殊字符，记得先替换掉
            aev = json.loads(self.assert_expect_value)
            # 最后只要str格式的，如果是int或者float格式的，则还要原来的值
            self.assert_expect_value = aev if type(aev) != int and type(aev) != float else self.assert_expect_value
        except Exception as e:
            pass

    def general_handle(self):
        assert_ret = False

        try:
            # if self.assert_method == "3":
            #     assert_ret = self.assert_expect_value > self.assert_real_value
            if self.assert_method == "4":
                assert_ret = self.assert_expect_value <= self.assert_real_value
            # elif self.assert_method == "5":
            #     assert_ret = self.assert_expect_value < self.assert_real_value
            elif self.assert_method == "6":
                assert_ret = self.assert_expect_value >= self.assert_real_value
            elif self.assert_method == "7":
                assert_ret = self.assert_expect_value in self.assert_real_value
            elif self.assert_method == "8":
                assert_ret = self.assert_expect_value not in self.assert_real_value
            elif self.assert_method == "20":
                assert_ret = self.assert_real_value in self.assert_expect_value
        except Exception as e:
            self.msg = "对比时出错：{}".format(e)
        self.assert_ret = assert_ret

    def len_handle(self):

        try:
            # 有些类型len会报错
            self.assert_real_value = str(len(self.assert_real_value))
        except Exception as e:
            self.assert_erro = "此数据不可以使用len{}".format(e)
        else:
            if self.assert_method == "9":
                self.assert_ret = self.assert_expect_value == self.assert_real_value
            elif self.assert_method == "10":
                self.assert_ret = self.assert_expect_value != self.assert_real_value
            # elif self.assert_method == "11":
            #     self.assert_ret = self.assert_expect_value > self.assert_real_value
            elif self.assert_method == "12":
                self.assert_ret = self.assert_expect_value <= self.assert_real_value
            # elif self.assert_method == "13":
            #     self.assert_ret = self.assert_expect_value < self.assert_real_value
            elif self.assert_method == "14":
                self.assert_ret = self.assert_expect_value >= self.assert_real_value

    def specific_handle(self):
        msg = ""

        try:
            if self.assert_method == "16":
                msg = self.a_in_b(self.assert_expect_value, self.assert_real_value)

            elif self.assert_method == "17":
                msg = self.a_in_b(self.assert_real_value, self.assert_expect_value)

            elif self.assert_method == "18":
                msg = self.list_not_rank_eq(self.assert_real_value, self.assert_expect_value)

            elif self.assert_method == "19":
                if type(self.assert_real_value) == dict and type(self.assert_expect_value) == dict:
                    keys1 = list(self.assert_expect_value.keys())
                    keys2 = list(self.assert_real_value.keys())
                    msg = self.list_not_rank_eq(keys1, keys2)
                else:
                    msg = "此断言方法只可判断{}-{}!"
                if msg:
                    self.assert_erro = msg
                else:
                    self.assert_ret = True

            elif self.assert_method == "90":
                pass

        except Exception as e:
            msg = "校验时出错：{}".format(e)
        if msg:
            self.assert_erro = msg
        else:
            self.assert_ret = True

    @staticmethod
    # 对比两个{}或[] 中的元素 是否in的关系， a只可少，不可多，并且值一致
    def a_in_b(a, b):
        # 查看ａ in b
        msg = ""
        lack = []  # 缺少的字段/下标   其实in的方法用不到这里
        overstep = []  # 多出来的字段/下标
        inconformity = []  # 值对不上的

        if type(a) == dict and type(b) == dict:
            for i in a:
                try:
                    if a[i] != b[i]:
                        inconformity.append(i)
                except:
                    overstep.append(i)
            # for i in b:
            #     try:
            #         a[i]
            #     except:
            #         lack.append(i)
            # if lack:
            #     msg += "缺少字段：{}\t".format(lack)
            if overstep:
                msg += "多出字段：{}\t".format(overstep)
            if inconformity:
                msg += "字段值不一致：{}".format(inconformity)

        elif type(a) == list and type(b) == list:
            b = copy.deepcopy(b)
            for i in a:
                if i in b:
                    b.remove(i)
                else:
                    return "期望结果与实际结果不一致"

        else:
            msg = "格式不统一:{},{}。只可比较同为list 或 同为dict".format(type(a), type(b))

        return msg

    @staticmethod
    # 对比两个列表是否相等（但不计较排序）
    def list_not_rank_eq(a, b):
        """
            # 前提：只判断两个列表
            # 先判断两个列表len是否一样    不一样返回false
            # 循环a 在循环b
            # a在b中，将b移除
            # a不在b中了，返回false
        :param a: 列表a
        :param b: 列表b
        :return: 错误信息True 或者 ""

        """
        if type(a) != list or type(b) != list:
            return "只可比两个[]"

        if len(a) != len(b):
            return "列表长度不一致"

        b = copy.deepcopy(b)
        for i in a:
            if i in b:
                b.remove(i)
            else:
                return "错误元素：{}".format(i)

        return ""


class HtmlTestOneCase:

    def __init__(self, req):
        self.req = req
        self.api_id = self.req.POST.get("api_id", "")
        if not self.api_id:
            response_400_raise_exception("缺少参数: api_id")

    def test_case(self):
        # 1.全局配置处理
        global_env_id = self.req.POST.get("global_env_id", "")
        # global_host_id = self.req.POST.get("global_host_id", "")
        # global_variable_id = self.req.POST.get("global_variable_id", "")
        # global_header_id = self.req.POST.get("global_header_id", "")
        # global_cookie_id = self.req.POST.get("global_cookie_id", "")

        self.global_config = GlobalConfig(global_env_id)

        if self.global_config.msg:
            response_400_raise_exception(self.global_config.msg)
        else:
            self.global_config.get_global_config()
            if self.global_config.msg:
                response_400_raise_exception(self.global_config.msg)
        # self.global_config = GlobalConfig(global_host_id, global_variable_id, global_header_id, global_cookie_id)
        # 3. 获取api部分的参数
        try:
            api_raw = ApiApi.m.get(id=self.api_id)
        except:
            response_400_raise_exception("不存在的接口id:{}".format(self.api_id))
        else:
            # api_item = get_api_param(self.req)
            api_item = model_to_dict(api_raw, fields=["method"])

            # 4. 获取case部分的参数
            case_item, warning = get_case_param(self.req, title_flag=False)

            req_item = get_req_item(self.global_config.host, api_item, case_item)
            toc = TestOneCase(case_item, req_item, self.global_config, warning, True)
            r_data = toc.test_case()

            return r_data


class BatchTest:

    def __init__(self, req, task_info, global_env_id, trigger_way, task_group_id=None):

        self.req = req
        self.task_info = task_info
        # self.task_info = TestTask.m.get(id=1)
        self.test_type = task_info.test_type  # 1全量，2冒烟,3场景
        self.global_env_id = global_env_id  # 手动测试时需要指定一个环境，定时任务用的任务中的所有环境
        self.trigger_way = trigger_way
        self.task_group_id = task_group_id
        self.start_time = time.time()

        # 0. 创建本次报告
        self.report_id = self.crate_report()

    def batch_test(self):
        try:
            # print("batch_test")
            # 0. 报告接收配置
            self.report_receive_handle()
            # print("0. 报告接收配置")

            # self.exception_handle("测试错误信息")

            # 1. 全局配置
            # self.global_config = GlobalConfig(
            #     self.task_info.global_host_id,
            #     self.task_info.global_variable_id,
            #     self.task_info.global_header_id,
            #     self.task_info.global_cookie_id
            # )
            self.global_config = GlobalConfig(self.global_env_id)

            if self.global_config.msg:
                response_400_raise_exception(self.global_config.msg)
            else:
                # 更新详情数据
                testreport_item = {
                    "global_env_id": self.global_config.env.id,
                    "global_env_title": self.global_config.env.title,
                }
                TestReport.m.filter(id=self.report_id).update(**testreport_item)

                self.global_config.get_global_config()
                if self.global_config.msg:
                    response_400_raise_exception(self.global_config.msg)

            # print("1. 全局配置")
            # print(self.global_config.get_global_config_dict())

            # 2. 创建线程池
            futures = Futures(settings.THREAD_MAX_WORKERS)  # 创建线程池，限定最大线程数量
            # print("2. 创建线程池")

            # 3. 对部分入参做校验,并获取要处理的api_id 或 case_id
            api_list = []

            task_info_dict = model_to_dict(self.task_info)
            if self.test_type in ["全量测试", "冒烟测试"]:
                # api_id_list = self.get_api_id_list()
                msg, api_id_list = api_ids_handle(task_info_dict)
                if msg:
                    self.exception_handle(msg)
                # 4. 开始测试每一个接口和其下用例
                api_list = self.api_handle(futures, api_id_list)

            elif self.test_type == "场景测试":
                # case_id_list = self.get_case_id_list()
                msg, case_id_list = case_ids_handle(task_info_dict)
                if msg:
                    self.exception_handle(msg)
                # 4. 开始测试每一个接口和其下用例
                api_list = self.case_handle(futures, case_id_list)

            else:
                self.exception_handle("不存在的测试类型:{}".format(self.test_type))
            # print("3. 对部分入参做校验,并获取要处理的api_id 或 case_id")

            # 5. 整理全部的接口执行情况
            statistics_item = self.get_statistics_item(api_list)
            # print("45. 整理全部的接口执行情况")

            # 7. 测试数据整理入库
            # 8. 发送邮件, 发送企业微信
            r_data = self.other_handle(api_list, statistics_item)
            # print("678. 测试数据整理入库")

            # 9. 返回最终数据
            execution_time = time.time() - self.start_time   # 执行时长
            r_data["execution_time"] = execution_time
            TestReport.m.filter(id=r_data["report_id"]).update(
                **{
                    "execution_time": execution_time,
                    "flag": True,
                })
            # print("9. 返回最终数据")

            return r_data

        except Exception as e:
            self.exception_handle("批量执行任务时未知异常：{}".format(e))

    def crate_report(self):
        # 保存到数据库
        testreport_item = {
            "task_id": self.task_info.id,
            "title": self.task_info.title,
            "test_type": self.test_type,
            "project_id": self.task_info.project_id,
            "project_title": self.task_info.project_title,
            "trigger_way": self.trigger_way,
            "task_group_id": self.task_group_id,
        }

        user_item = {}
        if self.trigger_way == "定时任务":
            c_time = get_now_time()
            user_item = {
                "create_user": self.task_info.latest_update_user,
                "create_user_id": self.task_info.latest_update_user_id,
                "c_date": c_time,
                "latest_update_user": self.task_info.latest_update_user,
                "latest_update_user_id": self.task_info.latest_update_user_id,
                "u_date": c_time,
            }
        elif self.trigger_way == "手动测试":
            user_item = get_user_info_for_session(self.req, create=True)
        testreport_item.update(user_item)

        try:
            obj = TestReport.m.create(**testreport_item)
            return obj.id
        except Exception as e:
            response_400_raise_exception("创建报告时出错：{}".format(e))

    def exception_handle(self, erro_msg):
        """
            跑任务时出现的异常都要记录到数据库中,
            并且发送邮件/企业微信提醒,
            最后在返回异常响应
        """

        erro_msg = "任务运行时出错:  " + erro_msg

        # 1. 异常信息存储到数据库
        item = {
            "flag": False,
            "erro_msg": erro_msg
        }
        TestReport.m.filter(id=self.report_id).update(**item)

        # 2.1 整理信息,发送企业微信用户组，企业微信群聊，邮箱用户组
        title = "【测试报告】 - {}".format(self.task_info.title)
        # 查看此邮件的完整地址
        report_url = settings.IP + "/html/api/test_report?index_flag=1&id={}".format(self.report_id)
        try:
            env_title = self.global_config.env.title
        except:
            env_title = ""
        body = "{}\n" \
               "任务id： {}\n" \
               "任务名称： {}\n" \
               "全局环境： {}\n" \
               "报告链接： {}\n".format(
            erro_msg, self.task_info.id, self.task_info.title, env_title, report_url)

        content = "{}\n\n{}".format(title, body)

        send_workwx_user_group_flag, send_workwx_user_group_msg = send_workwx_user_group(content, self.workwx_user_group)
        send_workwx_group_chat_flag, send_workwx_group_chat_msg = send_workwx_group_chat(content, self.workwx_group_chat)
        send_email_flag, send_email_msg = self.send_eamil(title, content)
        # self.send_workwx_user_group(content)
        # self.send_workwx_group_chat(content)
        # self.send_eamil(title, content)
        TestReport.m.filter(id=self.report_id).update(
            **{
                "send_workwx_user_group_flag": send_workwx_user_group_flag,
                "send_workwx_user_group_msg": send_workwx_user_group_msg,
                "send_workwx_group_chat_flag": send_workwx_group_chat_flag,
                "send_workwx_group_chat_msg": send_workwx_group_chat_msg,
                "send_email_flag": send_email_flag,
                "send_email_msg": send_email_msg,
            })

        # 3. 构造接口返回体
        response_400_raise_exception(erro_msg)
    #
    # def send_workwx_user_group(self, content):
    #
    #     # 2.2. 发送企业微信用户组
    #     send_workwx_user_group_flag = None
    #     send_workwx_user_group_msg = ""
    #     if self.workwx_user_group:
    #         wwx = WorkWeixinApi(2)
    #         # send_workwx_msg = wwx.msg
    #         if wwx.msg:
    #             send_workwx_user_group_flag = False
    #         else:
    #             send_workwx_user_group_flag = wwx.send_msg(self.workwx_user_group, content)
    #         send_workwx_user_group_msg = wwx.msg
    #     else:
    #         send_workwx_user_group_msg = "无接收人"
    #
    #     # print("{} : id:{} workwx_user_group_msg:{}".format(datetime.datetime.now(), self.task_info.workwx_user_group_id, send_workwx_user_group_msg))
    #     TestReport.m.filter(id=self.report_id).update(
    #         **{
    #             "send_workwx_user_group_flag": send_workwx_user_group_flag,
    #             "send_workwx_user_group_msg": send_workwx_user_group_msg
    #         })
    #     return send_workwx_user_group_flag, send_workwx_user_group_msg
    #
    # def send_workwx_group_chat(self, content):
    #
    #     # 2.3 发送企业微信群
    #     send_workwx_group_chat_flag = None
    #     send_workwx_group_chat_msg = ""
    #     if self.workwx_group_chat:
    #         body = {
    #             "msgtype": "text",
    #             "text": {
    #                 "content": content,
    #                 "mentioned_list": [],
    #                 "mentioned_mobile_list": []
    #             }
    #         }
    #         try:
    #             res = requests.post(self.workwx_group_chat, json=body)
    #             json_res = res.json()
    #             if json_res["errcode"] == 0:    # errcode=0为成功
    #                 send_workwx_group_chat_flag = True
    #             else:
    #                 send_workwx_group_chat_flag = False
    #                 send_workwx_group_chat_msg = json_res["errmsg"]
    #         except Exception as e:
    #             send_workwx_group_chat_msg = "发送错误：{}".format(e)
    #     else:
    #         send_workwx_group_chat_msg = "无接收群"
    #
    #     TestReport.m.filter(id=self.report_id).update(
    #         **{
    #             "send_workwx_group_chat_flag": send_workwx_group_chat_flag,
    #             "send_workwx_group_chat_msg": send_workwx_group_chat_msg
    #         })
    #     return send_workwx_group_chat_flag, send_workwx_group_chat_msg

    def send_eamil(self, title, content):
        # 2.4. 发送邮件
        receivers = str_to_list(self.email_user_group)
        send_email_flag = None
        send_email_msg = ""

        if receivers:
            send_email_flag = self.send_email_handle(title, content, receivers)
        else:
            send_email_msg = "无接收人"

        # TestReport.m.filter(id=self.report_id).update(
        #     **{
        #         "send_email_flag": send_email_flag,
        #         "send_email_msg": send_email_msg,
        #     })
        return send_email_flag, send_email_msg

    def report_receive_handle(self):

        try:
            if self.task_info.workwx_user_group_id:
                info = WorkWxUserGroup.m.get(id=self.task_info.workwx_user_group_id)
                self.workwx_user_group = info.params or ""
            else:
                self.workwx_user_group = ""
        except Exception as e:
            self.exception_handle("获取微信用户组出错！".format(e))

        try:
            if self.task_info.workwx_group_chat_id:
                info = WorkWxGroupChat.m.get(id=self.task_info.workwx_group_chat_id)
                self.workwx_group_chat = info.params or ""
            else:
                self.workwx_group_chat = ""
        except Exception as e:
            self.exception_handle("获取微信群出错！".format(e))

        try:
            if self.task_info.email_user_group_id:
                info = EmailUserGroup.m.get(id=self.task_info.email_user_group_id)
                self.email_user_group = info.params or ""
            else:
                self.email_user_group = ""
        except Exception as e:
            self.exception_handle("获取邮箱用户组出错！".format(e))

    def case_handle(self, futures, case_id_list):
        api_list = []

        for index, case_id in enumerate(case_id_list):
            # print("handel case_id:{} --- {}/{}".format(case_id, index, len(case_id_list)))
            try:
                case_data = ApiCase.m.get(id=int(case_id))
            except:
                self.exception_handle("不存在的case id:{}".format(case_id))
            else:
                api_data = ApiApi.m.get(id=case_data.api_id)
                api_item = model_to_dict(api_data, ["id", "title", "desc", "method"])
                case_item, erro_msg = db_case_info_handle(case_data)
                if erro_msg:
                    self.exception_handle(erro_msg)

                api_item["case_list"] = []

                if case_item["status"]:  # 场景测试不管是否启用

                    # 获取发送请求用到的字段
                    req_item = get_req_item(self.global_config.host, api_item, case_item)
                    # 返回需要的数据 assert_flag 存放用例的id
                    futures.submit(
                        self.api_handle3, api_item, case_item, req_item)  # 多线程方式
                else:
                    temp = {
                        "id": case_item["id"],
                        "title": case_item["title"],
                        "asserts_flag": None,
                    }
                    api_item["case_list"].append(temp)
            futures.as_completed()  # 全部请求发送完毕，并处理完成后才能进行下一步

            time.sleep(settings.REQUEST_SLEEP)     # 防止请求过快

            statistics_item = {
                "success": 0,
                "fail": 0,
                "ignore": 0,
                "count": 0,
                "flag": None,
            }
            for case in api_item["case_list"]:
                if case["asserts_flag"]:
                    statistics_item["success"] += 1
                elif case["asserts_flag"] == False:
                    statistics_item["fail"] += 1
                else:
                    statistics_item["ignore"] += 1
                statistics_item["count"] += 1
            if statistics_item["count"] == statistics_item["ignore"]:
                statistics_item["flag"] = None
            else:
                statistics_item["flag"] = statistics_item["fail"] == 0

            api_item["statistics_item"] = statistics_item
            api_list.append(api_item)

        return api_list

    def api_handle(self, futures, api_id_list):

        api_list = []

        for api_id in api_id_list:
            # 获取接口参数
            try:
                api_data = ApiApi.m.get(id=api_id)
                api_item = model_to_dict(api_data, ["id", "title", "desc", "method"])
            except:
                self.exception_handle("不存在的接口id：".format(api_id))
            else:
                self.api_handle2(futures, api_item)

                api_item['group_id'] = api_data.group_id
                api_item['group_title'] = ApiGroup.m.get(id=api_data.group_id).title

                api_list.append(api_item)

        return api_list

    def api_handle2(self, futures, api_item):

        # 获取此api下的所有case数据
        case_datas = ApiCase.m.filter(api=api_item["id"])
        if self.test_type == "冒烟测试":
            if len(case_datas) >= 2:    # 优先要第二条用例
                case_datas = case_datas[1:2]

        api_item["case_list"] = []

        for case_data in case_datas:

            case_item, erro_msg = db_case_info_handle(case_data)
            if erro_msg:
                self.exception_handle("用例id:{}:{}".format(
                    case_data.id, erro_msg))

            if case_item["status"]:  # 只有在用例是启用状态下,才会跑此用例
                # 获取发送请求用到的字段
                req_item = get_req_item(self.global_config.host, api_item, case_item)

                # 返回需要的数据 assert_flag 存放用例的id
                futures.submit(self.api_handle3, api_item, case_item, req_item)  # 多线程方式

        futures.as_completed()  # 全部请求发送完毕，并处理完成后才能进行下一步

        statistics_item = {
            "success": 0,
            "fail": 0,
            "ignore": 0,
            "count": 0,
            "flag": None,
        }
        for case in api_item["case_list"]:
            if case["asserts_flag"]:
                statistics_item["success"] += 1
            elif case["asserts_flag"] == False:
                statistics_item["fail"] += 1
            else:
                statistics_item["ignore"] += 1
            statistics_item["count"] += 1
        statistics_item["flag"] = statistics_item["fail"] == 0

        api_item["statistics_item"] = statistics_item

    def api_handle3(self, api_item, case_item, req_item):
        # 发送请求获取结果，并发送case项目中
        toc = TestOneCase(case_item, req_item, self.global_config)
        r_data = toc.test_case()
        # print("case_info", json_dumps_indent4(r_data))
        report_detail = {
            "report_id": self.report_id,
            "api_id": api_item["id"],
            "api_title": api_item["title"],
            "api_desc": api_item["desc"],
            "method": api_item["method"],
            "case_id": case_item["id"],
            "case_title": case_item["title"],
            "final_ret": r_data["res_part"]["asserts_flag"],
            "case_info": json_dumps(r_data),
        }

        user_item = {}
        if self.trigger_way == "定时任务":
            c_time = get_now_time()
            user_item = {
                "create_user": self.task_info.latest_update_user,
                "create_user_id": self.task_info.latest_update_user_id,
                "c_date": c_time,
                "latest_update_user": self.task_info.latest_update_user,
                "latest_update_user_id": self.task_info.latest_update_user_id,
                "u_date": c_time,
            }
        elif self.trigger_way == "手动测试":
            user_item = get_user_info_for_session(self.req, create=True)

        report_detail.update(user_item)
        obj = TestReportDetail.m.create(**report_detail)

        info = {
            "id": case_item["id"],
            "title": case_item["title"],
            "asserts_flag": r_data["res_part"]["asserts_flag"],
            "report_detail_id": obj.pk,
        }
        # 将case数据，响应数据放入case列表中
        api_item["case_list"].append(info)

    def get_statistics_item(self, api_list):
        # 接口下的统计
        statistics_item = {
            "success": 0,
            "fail": 0,
            "ignore": 0,
            "count": 0,
            "flag": False,
        }
        try:
            for api in api_list:
                if api["statistics_item"]["flag"]:
                    statistics_item["success"] += 1
                elif api["statistics_item"]["flag"] == False:
                    statistics_item["fail"] += 1
                else:
                    statistics_item["ignore"] += 1
                statistics_item["count"] += 1
            statistics_item["flag"] = statistics_item["fail"] == 0
            # statistics_item["flag"] = statistics_item["count"] == statistics_item["success"]
        except Exception as e:
            self.exception_handle("统计时出错:{}".format(e))
        return statistics_item

    def other_handle(self, api_list, statistics_item):

        # 组装测试结果统计和测试数据信息
        report = {
            "api_list": api_list,
            "statistics_item": statistics_item,
            "global_config": json_dumps(self.global_config.get_global_config_dict()),
        }

        j_report = json_dumps_indent4(report)

        # 更新详情数据
        testreport_item = {
            "report": j_report,
            "test_ret": statistics_item["flag"]
        }

        TestReport.m.filter(id=self.report_id).update(**testreport_item)

        # 查看此邮件的完整地址
        report_url = settings.IP + "/html/api/test_report?index_flag=1&id={}".format(self.report_id)
        title = "【测试报告】 - {}".format(self.task_info.title)
        # 发送企业微信部分
        body = "本此总共测试{}个".format(statistics_item["count"])
        if self.test_type == "场景测试":
            # for api in api_list:
            #     title_list.append(api["case_list"][0]["title"])
            body += "用例"
        else:
            # title_list = [api["title"] for api in api_list]
            body += "接口"

        # "详情请查看：<a href='{}'>{}</a>\r\n\r\n" \
        body += ":\r\n" \
              "通过：{}个, 失败：{}个, 忽略：{}个\r\n" \
              "详情请查看：{}\r\n\r\n" \
              "测试类型：{}\r\n" \
              "全局环境：{}\r\n" \
              "触发方式：{}\r\n" \
              "".format(statistics_item["success"], statistics_item["fail"], statistics_item["ignore"],
                    report_url, self.test_type, self.global_config.env.title, self.trigger_way)

        content = "{}\n\n{}".format(title, body)
        send_workwx_user_group_flag, send_workwx_user_group_msg = send_workwx_user_group(content, self.workwx_user_group)
        send_workwx_group_chat_flag, send_workwx_group_chat_msg = send_workwx_group_chat(content, self.workwx_group_chat)
        send_email_flag, send_email_msg = self.send_eamil(title, content)

        TestReport.m.filter(id=self.report_id).update(
            **{
                "send_workwx_user_group_flag": send_workwx_user_group_flag,
                "send_workwx_user_group_msg": send_workwx_user_group_msg,
                "send_workwx_group_chat_flag": send_workwx_group_chat_flag,
                "send_workwx_group_chat_msg": send_workwx_group_chat_msg,
                "send_email_flag": send_email_flag,
                "send_email_msg": send_email_msg,
            })

        # 构造接口返回数据
        r_data = dict()

        r_data["report_id"] = self.report_id
        r_data["report_url"] = report_url
        r_data["test_type"] = self.test_type
        r_data["global_host"] = self.global_config.host.title if self.global_config.host else "未使用！"
        r_data["project_title"] = self.task_info.project_title
        r_data["send_workwx_user_group_flag"] = send_workwx_user_group_flag
        r_data["send_workwx_user_group_msg"] = send_workwx_user_group_msg
        r_data["send_workwx_group_chat_flag"] = send_workwx_group_chat_flag
        r_data["send_workwx_group_chat_msg"] = send_workwx_group_chat_msg
        r_data["send_email_flag"] = send_email_flag
        r_data["send_email_msg"] = send_email_msg
        # r_data["ret"] = True
        # r_data["msg"] = None
        r_data.update(report)
        for api in r_data["api_list"]:
            del api["case_list"]
        return r_data

    def send_email_handle(self, title, content, receivers=None):
        sender = settings.SENDER
        mail_host = settings.MAIL_HOST
        mail_pass = settings.MAIL_PASS
        # me = "guojing02@qding.me"
        # 没有收件人，则设为默认收件人。有收件人，但是没有我，则添加我
        if not receivers:
            receivers = settings.RECEIVERS
        # if me not in receivers:
        #     receivers.append(me)

        flag = send_email(sender, mail_host, mail_pass, receivers, title, content)

        return flag



