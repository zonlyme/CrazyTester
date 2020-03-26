from .view_basic import *


# 获取nva部分的数据
def get_nav(req):
    # 所有构造好的节点数据列表
    nav_data = []
    # 获取全部节点数据
    data_list = NavNode.m.filter(isDelete=False)

    for data in list(data_list):
        # 构造第一级节点的item
        html = "<span class='fodler' value='{}'>{}</span>".format(data.pk, data.node_name)
        item = {"text": html}
        # 获取当前这个一级节点下的所有子节点
        get_child_node(item, data.pk)
        # 获取完毕之后，加入到列表中，获取下一个一级节点的所有子节点
        nav_data.append(item)

    json_data = json.dumps(nav_data)

    return JsonResponse(json_data, safe=False)


# 当前的数据列表, 节点id=node_id
def get_child_node(item, node_id):

    api_list = APIData.m.filter(parent_id=node_id)
    item["tags"] = ["{}".format(len(api_list))]
    # 创建一个集合，放入所有接口数据
    api_data_node = item.setdefault("nodes", [])
    # print(list(api_list))

    # 构建所有接口数据，并放入接口集合中
    for api_data in api_list:
        case_count = CaseData.m.filter(parent_id=api_data.id).count()
        api_item = {
            "text": "<span class='api' value='{}'>{} -- {}</span>".format(api_data.id, api_data.id, api_data.title),
            # "href": "/interface/get_api_data/".format()
            "tags": ["{}".format(case_count)]
        }

        api_data_node.append(api_item)


# 获取所有节点(首层)
def get_all_node(req):
    node_data = []
    data_list = NavNode.m.filter(isDelete=False)
    for data in list(data_list):
        item = {}
        item["id"] = data.pk
        item["name"] = data.node_name
        node_data.append(item)

    json_data = json.dumps(node_data)
    return JsonResponse(json_data, safe=False)


# 节点增删改
@login_required
def nodeOperate(req):
    p = req.POST
    operate = p["operate"]
    new_node_data = {}
    res_data = {}
    new_node_data["node_name"] = p["fname"]

    # 根据node_id删除api, case
    def delete_api(node_id):
        apis = APIData.m.filter(parent_id=node_id)
        for api in apis:
            CaseData.m.filter(parent_id=int(api.id)).delete()
            try:
                APIData.m.filter(id=int(api.id)).delete()
            except Exception as e:
                res_data["ret"] = False
                res_data["erro_msg"] = "删除时失败:{}".format(e)
        NavNode.m.filter(id=node_id).delete()


    if operate == "newFodler":
        # 创建节点
        obj = NavNode.m.create(**new_node_data)
        res_data['id'] = obj.pk

    elif operate == "editeFodler":
        node_id = int(p["pNodeId"])
        NavNode.m.filter(id=node_id).update(**new_node_data)

    elif operate == "deleteFodler":
        node_id = int(p["pNodeId"])
        # 找到这个节点下的所有子节点
        delete_api(node_id)

    res_data["ret"] = True

    return JsonResponse(json.dumps(res_data), safe=False)




