from api.view_basic import *


case_json_filed = ["params", "data", "sample_data",
        "cookies", "headers", "asserts", "prefix", "rsgv", "rsgh"]


@login_required
@require_http_methods(["GET"])
def get_case_list(req):
    """
        通过api_id或case_id获取 某个用例下的所有用例
        优先根据case_id查询
    """
    api_id = req.GET.get("api_id", "")
    case_id = req.GET.get("case_id", "")

    if not api_id and not case_id:
        return response_400("缺少参数：api_id or case_id !")

    if case_id:
        try:
            case_model = ApiCase.m.get(pk=case_id)
            api_id = case_model.api_id
        except:
            return response_400("不存在的用例:{}!".format(case_id))

    try:
        api_data_raw = ApiApi.m.get(pk=api_id)
    except:
        return response_400("不存在的接口:{}!".format(api_id))

    api_data = model_to_dict(api_data_raw, fields=["id", "method", "title", "desc"])

    group_data_raw = ApiGroup.m.get(pk=api_data_raw.group_id)
    group_data = model_to_dict(group_data_raw, fields=["id", "title"])

    project_data_raw = ApiProject.m.get(pk=group_data_raw.project_id)
    project_data = model_to_dict(project_data_raw, exclude=["isDelete", "c_date", "u_date"])
    # 获取这个接口的所有用例,并只要id和title字段
    case_list = []
    cases = ApiCase.m.filter(api=api_id)
    for case in cases:
        item = model_to_dict(case, fields=["id", "title"])
        case_list.append(item)

    r_data = {
        "project_data": project_data,
        "group_data": group_data,
        "api_data": api_data,
        "case_list": case_list,
    }

    return response_200(**r_data)


@require_http_methods(["GET"])
def get_case_data(req):

    id = req.GET.get("id", "")
    try:
        data_model = ApiCase.m.get(pk=id)
        dict_data = model_to_dict(data_model)
        dict_data["u_date"] = data_model.u_date.strftime('%Y-%m-%d %H:%M:%S')
        dict_data["c_date"] = data_model.c_date.strftime('%Y-%m-%d %H:%M:%S')

    except Exception as e:
        return response_400("没有这个case或者已经被删除:{}".format(e))

    else:
        for i in case_json_filed:
            if dict_data[i]:
                dict_data[i] = json.loads(dict_data[i])

        return response_200(data=dict_data)


@require_http_methods(["POST"])
@login_required
def save_case(req):
    item, warning = get_case_param(req)
    # 将这几个参数的值转换成json格式
    dict_to_json(item, case_json_filed)

    try:
        del item["id"]  # 新增不需要id字段
        get_user_info_for_session(req, item, create=True)
        new_case = ApiCase.m.create(**item)

    except Exception as e:
        return response_400("新增失败!{}".format(e))

    else:
        return response_200(warning=warning, id=new_case.id)


@require_http_methods(["POST"])
@login_required
def update_case(req):
    item, warning = get_case_param(req)
    # 将这几个参数的值转换成json格式
    dict_to_json(item, case_json_filed)

    get_user_info_for_session(req, item)
    try:
        ApiCase.m.filter(id=item["id"]).update(**item)
    except Exception as e:
        return response_400("更新失败!{}".format(e))
    else:
        return response_200(warning=warning)


@require_http_methods(["GET"])
@login_required
def delete_case(req):

    id = req.GET.get("id", None)

    if not id:
        response_400("缺少参数:用例id：")
    try:
        item = {"isDelete": True}
        get_user_info_for_session(req, item)
        ApiCase.m.filter(pk=int(id)).delete()
    except Exception as e:
        return response_400("删除用例时出错：".format(e))

    return response_200()


def get_case_param(req, title_flag=True):
    """
    :param title_flag: 发送请求不校验标题,增删改用例需要校验
    :return:返回的 用例参数数据都为字典格式
    """

    warning = []
    item = {}
    p = req.POST

    item['title'] = p.get("case_title", "")
    item["desc"] = p.get("case_desc", "")
    item["url"] = p.get("url", "")
    item["method"] = p.get("method", "")
    item["status"] = p.get("case_status", "")
    item["status"] = True if item["status"] == "true" else False
    item['data'] = p.get("params", "")
    item['sample_data'] = p.get("sample_data", "")
    item['headers'] = p.get("headers", "")
    item['cookies'] = p.get("cookies", "")

    item['api_id'] = p.get("api_id", "")

    # 不需要的字段
    item['id'] = p.get("case_id", "")       # 保存case不需要此字段，更新case需要
    item["header_key"] = p.getlist("header_key", "")
    item["header_value"] = p.getlist("header_value", "")
    item["param_key"] = p.getlist("param_key", "")
    item["param_value"] = p.getlist("param_value", "")

    # 获取前置信息
    item["prefix_status"] = p.getlist("prefix_status", "")
    item["prefix_case_id"] = p.getlist("prefix_case_id", "")
    item["prefix_set_var_name"] = p.getlist("prefix_set_var_name", "")
    item["prefix_key"] = p.getlist("prefix_key", "")
    # item["prefix_real_value"] = p.getlist("prefix_real_value", "")

    # 获取后置信息
    item["rsgv_status"] = p.getlist("rsgv_status", "")
    item["rsgv_name"] = p.getlist("rsgv_name", "")
    item["rsgv_set_method"] = p.getlist("rsgv_set_method", "")
    item["rsgv_key"] = p.getlist("rsgv_key", "")
    # item["rsgv_real_value"] = p.getlist("rsgv_real_value", "")

    item["rsgh_status"] = p.getlist("rsgh_status", "")
    item["rsgh_name"] = p.getlist("rsgh_name", "")
    item["rsgh_set_method"] = p.getlist("rsgh_set_method", "")
    item["rsgh_key"] = p.getlist("rsgh_key", "")
    # item["rsgh_real_value"] = p.getlist("rsgh_real_value", "")

    item["set_global_cookies"] = True if p.get("set_global_cookies", False) == "true" else False
    item["clear_global_cookies"] = True if p.get("clear_global_cookies", False) == "true" else False

    # item['set_global_cookies'] = p.get("set_global_cookies", False)
    # item['clear_global_cookies'] = p.get("clear_global_cookies", False)
    # item["set_global_cookies"] = True if item["set_global_cookies"] == "true" else False
    # item["clear_global_cookies"] = True if item["clear_global_cookies"] == "true" else False

    # 获取断言信息
    item["assert_status"] = p.getlist("verify_status", "")
    item["assert_key"] = p.getlist("verify_key", "")
    item["assert_method"] = p.getlist("verify_method", "")
    item["assert_expect_value"] = p.getlist("verify_expect_ret", "")
    # item["assert_real_ret"] = p.getlist("assert_real_ret", "")

    # print(item)

    # 发送请求不校验标题,增删改用例需要校验
    if title_flag:
        if not item["title"]:
            response_400_raise_exception("请输入标题！")

    # 中数mongo库中的_id:'220000\x016e665be0-012e-1000-e000-282cc0a80043\\u00011949100100000015632911'
    # 需要转换成：2200006e665be0-012e-1000-e000-282cc0a80043\u00011949100100000015632911
    # 需要转化的：param_value  data，从excel导入到库的需要在处理asserts
    # item["data"] = item["data"].replace("\u", "\\u")
    item["data"] = item["data"].replace("\u0001", "\\u0001")
    item["param_value"] = [i.replace("\u0001", "\\u0001") for i in item["param_value"]]
    item["assert_expect_value"] = [i.replace("\u0001", "\\u0001") for i in item["assert_expect_value"]]

    item["params"] = {}
    # 键值对格式转换成dict格式
    for i in range(len(item["param_key"])):
        if item["param_key"][i].strip():
            item["params"][item["param_key"][i]] = item["param_value"][i]
        else:
            warning.append("params名称为空的参数已被忽略！")

    item["headers"] = {}
    # 键值对格式转换成dict格式
    for i in range(len(item["header_key"])):
        if item["header_key"][i].strip():
            item["headers"][item["header_key"][i]] = item["header_value"][i]
        else:
            warning.append("headers名称为空的参数已被忽略！")

    item["prefix"] = []  # [{prefix_item}, {prefix_item}...]
    try:
        if item["prefix_status"]:
            item["prefix_status"] = p.getlist("prefix_status", "")

            for i in range(len(item["prefix_status"])):
                prefix_item = {
                    "prefix_status": item["prefix_status"][i],              # 前置状态,是否启用
                    "prefix_case_id": item["prefix_case_id"][i],            # 调用id
                    "prefix_set_var_name": item["prefix_set_var_name"][i],  # 变量名称
                    "prefix_key": item["prefix_key"][i],                    # 变量键
                }
                item["prefix"].append(prefix_item)
    except Exception as e:
        response_400_raise_exception("前置参数不合法!{}".format(e))

    item["rsgv"] = []  # [{rsgv_item}, {rsgv_item}...]
    try:
        if item["rsgv_status"]:
            for i in range(len(item["rsgv_status"])):
                rsgv_item = {
                    "rsgv_status": item["rsgv_status"][i],          # 状态,是否启用
                    "rsgv_name": item["rsgv_name"][i],              # 变量名字
                    "rsgv_set_method": item["rsgv_set_method"][i],  # 添加方式
                    "rsgv_key": item["rsgv_key"][i],                # 变量键
                }
                item["rsgv"].append(rsgv_item)
    except Exception as e:
        response_400_raise_exception("响应体设置全局变量 参数不合法!{}".format(e))

    item["rsgh"] = []  # [{rsgh_item}, {rsgh_item}...]
    try:
        if item["rsgh_status"]:
            for i in range(len(item["rsgh_status"])):
                rsgh_item = {
                    "rsgh_status": item["rsgh_status"][i],  # 状态,是否启用
                    "rsgh_name": item["rsgh_name"][i],  # 变量名字
                    "rsgh_set_method": item["rsgh_set_method"][i],  # 设置方式
                    "rsgh_key": item["rsgh_key"][i],  # 变量键
                }
                item["rsgh"].append(rsgh_item)
    except Exception as e:
        response_400_raise_exception("响应头设置全局头 参数不合法!{}".format(e))

    item["asserts"] = []    # [{assert_item}, {assert_item}...]
    try:
        if item["assert_key"]:
            for i in range(len(item["assert_key"])):
                assert_item = {
                    "assert_status": item["assert_status"][i],          # 断言状态
                    "assert_key": item["assert_key"][i],                 # 断言键
                    "assert_method": item["assert_method"][i],           # 断言方式
                    "assert_expect_value": item["assert_expect_value"][i],  # 断言期望值
                }
                item["asserts"].append(assert_item)
    except Exception as e:
        response_400_raise_exception("断言参数不合法!{}".format(e))

    # 将所有json格式数据转换成字典
    erro_msg = verify_is_json_and_switch(item, ["data", "sample_data", "cookies"])
    if erro_msg:
        response_400_raise_exception(erro_msg)

    # 整理出case部分真正需要的字段
    case_item = dict()
    case_item['id'] = item['id']
    case_item['title'] = item['title']
    case_item['desc'] = item['desc']
    case_item['url'] = item['url']
    case_item['status'] = item['status']
    case_item['params'] = item['params']  # 请求参数
    case_item['data'] = item['data']      # 请求体
    case_item['sample_data'] = item['sample_data']      # 样例数据
    case_item['headers'] = item['headers']
    case_item['cookies'] = item['cookies']
    case_item['api_id'] = item['api_id']

    case_item['prefix'] = item['prefix']
    case_item['rsgv'] = item['rsgv']
    case_item['rsgh'] = item['rsgh']
    case_item['set_global_cookies'] = item['set_global_cookies']
    case_item['clear_global_cookies'] = item['clear_global_cookies']
    case_item['asserts'] = item['asserts']

    # for key in case_item.keys():
    #     print(key, type(case_item[key]), case_item[key])

    return case_item, ",".join(warning)

