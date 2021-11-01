from django.http import JsonResponse


def json_response(msg="ok", ret=None, code=200, status=200, raise_exception=None, **kwargs):

    info = {
        "code": code,
        "msg": msg,
        "ret": ret
    }
    info.update(kwargs)

    if raise_exception:
        info.update({"status": status})
        info.update(**kwargs)
        raise BreakFuncExceptin(info)

    return JsonResponse(info, safe=False, status=status, json_dumps_params={"ensure_ascii": False})


def response_200(msg="ok！", raise_exception=None, **kwargs):
    return json_response(msg=msg, ret=True, code=200, status=200, raise_exception=raise_exception, **kwargs)


def response_400(msg="参数错误！", raise_exception=None, **kwargs):
    return json_response(msg=msg, ret=False, code=400, status=400, raise_exception=raise_exception, **kwargs)


def response_404(msg="NOT FOUND！", raise_exception=None, **kwargs):
    return json_response(msg=msg, ret=False, code=404, status=404, raise_exception=raise_exception, **kwargs)


def response_500(msg="服务器内部错误！", raise_exception=None, **kwargs):
    return json_response(msg=msg, ret=False, code=500, status=500, raise_exception=raise_exception, **kwargs)


def response_200_raise_exception(msg="ok！", **kwargs):
    return response_200(msg=msg, raise_exception=True, **kwargs)


def response_400_raise_exception(msg="参数错误！", **kwargs):
    return response_400(msg=msg, raise_exception=True, **kwargs)


def response_404_raise_exception(msg="NOT FOUND！", **kwargs):
    return response_404(msg=msg, raise_exception=True, **kwargs)


def response_500_raise_exception(msg="服务器内部错误！", **kwargs):
    return response_500(msg=msg, raise_exception=True, **kwargs)


class BreakFuncExceptin(Exception):
    """ 用于视图层级过深 并有错误或异常时，直接引发异常跳到中间件 处理返回响应"""
    def __init__(self, data):
        self.data = data

    def __str__(self):

        try:
            return self.data["msg"]
        except:
            pass


if __name__ == '__main__':
    response_400(rasie_flag=True)

