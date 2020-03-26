from django.conf.urls import url
# from .view_basic import *
from .view_api import *
from .view_node import *
from .view_case import *
from .view_send_req import *
from .view_test_report import *
from .view_other_fun import *
from .func_business_license_recognit import *


urlpatterns = [

    # 自测用的接口
    url(r"^test_self", test_self),

    # 登陆验证
    url(r"^login_verify$", login_verify),

    # 注销
    url(r"^logout$", logout),

    # 主页
    url(r'^$|^interface$', interface),

    # 获取环境信息
    url(r'^get_env$', get_env),

    # 发送测试接口的请求
    url(r'^send_req$', send_req),

    # 获取nav全部数据
    url(r'^get_nav$', get_nav),

    # 取所有节点(首层)
    url(r'^get_all_node$', get_all_node),

    # 获取API的数据
    url(r"^get_api_data/(\d+)$", get_api_data),

    # 获取case的数据
    url(r"^get_case_data/(\d+)$", get_case_data),

    # 删除API
    url(r"^deleteAPI/(\d+)$", deleteAPI),
    # 保存API
    url(r"^saveAPI/(\d+)$", saveAPI),
    # 更新API
    url(r"^updateAPI$", updateAPI),

    # kv格式转换成json格式
    url(r"^switch_json$", switch_json),
    # json格式转换成kv格式
    url(r"^switch_kv$", switch_kv),
    # F12的请求参数转换json
    url(r"^F12_p_to_json$", F12_p_to_json),
    # 节点的增删改查
    url(r"^nodeOperate", nodeOperate),

    # 添加当前时间戳
    url(r"^add_sign", add_sign),

    # 保存case
    url(r"^save_case$", save_case),
    # 删除case
    url(r"^delete_case$", delete_case),
    # 更新case
    url(r"^update_case$", update_case),


    # 通过接口调用，测试接口，返回报告信息
    url(r"^batch_test$", batch_test),
    # url(r"^test/(\d+)/node=(.*)", test_node),

    # 测试报告页面
    url(r"^report/\d+$", report),
    url(r"^report/(\d+)_data$", get_report_data),
    url(r"^report/get_case_detail$", get_case_detail),
    # 获取全部报告数据
    url(r"^report/get_all_report$", get_all_report),

    # 测试报告页面 第二种格式
    url(r"^report2/\d+$", report2),
    url(r"^report2/(\d+)_data$", get_report_data),
    url(r"^report/get_report_detail$", get_report_detail),
    url(r"^report2/get_all_report$", get_all_report),

    # 上传用例
    url(r"^upload_case$", upload_case),

    # 批量识别全国二维码
    url(r"^license_recognit$", license_recognit),

    # 下载接口用例数据 dl_api_case_data:数据处理判断，结果为ｔｒｕｅ通过触发ａ标签直接请求文件
    url(r"^dl_api_case_data$", dl_api_case_data),

    # 下载文件
    url(r"^download/(.*)", download),
]