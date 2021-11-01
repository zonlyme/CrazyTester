from api.view_basic import *


@login_required
@require_http_methods(["GET"])
def get_api_list(req):
    group_id = req.GET.get("group_id", "")

    if not group_id:
        return response_400("缺少参数或参数值：id")

    apis = ApiApi.m.filter(group=group_id)
    datas = []
    for api in list(apis):
        api_data = model_to_dict(api, exclude=["isDelete"])
        api_data["case_count"] = ApiCase.m.filter(api=api.id).count()
        datas.append(api_data)

    return response_200(datas=datas)


@require_http_methods(["POST"])
@login_required
def add_api(req):

    item = get_api_param(req)

    item["group_id"] = req.POST.get("group_id", "")

    if not item["group_id"]:
        return response_400("缺少参数:group_id")

    if not item["title"]:
        return response_400("请输入接口名称!")
    try:
        del item["id"]
        get_user_info_for_session(req, item, create=True)
        obj = ApiApi.m.create(**item)
        return response_200(id=obj.id)
    except Exception as e:
        return response_400("创建失败！{}".format(e))


@require_http_methods(["POST"])
@login_required
def delete_api(req):

    api_id = req.POST.get("api_id", "")

    try:
        item = {"isDelete": True}
        get_user_info_for_session(req, item)

        ApiCase.m.filter(api=int(api_id)).update(**item)
        ApiApi.m.filter(id=int(api_id)).update(**item)

        return response_200()

    except Exception as e:
        return response_400("删除失败:{}".format(e))


@require_http_methods(["POST"])
@login_required
def update_api(req):

    item = get_api_param(req)

    if not item["id"]:
        return response_400("请选择接口!")

    if not item["title"]:
        return response_400("请输入接口名称!")

    try:
        get_user_info_for_session(req, item)
        ApiApi.m.filter(id=item["id"]).update(**item)
        return response_200()

    except Exception as e:
        return response_400("新增时出错：{}".format(e))


# 获取api部分需要的参数
def get_api_param(req):

    item = {}
    p = req.POST
    item['id'] = p.get("api_id", "")
    item['title'] = p.get("api_title", "")
    item["desc"] = p.get("api_desc", "")
    item['method'] = p.get("method", "")

    if item["method"] not in ["GET", "POST"]:
        response_400_raise_exception("请求方式只可为 GET, POST")

    return item


