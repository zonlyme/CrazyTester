from .view_basic import *

@login_required
def get_api_data(req, api_id):
    api_id = int(api_id)
    # 返回的字典格式数据
    r_data = {}
    try:
        # 从数据库中查找id为api_id的数据
        api_data = APIData.m.get(pk=api_id)
        # 有两个参数fields 只输出哪些字段和exclude 不输出哪些字段来配置输出
        api_data = model_to_dict(api_data)

        # 获取这个接口的所有用例,并只要id和title字段
        case_data = []
        cases = CaseData.m.filter(parent_id=api_id)
        for case in cases:
            item = model_to_dict(case, fields=["id", "title"])
            case_data.append(item)
        # print(case_data)

        r_data['api_data'] = api_data
        r_data['case_data'] = case_data
        r_data["ret"] = True

    except Exception as e:
        # 查询之后不符合条件或者不存在就会报异常
        r_data["ret"] = False
        r_data["erro"] = "没有这个API或者已经被删除！{}".format(e)
        # print("get_api_data错误：{}".format(e))

    json_data = json.dumps(r_data)
    return JsonResponse(json_data, safe=False)

@login_required
def deleteAPI(req, api_id):
    data = {}
    try:
        # 奖这个api和他的case更改为删除状态，
        CaseData.m.filter(parent_id=int(api_id)).delete()
        APIData.m.filter(id=int(api_id)).delete()

        data["ret"] = True
    except Exception as e:
        data["ret"] = False
        data['erro_msg'] = "删除失败:{}".format(e)

    json_data = json.dumps(data)
    return JsonResponse(json_data, safe=False)

@login_required
def saveAPI(req, node_id):
    r_data = {}

    # 获取表单中的参数
    item = get_api_param(req)
    # 验证api字段的必填项
    # fileds = ["title", "method", "url"]
    fileds = ["title", "method"]
    erro_fileds = verify_not_is_None(item, fileds)

    # 如果处理参数部分有错误，直接返回结果和错误信息
    if erro_fileds:
        r_data["ret"] = False
        r_data["erro"] = "{}不能为空！".format(erro_fileds)
    else:
        try:
            item["parent_id_id"] = int(node_id)
            # print(item)
        except:
            r_data["erro"] = "parent_id有误！"
            r_data["ret"] = False
        else:
            # 新增数据不需要id
            del item["id"]

            # try:
            obj = APIData.m.create(**item)
            r_data['ret'] = True
            r_data['id'] = obj.pk
            r_data["parent_id"] = obj.parent_id_id
            # except Exception as e:
            #     r_data["ret"] = False
            #     r_data["erro"] = "数据库插入表时出现异常：".format(e)

    json_data = json.dumps(r_data)
    return JsonResponse(json_data, safe=False)

@login_required
def updateAPI(req):
    warning = []
    erro = []
    r_data = {}

    # 获取表单中的参数
    item = get_api_param(req)
    # 验证api字段的必填项
    # fileds = ["id", "title", "method", "url"]
    fileds = ["id", "title", "method"]
    erro_fileds = verify_not_is_None(item, fileds)

    # 如果处理参数部分有错误，直接返回结果和错误信息
    if erro_fileds:
        r_data["ret"] = False
        r_data["erro"] = "{}不能为空！".format(erro_fileds)
    else:
        try:
            # 还是用之前的parent_id(更新操作parent_id不会变)
            api_id = int(item["id"])
            api_data = APIData.m.get(id=api_id)
            item["parent_id"] = api_data.parent_id
            APIData.m.filter(id=api_id).update(**item)
            r_data['ret'] = True
            r_data["warning"] = warning
        except Exception as e:
            erro.append("入库更新表时出现异常：".format(e))
            r_data["ret"] = False
            r_data["erro"] = ",".join(erro)

    json_data = json.dumps(r_data)
    return JsonResponse(json_data, safe=False)


# 获取api部分需要的参数
def get_api_param(req):

    item = {}
    p = req.POST
    item['id'] = p.get("c_api_id", "")
    item['title'] = p.get("api_title", "")
    item["desc"] = p.get("api_desc", "")
    item['method'] = p.get("method", "")
    # item['url'] = p.get("url", "")

    return item


