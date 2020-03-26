from.view_basic import *

def get_case_data(req, case_id):
    case_id = int(case_id)
    # 返回的字典格式数据
    r_data = {}
    try:
        # 从case_data数据库中查找id为case_id的数据
        data = CaseData.m.get(pk=case_id)
        # 有两个参数fields 只输出哪些字段和exclude 不输出哪些字段来配置输出
        dict_data = model_to_dict(data)
        # print("dict_data", dict_data)

    except Exception as e:
        # 查询之后不符合条件或者不存在就会报异常
        r_data["ret"] = False
        r_data["erro"] = "没有这个case或者已经被删除:{}".format(e)
    else:
        # 要格式化输出的
        p_list = ["data", "cookies", "res_headers", "res_body"]
        for i in p_list:
            if dict_data[i]:
                try:
                    dict_data[i] = json.dumps(
                        json.loads(dict_data[i]), indent=4, ensure_ascii=False)
                except:
                    pass

        # 要转换成字典的
        p_list2 = ["params", "headers", "asserts", "prefix", "rsgv"]
        for i in p_list2:
            if dict_data[i]:
                dict_data[i] = json.loads(dict_data[i])

        r_data["ret"] = True
        r_data['case_data'] = dict_data

    json_data = json.dumps(r_data)
    return JsonResponse(json_data, safe=False)


@login_required
def save_case(req):
    data = get_case_param(req)
    if data["ret"]:
        item = data["item"]

        # 将这几个参数的值转换成json格式
        dict_to_json(item, ["params", "data", "cookies", "headers", "asserts", "prefix", "rsgv"])

        del item["id"] # 新增不需要id字段
        new_case = CaseData.m.create(**item)

        r_data = {"ret":True, "warning":data["warning"], "id":new_case.id, "title":new_case.title}
        return JsonResponse(json.dumps(r_data), safe=False)

    else:
        return JsonResponse(json.dumps(data), safe=False)

@login_required
def delete_case(req):
    r_data = {}
    case_id = req.POST.get("case_id", None)
    if case_id:
        try:
            CaseData.m.filter(pk=int(case_id)).delete()
            r_data["ret"] = True
        except Exception as e:
            r_data["ret"] = False
            r_data["erro_msg"] = "数据库删除case出错：".format(e)
    else:
        r_data["ret"] = False
        r_data["erro_msg"] = "case_id为空："

    return JsonResponse(json.dumps(r_data), safe=False)


@login_required
def update_case(req):
    data = get_case_param(req)
    if data["ret"]:
        item = data["item"]

        try:
            # 将这几个参数的值转换成json格式
            dict_to_json(item, ["params", "data", "cookies", "headers", "asserts", "prefix", "rsgv"])
        except Exception as e:
            data["warning"] = "参数转换成json时失败:{}".format(e)
            return JsonResponse(json.dumps(data), safe=False)

        try:
            # erro_msg = verify_not_is_None(item, ["id"])       # 验证id，但是前段验证过了，咱不做处理
            CaseData.m.filter(id=item["id"]).update(**item)
        except Exception as e:
            data["warning"] = "更新表时失败:{}".format(e)
            return JsonResponse(json.dumps(data), safe=False)

        r_data = {"ret":True, "warning":data["warning"]}
        return JsonResponse(json.dumps(r_data), safe=False)

    else:
        return JsonResponse(json.dumps(data), safe=False)


def get_case_param(req, title_flag=True):
    """

    :param req:
    :param title_flag: 是否验证title为不为空, true为验证
    :return:
        返回的数据都为python格式
    """

    item = {}
    warning = []

    p = req.POST
    item['title'] = p.get("case_title", None)
    item["desc"] = p.get("case_desc", None)
    item["url"] = p.get("url", None)

    item["status"] = p.get("case_status", "")

    item['data'] = p.get("params", None)
    item['headers'] = p.get("headers", None)
    item['cookies'] = p.get("cookies", None)
    # item['res_headers'] = p.get("res_headers", None)
    # item['res_body'] = p.get("res_body", None)

    item['parent_id_id'] = p.get("c_api_id", None)

    # 需要处理后删掉的字段
    item['id'] = p.get("c_case_id", None)       # 保存case不需要此字段，更新case需要
    item["header_key"] = p.getlist("header_key", None)
    item["header_value"] = p.getlist("header_value", None)
    item["param_key"] = p.getlist("param_key", None)
    item["param_value"] = p.getlist("param_value", None)

    # 获取前置信息
    item["prefix_status"] = p.getlist("prefix_status", "")
    item["prefix_case_id"] = p.getlist("prefix_case_id", "")
    item["prefix_set_var_name"] = p.getlist("prefix_set_var_name", "")
    item["prefix_key"] = p.getlist("prefix_key", "")
    # item["prefix_real_value"] = p.getlist("prefix_real_value", "")

    # 获取后置信息
    item["rsgv_status"] = p.getlist("rsgv_status", "")
    item["rsgv_name"] = p.getlist("rsgv_name", "")
    item["rsgv_key"] = p.getlist("rsgv_key", "")
    # item["rsgv_real_value"] = p.getlist("rsgv_real_value", "")

    # 获取断言信息
    item["assert_status"] = p.getlist("verify_status", None)
    item["assert_key"] = p.getlist("verify_key", None)
    item["assert_method"] = p.getlist("verify_method", None)
    item["assert_expect_value"] = p.getlist("verify_expect_ret", None)
    # item["assert_real_ret"] = p.getlist("assert_real_ret", None)

    # 处理某些参数
    erro_msg = case_item_handel(item, warning, title_flag)
    if erro_msg:
        return {"ret":False, "erro_msg":erro_msg}

    return {"item":item, "warning":warning, "ret":True}


def case_item_handel(item, warning, title_flag):
    """
    :param item: 从请求体中获取的原生的参数，还未处理
    :param warning: 有错误但是不致命的错误，只会在页面单接口测试中提示
    :param title_flag: 区分保存和接口测试，保存需要标题，接口测试不需要标题
    :return:
    """

    # 验证json格式的字段是否正确
    erro_msg = verify_is_json(item, ["data", "cookies"])
    if erro_msg:
        return erro_msg
    # 验证不能为空的字段是否正确
    if title_flag:
        erro_msg = verify_not_is_None(item, ["title", "url"])
        if erro_msg:
            return erro_msg

    # 中数mongo库中的_id:'220000\x016e665be0-012e-1000-e000-282cc0a80043\\u00011949100100000015632911'
    # 需要转换成：2200006e665be0-012e-1000-e000-282cc0a80043\u00011949100100000015632911
    # 需要转化的：param_value  data，从excel导入到库的需要在处理asserts
    item["data"] = item["data"].replace("\u0001", "\\u0001")
    item["param_value"] = [i.replace("\u0001", "\\u0001") for i in item["param_value"]]
    # 键值对格式转换成dict格式
    item["headers"] = kv_switch_dict(item["header_key"], item["header_value"], warning)
    item["params"] = kv_switch_dict(item["param_key"], item["param_value"], warning)

    item["prefix"] = []  # [{prefix_item}, {prefix_item}...]
    try:
        if item["prefix_status"]:
            for i in range(len(item["prefix_status"])):
                prefix_item = {
                    "prefix_status": item["prefix_status"][i],              # 前置状态,是否启用
                    "prefix_case_id": item["prefix_case_id"][i],            # 调用id
                    "prefix_set_var_name": item["prefix_set_var_name"][i],  # 变量名称
                    "prefix_key": item["prefix_key"][i],                    # 变量键
                    # "prefix_real_value": item["prefix_real_value"][i],      # 实际值
                }
                item["prefix"].append(prefix_item)
    except Exception as e:
        return "组合前置时出错：{}".format(e)

    item["rsgv"] = []  # [{rsgv_item}, {rsgv_item}...]
    try:
        if item["rsgv_status"]:
            for i in range(len(item["rsgv_status"])):
                rsgv_item = {
                    "rsgv_status": item["rsgv_status"][i],          # 后置状态,是否启用
                    "rsgv_name": item["rsgv_name"][i],              # 变量名字
                    "rsgv_key": item["rsgv_key"][i],                # 变量键
                    # "rsgv_real_value": item["rsgv_real_value"][i],  # 实际值
                }
                item["rsgv"].append(rsgv_item)
    except Exception as e:
        return "组合后置时出错：{}".format(e)

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
        return "组合断言时出错：{}".format(e)

    # 将所有json格式数据转换成字典
    json_to_dict(item, ["data", "cookies"])

    # 删除多余字段
    del item["header_key"]
    del item["header_value"]

    del item["param_key"]
    del item["param_value"]

    del item["assert_status"]
    del item["assert_key"]
    del item["assert_method"]
    del item["assert_expect_value"]

    del item["prefix_status"]
    del item["prefix_case_id"]
    del item["prefix_set_var_name"]
    del item["prefix_key"]
    # del item["prefix_real_value"]

    del item["rsgv_status"]
    del item["rsgv_name"]
    del item["rsgv_key"]
    # del item["rsgv_real_value"]







