from django.utils.deprecation import MiddlewareMixin
# from api.extensions.custom_json_response import JsonResponse
from django.http.response import JsonResponse
from api.extensions.custom_response import *


class MD(MiddlewareMixin):

    # def process_request(self, request):
    #     """
    #     request.POST 取出的是表单格式数据：'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8'
    #     request.body 取出的是json格式数据: Content-Type : application/json ， 通过eval(request.body) 可转为 dict
    #     drf 中 request.data, 取出的就是json格式数据，为字典类型
    #     """
    #     ct = request.META.get("CONTENT_TYPE", "")   # 这里都大写了
    #
    #     if ct == "application/json" and request.body:
    #         try:
    #             request.dict_body = eval(request.body)
    #         except Exception as e:
    #             print(str(e))
    #             pass

    def process_exception(self, request, exception):

        # 处理主动抛出的异常（一般用于错误参数类
        if isinstance(exception, BreakFuncExceptin):
            return json_response(**exception.data)

        return response_500(msg="md：{}".format(str(exception)))


if __name__ == '__main__':
    response_400(msg="参数错误")