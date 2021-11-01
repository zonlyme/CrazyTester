from api.view_basic import *


@require_http_methods(["GET"])
@login_required
def get_all_project(req):

    datas = []
    user_permission = "0"
    try:
        pros = get_all_projects()
        username = str(req.session.get("user"))

        for pro in pros:
            # 用户可见项目权限
            if username in str_to_list(pro.users or ""):
                datas.append(model_to_dict(pro, fields=["id", "title"]))

        # 可新增项目权限
        user = User.objects.get(username=username)
        if user.is_superuser:
            user_permission = "1"

        # kejian_users = str_to_list(ApiUser.m.get(type_id="2").users or "")
        # if username in kejian_users:
        #     user_permission = "1"

        return response_200(data=datas, user_permission=user_permission)
    except Exception as e:
        return response_400("获取项目列表出错！{}".format(e))


@require_http_methods(["POST"])
@login_required
def add_project(req):

    title = req.POST.get("title", "")

    if not title:
        return response_400("缺少参数或参数值：title！")
    try:
        item = {
            "title": title,
            "users": str(req.session.get("user"))
        }
        get_user_info_for_session(req, item, create=True)

        obj = ApiProject.m.create(**item)
        return response_200()

    except Exception as e:
        return response_400("创建时出错:{}".format(e))


@require_http_methods(["POST"])
@login_required
def delete_project(req):

    id = req.POST.get("id", "")

    if not id:
        return response_400("缺少参数或参数值!:id")

    try:
        ApiProject.m.get(id=id)
    except Exception as e:
        return response_400("不存在的项目!:{}".format(e))

    else:
        try:
            group_list = ApiGroup.m.filter(project=id)

            item = {
                "isDelete": True
            }
            get_user_info_for_session(req, item)

            for group in list(group_list):
                delete_group2(group.id, item)

            ApiProject.m.filter(id=id).update(**item)
            return response_200()

        except Exception as e:
            return response_400("删除时出错:{}".format(e))


@require_http_methods(["POST"])
@login_required
def update_project(req):
    id = req.POST.get("id", "")
    title = req.POST.get("title", "")

    if not id or not title:
        return response_400("缺少参数或参数值：id，title!")

    item = {
        "title": title
    }
    get_user_info_for_session(req, item)
    try:
        ApiProject.m.filter(id=id).update(**item)
        return response_200()

    except Exception as e:
        return response_400("更新时出错:{}".format(e))


@require_http_methods(["GET"])
@login_required
def get_all_group(req):

    project_id = req.GET.get("id", "")

    if not project_id:
        return response_400("缺少参数或参数值：id!")

    datas = []
    try:
        project_modle = ApiProject.m.get(id=project_id)
    except:
        return response_400("不存在的分组：{}".format(project_id))
    else:
        group_modles = ApiGroup.m.filter(project=project_id)
        for group in group_modles:
            item = {
                "id": group.id,
                "title": group.title,
                "case_count": ApiApi.m.filter(group=group.id).count()
            }
            datas.append(item)
        return response_200(data=datas, pro_title=project_modle.title)


@require_http_methods(["POST"])
@login_required
def add_group(req):
    title = req.POST.get("title", "")
    project_id = req.POST.get("project_id", "")

    if not title or not project_id:
        return response_400("缺少参数或参数值：title!")
    try:
        item = {
            "title": title,
            "project_id": int(project_id),
        }
        get_user_info_for_session(req, item, create=True)
        obj = ApiGroup.m.create(**item)
        return response_200()
    except Exception as e:
        return response_400("创建时出错:{}".format(e))


def delete_group2(group_id, item):
    try:
        apis = ApiApi.m.filter(group=group_id)
        for api in apis:
            ApiCase.m.filter(api=api.id).update(**item)
            ApiApi.m.filter(id=api.id).update(**item)

        ApiGroup.m.filter(id=group_id).update(**item)
    except Exception as e:
        response_400_raise_exception("删除时出错2！:{}".format(e))


@require_http_methods(["POST"])
@login_required
def delete_group(req):

    id = req.POST.get("id", "")

    if not id:
        return response_400("缺少参数或参数值：id")

    try:
        ApiGroup.m.get(id=id)
    except Exception as e:
        return response_400("此分组不存在!:{}".format(e))
    try:
        item = {
            "isDelete": True
        }
        get_user_info_for_session(req, item)
        delete_group2(id, item)
        return response_200()

    except Exception as e:
        return response_400("删除时出错:{}".format(e))


@require_http_methods(["POST"])
@login_required
def update_group(req):

    id = req.POST.get("id", "")
    title = req.POST.get("title", "")

    if not id or not title:
        return response_400("请选择分组并填写分组名称!")

    item = {
        "title": title
    }
    get_user_info_for_session(req, item)
    try:
        ApiGroup.m.filter(id=id).update(**item)
        return response_200()
    except Exception as e:
        return response_400("更新时出错:{}".format(e))


