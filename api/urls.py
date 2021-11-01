from django.conf.urls import url
# from .view_basic import *
from api.view_api import *
from api.view_project_and_group import *
from api.view_case import *
from api.view_send_req import *
from api.view_test_report import *
from api.view_other_fun import *
from api.view_global_env import *
from api.view_test_task import *
from api.view_report_receive_config import *
from api.reprot_form import get_report_form_list, rf_verify, get_rf_result_list, get_rf_result_detail


urlpatterns = [
    # 自测用的接口
    url(r"^test", test),

    # 项目部分
    url(r'^get_all_project$', get_all_project),  # 取所有项目数据
    url(r"^add_project$", add_project),
    url(r"^delete_project$", delete_project),
    url(r"^update_project$", update_project),

    # 分组部分
    url(r'^get_all_group$', get_all_group),   # 获取某项目下所有分组数据
    url(r"^add_group$", add_group),
    url(r"^delete_group$", delete_group),
    url(r"^update_group$", update_group),

    # 接口部分部分
    url(r'^get_api_list$', get_api_list),
    url(r"^add_api$", add_api),
    url(r"^delete_api$", delete_api),
    url(r"^update_api$", update_api),

    # 用例部分
    url(r"^get_case_data$", get_case_data),   # 获取某个case的数据
    url(r"^get_case_list$", get_case_list),   # 获取某个接口下的所有用例
    url(r"^save_case$", save_case),
    url(r"^delete_case$", delete_case),
    url(r"^update_case$", update_case),

    # 全局配置
    url(r'^get_global_host$', get_global_host),
    url(r'^get_global_variable$', get_global_variable),
    url(r'^get_global_header$', get_global_header),
    url(r'^get_global_cookie$', get_global_cookie),
    url(r'^get_global_env$', get_global_env),

    # 接收报告配置
    url(r'^get_workwx_user_group', get_workwx_user_group),
    url(r'^get_workwx_group_chat', get_workwx_group_chat),
    url(r'^get_email_user_group', get_email_user_group),

    # 页面接口请求
    url(r'^send_req$', send_req),

    # 其他功能部分
    url(r"^switch_json$", switch_json),     # kv格式转换成json格式
    url(r"^switch_kv$", switch_kv),     # json格式转换成kv格式
    url(r"^F12_p_to_json$", F12_p_to_json),     # F12的请求参数转换json
    url(r"^excel_json_auto_switch$", excel_json_auto_switch),   # excel格式和json格式智能转换
    url(r"^add_sign", add_sign),        # 添加当前时间戳

    # 测试任务
    url(r"^get_test_task_list$", get_test_task_list),
    url(r"^get_test_task_detail", get_test_task_detail),
    url(r"^add_test_task$", add_test_task),
    url(r"^update_test_task$", update_test_task),
    url(r"^delete_test_task$", delete_test_task),
    url(r"^execute_task_now$", execute_task_now),
    # url(r"^start_cron_program$", start_cron_program),
    # url(r"^pause_cron_program$", pause_cron_program),
    # url(r"^resume_cron_program$", resume_cron_program),
    # url(r"^stop_cron_program$", stop_cron_program),
    url(r"^start_cron_task$", start_cron_task),     # 开始定时任务
    url(r"^stop_cron_task$", stop_cron_task),       # 停止定时任务
    url(r"^get_cron_info$", get_cron_info),     # 获取指定任务或所有任务的下次执行时间

    # 测试任务组
    url(r"^get_task_group_list$", get_task_group_list),
    url(r"^get_task_group_detail", get_task_group_detail),
    url(r"^add_task_group$", add_task_group),
    url(r"^update_task_group$", update_task_group),
    url(r"^delete_task_group$", delete_task_group),
    url(r"^execute_task_group_now$", execute_task_group_now),
    url(r"^start_cron_task_group$", start_cron_task_group),
    url(r"^stop_cron_task_group$", stop_cron_task_group),

    # 测试报告
    url(r"^get_report_list$", get_report_list),
    url(r"^get_report_data$", get_report_data),
    url(r"^get_case_detail$", get_case_detail),     # 获取用例详情数据，全量测试情况下
    url(r"^get_all_report$", get_all_report),       # 获取全部报告数据

    # 统计部分
    url(r"^staticitem_project$", staticitem_project),   # 按项目统计
    url(r"^staticitem_task$", staticitem_task),         # 按任务统计
    url(r"^staticitem_recent$", staticitem_recent),     # 按最近执行情况统计
    url(r"^staticitem_user$", staticitem_user),         # 按用户统计（最近七周每人新增用例数量
    url(r"^staticitem_user2$", staticitem_user2),       # 按用户统计（每个人新增的全部用例数量

    # 报表自动化
    url(r"^get_report_form_list$", get_report_form_list),
    url(r"^get_rf_result_list$", get_rf_result_list),
    url(r"^get_rf_result_detail$", get_rf_result_detail),
    url(r"^rf_verify$", rf_verify),  # 测试单个报表

    url(r"^upload_case$", upload_case),     # 上传用例
    # 下载接口用例数据 dl_api_case_data:数据处理判断，结果为true通过触发a标签直接请求文件
    url(r"^dl_api$", dl_api),
    url(r"^download_group$", download_group),

    url(r"^download/(.*)", download),   # 下载文件
]
