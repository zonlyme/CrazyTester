from .view_basic import *
from .view_api import get_api_param
from .view_case import get_case_param
from .send_email import send_email


# 单接口测试数据处理
def send_req(req):
    r_data = {}

    # 1. 获取表单中的api部分的参数并验证
    api_item = get_api_param(req)
    # 2. 验证api字段的必填项"method", 和判断env id的有效性
    env_id = req.POST.get("env", "")
    if env_id:
        env_id = int(env_id)
        try:
            env_data = EnvData.m.get(pk=env_id)
            host = env_data.host or ""
            env_params = json.loads(env_data.params) if env_data.params else ""  # 全局变量
        except Exception as e:
            r_data["ret"] = False
            r_data["erro_msg"] = "环境id有误：{}, {}".format(env_id, e)
            return JsonResponse(json.dumps(r_data), safe=False)

    erro_filed = verify_not_is_None(api_item, ["method"])
    # 如果处理参数部分有错误，直接返回结果和错误信息
    if erro_filed:
        r_data["ret"] = False
        r_data["erro_msg"] = "{}不能为空！".format(erro_filed)
        return JsonResponse(json.dumps(r_data), safe=False)
    else:
        # 2. 获取case部分的数据并验证 case_data:{"item":item, "warning":warning, "ret":True
        case_data = get_case_param(req, title_flag=False)
        if case_data["ret"]:
            case_item = case_data["item"]

            # 3.处理req_item发送请求需要的参数
            # add_UA(case_item)
            req_item = get_req_item(host, api_item, case_item, env_params)

            r_data = send_req2(req_item, host, env_params, case_data["warning"])
            return JsonResponse(json.dumps(r_data), safe=False)
        else:
            return JsonResponse(json.dumps(case_data), safe=False)


# 从请求参数中获取发送请求需要的数据
def get_req_item(host, api_item, case_item, env_params):
    """
    :param host: host
    :param api_item: 接口数据
    :param case_item: 用例数据
    :return: 只在发送请求中用到的参数
    """
    req_item = {}

    req_item["url"] = "{}{}".format(host, case_item["url"])
    req_item["method"] = api_item["method"]
    req_item["headers"] = case_item["headers"] or {}
    req_item["cookies"] = case_item["cookies"] or {}
    req_item["params"] = case_item["params"] or {}
    req_item["data"] = case_item["data"] or {}

    req_item["prefix"] = case_item["prefix"] or {}
    req_item["rsgv"] = case_item["rsgv"] or {}
    req_item["asserts"] = case_item["asserts"] or {}
    headmap = getheader(env_params)
    # 后期可能要根据账号绑定对应的header
    req_item["headers"].update(**headmap)
    # req_item["headers"]["X-Uid"] = headmap["X-Uid"]
    # req_item["headers"]["X-Timestamp"] = headmap["X-Timestamp"]
    # req_item["headers"]["X-Nonce"] = headmap["X-Nonce"]
    # req_item["headers"]["X-Signature"] = headmap["X-Signature"]
    # req_item["headers"]["X-Appid"] = headmap["X-Appid"]

    return req_item


def merge_paramkv_and_params(param_kv, params):
    """
    :param paramkv: 键值对合并成的字典
    :param params: json格式的字典
    :return: 用paramkv覆盖params里的数据，产生的字典(前者覆盖后者)
    """
    if params:
        if param_kv:
            params.update(**param_kv)
    else:
        params = param_kv if param_kv else {}

    return params

# 根据入参发送请求，并返回响应数据
def send_req2(item, host, env_params, warning=[]):
    """
    :param item:
    :param warning: 一个列表，盛放警告信息(不致命的, 页面单个接口测试才会用到)
    :return:
    """

    # 前置处理: 前置产生的变量只对本次请求生效,不要影响到全局环境变量
    c_case_env_params = copy.deepcopy(env_params)   # 当前用例环境变量

    prefix_handle(item["prefix"], host, c_case_env_params)
    # 处理参数化参数-全局的
    parameterization_handle(item, c_case_env_params)


    default_asserts = {
        "assert_status": "1",  # 断言键
        "assert_key": "",  # 断言键
        "assert_method": "0",  # 断言方式
        "assert_expect_value": "200",  # 断言期望值
    }

    asserts = []
    # 如果有断言,判断是否有启用的断言,
        # 如果有启用断言:深拷贝所有断言信息,
        # 如果没有启用断言:则追加默认断言，判断状态码
    # 如果没有断言,则为默认断言,判断状态码
    if len(item["asserts"]) > 0:
        for asserts in item["asserts"]:
            if asserts["assert_status"] == "1":
                asserts = copy.deepcopy(item["asserts"])
                break
        else:
            asserts = copy.deepcopy(item["asserts"])
            asserts.append(default_asserts)
    else:
        asserts.append(default_asserts)

    # asserts = copy.deepcopy(item["asserts"]) if item["asserts"] else default_asserts

    r_data = {
        "res_ret": True,  # 1.发送请求结果
        "erro_msg": None,  # 如果请求失败res_ret为Flase，写入异常信息
        "warning": None,  # 页面中发送请求，才会有内容的字段，用来存放页面中无效的请求头，params，批量运行，此字段没有值

        "res_body_is_json": None,  # 2.响应体是否是json格式，如果不是，验证结果为失败
        "res_headers": None,  # 响应体是json格式才能有响应头响应体
        "res_body": None,  # 响应体是json格式才能有响应头响应体

        "asserts": asserts,
        "asserts_flag": True,  # 此用例最终断言结果，有一条断言是失败的则为此值为失败

        "time": None,  # 响应时间，res_ret成功才会有
        "status_code": None,  # 响应状态码，res_ret成功才会有,

        "prefix": item["prefix"] or "",
        "rsgv": item["rsgv"] or "",
        "c_case_env_params": c_case_env_params,
        "real_url": item["url"]
    }

    # 将表单的kv和json格式的param合并成一个字典


    try:
        if item["method"] == "Get":
            # get方式合并paramkv和params
            params = merge_paramkv_and_params(item["params"], item["data"])

            res = requests.get(
                item["url"], params=params,
                headers=item["headers"], cookies=item["cookies"])

        elif item["method"] == "Post":
            res = requests.post(
                item["url"], params=item["params"],
                headers=item["headers"], cookies=item["cookies"],
                json=item["data"])  # json参数填写字典自动转换,并且响应头自动改为application/json

    except Exception as e:
        r_data['erro_msg'] = "请求接口出错:{}".format(e)
        r_data["res_ret"] = False
        r_data["asserts_flag"] = False

    else:
        r_data["status_code"] = res.status_code  # 响应码
        r_data["time"] = str((res.elapsed.microseconds) / 1000000) + "ms"  # 响应时间
        # res.headers是其他dict格式，需要转换成python标准dict格式
        r_data["res_headers"] = dict(res.headers)
        # 如果返回体是json格式，验证断言
        try:
            r_data["res_body"] = res.json()
        except Exception as e:
            r_data["res_body_is_json"] = False
            r_data["res_body"] = res.text
        else:  # 如果res_body 是json格式的话,验证结果，获取验证结果，和错误信息
            r_data["res_body_is_json"] = True

            # 验证断言信息,并判断所有断言最终结果
            for assert_item in r_data["asserts"]:
                if assert_item["assert_status"] == "1": # 如果断言是启用状态
                    vro = VerifyResOne(assert_item, res)
                    vro.verify_res_one()
                    if not assert_item["assert_ret"]:
                        r_data["asserts_flag"] = False

            # 响应成功调用后置
            rsgv_handle(item["rsgv"], env_params, r_data["res_body"])

            r_data['warning'] = ",".join(warning)
        dict_to_json_and_fromat(r_data, ["res_body", "res_headers", "prefix", "rsgv", "c_case_env_params"])
        dict_to_json_and_fromat(item, ["headers", "params", "data", "cookies"])

    return r_data


# 所有{{xxx}}的参数 参数化
def parameterization_handle(item, params):
    """
    :param item:
            处理发送请求时用到的所有参数，并将参数化其中的参数
            method <class 'str'>
            headers <class 'dict'>
            params <class 'dict'>
            data <class 'dict'>
            cookies <class 'dict'>
            url <class 'str'>
            asserts <class 'list'>
    :param :
    :return: 参数化替换完成的item
    """

    new_item = {}
    if params:
        new_item["headers"] = json.dumps(item["headers"]) or "{}"
        new_item["params"] = json.dumps(item["params"]) or "{}"
        new_item["data"] = json.dumps(item["data"]) or "{}"
        new_item["url"] = item["url"]
        new_item["asserts"] = json.dumps(item["asserts"]) or "{}"

        params_item = {}
        for i in params:
            # if params["enalbe"]:
            params_item[i["key"]] = i["value"]  # 这里组装成dict格式数据,重复的key以后面的为准嘻嘻

        for i, j in new_item.items():
            for k, v in params_item.items():
                key = "{{" + k + "}}"
                if key in new_item[i]:
                    # print("key - j :", key, new_item[i])
                    new_item[i] = j.replace(key, v)

        new_item["headers"] = json.loads(new_item["headers"])
        new_item["params"] = json.loads(new_item["params"])
        new_item["data"] = json.loads(new_item["data"])
        new_item["asserts"] = json.loads(new_item["asserts"])

    item.update(new_item)


def prefix_handle(prefixs, host, c_case_env_params):
    "prefix_status  prefix_case_id  prefix_set_var_name prefix_key  prefix_real_value"

    for prefix in prefixs:

        # 判断是否启用  1表示启用
        if prefix["prefix_status"] == "1":
            # 对参数进行校验,三者都没有,什么都不做,  没有用例id,返回报错
            # if not prefix["prefix_case_id"] and not prefix["prefix_set_var_name"] and not prefix["prefix_set_var_name"]:
            #     prefix["prefix_real_value"] = "前置操作错误: 没有填写用例id!"
            #     continue
            if not prefix["prefix_case_id"]:
                prefix["prefix_real_value"] = "前置操作错误: 没有填写用例id!"
                continue
            # 获取用例数据,接口数据
            try:
                case_data = CaseData.m.get(pk=prefix["prefix_case_id"])
            except Exception as e:
                prefix["prefix_real_value"] = "前置操作错误: 获取不到此用例:{}:{}".format(prefix["prefix_case_id"], e)
            else:
                api_data = APIData.m.get(pk=case_data.parent_id_id)
                case_data = model_to_dict(case_data)
                api_data = model_to_dict(api_data)
                item = get_req_item(host, api_data, case_data, c_case_env_params)
                # 发送请求
                try:
                    if item["method"] == "Get":
                        # get方式合并paramkv和params
                        params = merge_paramkv_and_params(item["params"], item["data"])

                        res = requests.get(
                            item["url"], params=params,
                            headers=item["headers"], cookies=item["cookies"])

                    elif item["method"] == "Post":
                        res = requests.post(
                            item["url"], params=item["params"],
                            headers=item["headers"], cookies=item["cookies"],
                            json=item["data"])  # json参数填写字典自动转换,并且响应头自动改为application/json

                except Exception as e:
                    prefix["prefix_real_value"] = "前置操作错误:发送请求时出错:{}".format(e)

                else:

                    if prefix["prefix_set_var_name"] and prefix["prefix_key"]:
                        try:
                            dict_res = res.json()
                            prefix["prefix_real_res"] = dict_res
                        except Exception as e:
                            prefix["prefix_real_res"] = res.text
                            prefix["prefix_real_value"] = "前置操作失败:接口响应不是json格式"
                        else:
                            try:
                                value = eval("dict_res" + prefix["prefix_key"])
                            except Exception as e:
                                prefix["prefix_real_value"] = "前置操作失败:变量键找不到或格式有误:{}".format(e)
                            else:
                                if type(value) == str or \
                                                type(value) == int or \
                                                type(value) == float:  # 如果实际值是int，float格式就转化成str格式，方便后续判断
                                    value = str(value)
                                    prefix["prefix_real_value"] = value
                                    params_template = {
                                        "key": prefix["prefix_set_var_name"],
                                        "value": value,
                                        "description": "",
                                        "enabled": True
                                    }
                                    c_case_env_params.append(params_template)   # 添加到当前用例变量中
                                else:
                                    prefix["prefix_real_value"] = "前置操作失败:变量值只能是数字或字符串,当前格式为:{}:{}".format(
                                        type(value), value)
                    else:
                        ret = res.status_code == 200  # 响应码 不判断断言,只认为200才是调通
                        if ret:
                            prefix["prefix_real_value"] = "前置操作成功:仅调用接口成功,接口状态码:{}".format(res.status_code)
                        else:
                            prefix["prefix_real_value"] = "前置操作失败:接口状态码:{}".format(res.status_code)
        # else:
        #     prefix["prefix_real_value"] = "前置操作失败:禁用状态"


# 后置操作:响应设置全局变量
def rsgv_handle(rsgvs, env_params, dict_res):
    for rsgv in rsgvs:
        # 判断是否启用  1表示启用
        if rsgv["rsgv_status"] == "1":
            if not rsgv["rsgv_name"]:
                rsgv["rsgv_real_value"] = "后置操作失败:没有填写变量名!"
                continue
            if not rsgv["rsgv_key"]:
                rsgv["rsgv_real_value"] = "后置操作失败:没有填写变量键!"
                continue
            try:
                value = eval("dict_res" + rsgv["rsgv_key"])
            except Exception as e:
                rsgv["rsgv_real_value"] = "后置操作失败:变量键找不到或格式有误:{}".format(e)
            else:
                if type(value) == str or \
                                type(value) == int or \
                                type(value) == float:  # 如果实际值是int，float格式就转化成str格式，方便后续判断
                    value = str(value)
                    rsgv["rsgv_real_value"] = value
                    params_template = {
                        "key": rsgv["rsgv_name"],
                        "value": value,
                        "description": "",
                        "enabled": True
                    }
                    env_params.append(params_template)  # 添加到当前用例变量中
                else:
                    rsgv["rsgv_real_value"] = "后置操作失败:变量值只能是数字或字符串,当前格式为:{}:{}".format(
                        type(value), value)


# 批量测试多个接口
def batch_test(req):
    """
    - 获取参数 并先判断参数有效性
    - 判断用户名密码 或者是否登录过有session
    - 测试接口 掉用的test_handle
    - 测试接口完成,统计测试信息
    - 构造数据,保存到测试报告表中
    - 发送邮件报告测试情况
    - 构造返回数据,返回响应


    :param env_id=0   apis=659 user=guojing    pw=jing0605 receivers=guojing@chinadaas.com alias=xxx第一次测试
    :return:
    """

    start_time = time.time()

    env_id = req.GET.get("env_id", "")
    api_ids = req.GET.get("apis", "")
    nodes_ids = req.GET.get("nodes", "")
    receivers = req.GET.get("receivers", "")
    alias = req.GET.get("alias", '')

    if env_id:
        env_id = int(env_id)
        try:
            env_data = EnvData.m.get(pk=env_id)
            host = env_data.host or ""
            env_params = json.loads(env_data.params)  # 全局变量
        except Exception as e:
            return HttpResponse("环境id有误：{}！\r{}".format(env_id, e))
    else:
        return HttpResponse("没有选择环境id！")

    if not api_ids:
        return HttpResponse("没有选择接口id！")

    try:
        api_id_list = [int(i) for i in splitDH(api_ids)]
    except Exception as e:
        return HttpResponse("接口id非数字！")

    # 判断所有node_id是否存在
    node_id_list = splitDH(nodes_ids)
    for node_id in node_id_list:
        try:
            NavNode.m.get(id=int(node_id))
        except Exception as e:
            return HttpResponse("不存在的node:{}".format(node_id))

    # 判断所有api_id是否存在
    for api_id in api_id_list:
        try:
            APIData.m.get(id=int(api_id))
        except Exception as e:
            return HttpResponse("不存在的接口id:{}".format(api_id))

    # 解析node下的所有api,放到api_id_list中
    for node_id in node_id_list:
        node = NavNode.m.get(id=int(node_id))
        apis = APIData.m.filter(parent_id=int(node.id))
        for api in apis:
            api_id_list.append(api.id)

    api_id_list = list(set(api_id_list))    # 去重,防止node下的api和api重复
    print(api_id_list)
    user = verify_user(req)
    if not user:
        return HttpResponse("未登陆或者用户名密码错误！")

    if receivers:
        receivers = splitDH(receivers)

    task_id = str(int(time.time()*10000000))
    api_list = []

    futures = Futures(settings.THREAD_MAX_WORKERS)  # 创建线程池，限定最大线程数量

    for api_id in api_id_list:
        ret = test_handle(futures, api_id, host, env_params, task_id)
        if ret["erro_msg"]:
            return HttpResponse(ret["erro_msg"])

        api_list.append(ret["api_item"])

     # 接口下的统计
    statistics_item = {
        "success": 0,
        "fail": 0,
        "count": 0,
        "flag": False,
    }
    for api in api_list:
        if api["statistics_item"]["flag"]:
            statistics_item["success"] += 1
        statistics_item["count"] += 1
        statistics_item["fail"] = statistics_item["count"] - statistics_item["success"]
    statistics_item["flag"] = True if statistics_item["count"] == statistics_item["success"] else False

    # 测试完成统计测试信息(添加每个接口下的用力通过情况，返回通过接口情况)
    # statistics_item = statistics_api(api_list)
    # 组装测试结果统计和测试数据信息
    report = {
        "api_list": api_list,
        "statistics_item": statistics_item,
        "host": host,
    }
    # 先获取一下所有api名字，在json化
    api_names = []
    for api in api_list:
        api_names.append(api["title"])
    api_names = ",".join(api_names)

    j_report = json.dumps(report, ensure_ascii=False, indent=4)

    test_report_title = alias.strip() or "{}-测试报告-{}".format(
        user, str(datetime.datetime.fromtimestamp(time.time()))[:19])
    # 保存到数据库
    testreport_item = {
        "task_id": task_id,
        "title": test_report_title,  # 测试报告+当前时间
        "report": j_report,
        "tester": user
    }

    try:
        obj = TestReport.m.create(**testreport_item)
    except Exception as e:
        return HttpResponse("出错了，出错原因：{}".format(e))

    report_url = settings.IP + "/interface/report/{}".format(obj.id)  # 查看此邮件的地址
    # 发送邮件
    email_title = "【测试报告】本次测试接口：{}".format(api_names)
    body_text = "本此总共测试{}个接口\r\n" \
                "{}\r\n" \
                "通过：{}个, 失败：{}个\r\n" \
                "详情请查看：{}\r\n" \
                "执行人：{}\r\n".format(
        statistics_item["count"], api_names, statistics_item["success"], statistics_item["fail"], report_url, user
    )
    send_email_flag = send_email_handle(email_title, body_text, receivers)

    # 构造返回数据
    r_data = {}
    r_data["host"] = host
    r_data["report_url"] = report_url
    r_data["send_email_flag"] = send_email_flag
    r_data["tester"] = user
    r_data.update(report)
    for api in r_data["api_list"]:
        del api["case_list"]

    end_time = time.time()
    t = end_time - start_time
    r_data["t"] = t
    r_data = json.dumps(r_data, ensure_ascii=False, indent=4)
    return HttpResponse(r_data)




# 发送邮件
def send_email_handle(title, body_text, receivers=None):
    sender = settings.SENDER
    mail_host = settings.MAIL_HOST
    mail_pass = settings.MAIL_PASS
    me = "guojing@chinadaas.com"
    # 没有收件人，则设为默认收件人。有收件人，但是没有我，则添加我
    if not receivers:
        receivers = settings.RECEIVERS
    if me not in receivers:
        receivers.append(me)

    flag = send_email(sender, mail_host, mail_pass, receivers, title, body_text)

    return flag


# 处理批量测试中调用的接口数据
def test_handle(futures, api_id, host, env_params, task_id):

    # 根据api_id获取api数据
    ret = {
        "erro_msg": "",
        "api_item": {}
    }
    # 获取接口参数
    try:
        api_data = APIData.m.get(id=int(api_id))
        api_item = model_to_dict(api_data, ["id", "title", "desc", "method"])
    except Exception as e:
        ret["erro_msg"] = "api_id:{},异常：{}".format(api_id, e)
        return ret

    # 验证接口关键信息是否非空
    erro_msg = verify_not_is_None(api_item, ["method"])
    if erro_msg:
        ret["erro_msg"] = erro_msg
        return ret

    # 获取此api下的所有case数据
    case_datas = CaseData.m.filter(parent_id=api_data.id)
    api_item["case_list"] = []

    for case_data in case_datas:
        case_item = model_to_dict(case_data)

        # case_item = model_to_dict(case_data, [
        #     "id", "title", "desc", "url", "status", "params", "data", "headers", "cookies", "asserts", "prefix", "rsgv"])

        if case_item["status"] == "1":    # 只有在用例是启用状态下,才会跑此用例

            # 验证用例数据必须为josn的字段,并转换成字典格式
            json_fields = ["params", "data", "headers", "cookies", "asserts", "prefix", "rsgv"]
            erro_msg = verify_is_json(case_item, json_fields)
            if erro_msg:
                case_item["erro_msg"] = erro_msg
                continue
            json_to_dict(case_item, json_fields)
            # 获取发送请求用到的字段
            req_item = get_req_item(host, api_item, case_item, env_params)
            # 返回需要的数据 assert_flag 存放用例的id
            futures.submit(send_req3, api_item, case_item, req_item, host, env_params, task_id)  # 多线程方式
            # send_req3(api_item, case_item, req_item)                    # 单线程方式

    futures.as_completed()  # 全部请求发送完毕，并处理完成后才能进行下一步

    statistics_item = {
        "success": 0,
        "fail": 0,
        "count": 0,
        "flag": False,
    }
    for case in api_item["case_list"]:
        if case["asserts_flag"]:
            statistics_item["success"] += 1
        statistics_item["count"] += 1
    statistics_item["fail"]  = statistics_item["count"] - statistics_item["success"]
    statistics_item["flag"] = True if statistics_item["count"] == statistics_item["success"] else False

    api_item["statistics_item"] = statistics_item
    ret["api_item"] = api_item
    return ret


# 发送请求前一些数据组合操作
def send_req3(api_item, case_item, req_item, host, env_params, task_id):
    # 发送请求获取结果，并发送case项目中
    r_data = send_req2(req_item, host, env_params)

    # 将case数据，响应数据放入case列表中
    case_item["r_data"] = r_data

    report_detail = {
        "task_id": task_id,
        "api_id": api_item["id"],
        "api_title": api_item["title"],
        "api_desc": api_item["desc"],
        "method": api_item["method"],
        "case_id": case_item["id"],
        "case_title": case_item["title"],
        "final_ret": r_data["asserts_flag"],
        "case_info": json.dumps(case_item),
        "c_date": datetime.datetime.now()
    }
    obj = TestReportDetail.m.create(**report_detail)
    info = {
        "id": case_item["id"],
        "title": case_item["title"],
        "asserts_flag": r_data["asserts_flag"],
        "report_detail_id": obj.pk,
    }
    # api_item["case_list"].append(case_item)
    api_item["case_list"].append(info)


# 分割逗号
def splitDH(str):
    """
        :param str: 字符串
        :return: 字符串以逗号分割，并且每个元素strip并且不要空的
                "1,2 ,2 ,3,   ," ==> ['1', '2', '2', '3']
    """
    return [i.strip() for i in str.strip().split(",") if i.strip()]


# 验证每一个断言的类
class VerifyResOne:
    """
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
    """
    # 一般关系
    general_handle_list = ["1", "2", "4", "6", "7", "8", "15", "20"]
    # len关系
    len_handle_list = ["9", "10", "12", "14"]
    # 特殊关系
    specific_handle_list = ["16", "17", "18", "19"]


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
        self.res = res
        self.item = item

    # 验证每一个断言
    def verify_res_one(self):

        if self.assert_method != "0":
            self.get_assert_real_value()
            if self.assert_erro:
                self.update_item()
                return
        try:
            if self.assert_method == "0":
                self.assert_ret = self.assert_expect_value == str(self.res.status_code)
                self.assert_real_value = self.res.status_code

            elif self.assert_method == "1" or self.assert_method == "15":
                # 分为true，flase，null，空""和字符串四种情况
                if self.assert_expect_value == "true":
                    self.assert_ret = self.assert_real_value == True
                elif self.assert_expect_value == "flase":
                    self.assert_ret = self.assert_real_value == False
                elif self.assert_expect_value == "null":
                    self.assert_ret = self.assert_real_value is None
                else:
                    self.assert_ret = self.assert_real_value == self.assert_expect_value

            elif self.assert_method == "2":
                # 分为true，flase，null，空""和字符串四种情况
                if self.assert_expect_value == "true":
                    self.assert_ret = self.assert_real_value != True
                elif self.assert_expect_value == "flase":
                    self.assert_ret = self.assert_real_value != False
                elif self.assert_expect_value == "null":
                    self.assert_ret = self.assert_real_value is not None
                elif self.assert_expect_value == "":
                    self.assert_ret = self.assert_real_value != ""
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

        self.update_item()

    def update_item(self):

        try:
            # 尝试将实际结果转化成json格式
            if type(self.assert_real_value) == dict or type(self.assert_real_value) == list:
                self.assert_real_value = json.dumps(self.assert_real_value, ensure_ascii=False)
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
            aev = json.loads(self.assert_expect_value.replace("\u0001", "\\u0001"))
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
            self.erro_msg = "对比时出错：{}".format(e)
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
        erro_msg = ""

        try:
            if self.assert_method == "16":
                erro_msg = self.a_in_b(self.assert_expect_value, self.assert_real_value)
            elif self.assert_method == "17":
                erro_msg = self.a_in_b(self.assert_real_value, self.assert_expect_value)
            elif self.assert_method == "18":
                erro_msg = self.list_not_rank_eq(self.assert_real_value, self.assert_expect_value)
            elif self.assert_method == "19":
                if type(self.assert_real_value) == dict and type(self.assert_expect_value) == dict:
                    keys1 = list(self.assert_expect_value.keys())
                    keys2 = list(self.assert_real_value.keys())
                    erro_msg = self.list_not_rank_eq(keys1, keys2)
                else:
                    erro_msg = "此断言方法只可判断{}-{}!"
                if erro_msg:
                    self.assert_erro = erro_msg
                else:
                    self.assert_ret = True
        except Exception as e:
            erro_msg = "校验时出错：{}".format(e)
        if erro_msg:
            self.assert_erro = erro_msg
        else:
            self.assert_ret = True


    @staticmethod
    # 对比两个{}或[] 中的元素 是否in的关系， a只可少，不可多，并且值一致
    def a_in_b(a, b):
        # 查看ａ in b
        erro_msg = ""
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
            #     erro_msg += "缺少字段：{}\t".format(lack)
            if overstep:
                erro_msg += "多出字段：{}\t".format(overstep)
            if inconformity:
                erro_msg += "字段值不一致：{}".format(inconformity)

        elif type(a) == list and type(b) == list:
            b = copy.deepcopy(b)
            for i in a:
                if i in b:
                    b.remove(i)
                else:
                    return "期望结果与实际结果不一致"

        else:
            erro_msg = "格式不统一:{},{}。只可比较同为list 或 同为dict".format(type(a), type(b))

        return erro_msg

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


