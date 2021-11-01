from api.view_basic import *


@require_http_methods(["GET"])
def get_workwx_user_group(req):

    datas = []

    try:
        infos = WorkWxUserGroup.m.filter()
        for i in infos:
            datas.append(model_to_dict(i))

    except Exception as e:
        return response_400("错误信息：{}".format(e))

    return response_200(data=datas)


@require_http_methods(["GET"])
def get_workwx_group_chat(req):

    datas = []

    try:
        infos = WorkWxGroupChat.m.filter()
        for i in infos:
            datas.append(model_to_dict(i))

    except Exception as e:
        return response_400("错误信息：{}".format(e))

    return response_200(data=datas)


@require_http_methods(["GET"])
def get_email_user_group(req):

    datas = []

    try:
        infos = EmailUserGroup.m.filter()
        for i in infos:
            datas.append(model_to_dict(i))

    except Exception as e:
        return response_400("错误信息：{}".format(e))

    return response_200(data=datas)

