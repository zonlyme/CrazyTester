from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers import SchedulerNotRunningError, SchedulerAlreadyRunningError
from api.view_basic import *
from api.view_send_req import execute_task
from api.extensions.workwx import send_workwx_user_group

scheduler = BackgroundScheduler()  # 非阻塞


@require_http_methods(["GET"])
@login_required
def start_cron_program(req):
    return _start_cron_program()


def _start_cron_program():
    # global scheduler

    # if scheduler:
    #     return response_400("定时任务程序已经启动!")
    #
    # scheduler = BackgroundScheduler()  # 非阻塞
    # scheduler.start()
    try:
        scheduler.start()
        print("定时任务程序启动成功!")
    except SchedulerAlreadyRunningError as e:
        return response_400("定时任务程序已经启动!")
    except Exception as e:
        return response_400("启动程序失败！{}".format(e))

    tasks = TestTask.m.filter(cron_status="1")
    for task in list(tasks):
        cron = task.cron
        if cron:  # 如果有cron表达式
            cron_item = cron_handel(cron)
            if cron_item:  # cron_item 表示处理有误
                try:
                    # 添加定时任务
                    scheduler.add_job(execute_task, 'cron', args=[None, str(task.id), None, "定时任务"],
                                      id=str(task.id), **cron_item)
                    continue    # 添加不成功就 不把状态更改为未启用
                except Exception as e:
                    TestTask.m.filter(id=task.id).update(**{"cron_status": "2"})
                    print("测试任务启动任务失败！{}".format(e))

    task_groups = TestTaskGroup.m.filter(cron_status="1")
    for task_group in list(task_groups):
        cron = task_group.cron
        if cron:  # 如果有cron表达式
            cron_item = cron_handel(cron)
            if cron_item:  # cron_item 表示处理有误
                try:
                    # 添加定时任务
                    scheduler.add_job(execute_task_group, 'cron', args=[str(task_group.id), None, "定时任务"],
                                      id="task_group_{}".format(task_group.id), **cron_item)
                    continue    # 添加不成功就 不把状态更改为未启用
                except Exception as e:
                    TestTaskGroup.m.filter(id=task_group.id).update(**{"cron_status": "2"})
                    print("测试任务组启动任务失败！{}".format(e))
                    # return response_400("启动任务失败！{}".format(e))

    return response_200()


@require_http_methods(["GET"])
@login_required
def pause_cron_program(req):
    # global scheduler

    if not scheduler:
        return response_400("定时任务程序未启动!")

    try:
        scheduler.pause()
    except Exception as e:
        return response_400("定时程序暂停失败!{}".format(e))

    return response_200()


@require_http_methods(["GET"])
@login_required
def resume_cron_program(req):
    # global scheduler

    if not scheduler:
        return response_400("定时任务程序未启动!")

    try:
        scheduler.resume()
    except Exception as e:
        return response_400("定时程序恢复失败！{}".format(e))

    return response_200()


@require_http_methods(["GET"])
@login_required
def stop_cron_program(req):
    # global scheduler

    if not scheduler:
        return response_400("定时任务程序未启动!")

    try:
        # scheduler.pause()
        # scheduler.resume()
        scheduler.shutdown()
    except SchedulerNotRunningError as e:
        return response_400("定时任务程序未启动!")
    except Exception as e:
        return response_400("停止失败！{}".format(e))

    return response_200()


def task_cron_verify(req):

    task_id = req.GET.get("task_id", "")

    if not task_id:
        response_400_raise_exception("缺少测试任务id！")

    # if not scheduler:
    #     response_400_raise_exception("定时任务程序未启动！")

    try:
        task = TestTask.m.get(id=task_id)
        return task
    except:
        response_400_raise_exception("不存在的测试任务：{}".format(task_id))


@require_http_methods(["GET"])
@login_required
def start_cron_task(req):

    task = task_cron_verify(req)

    # 1. 校验是否已经启动
    if task.cron_status == "1":
        return response_400("定时任务已经启动!")

    if task.cron:    # 如果有cron表达式
        cron_item = cron_handel(task.cron)
        if cron_item:    # 如果处理完的corn表达式 不为空
            try:
                # 2. 添加定时任务
                scheduler.add_job(execute_task, 'cron', id=str(task.id),
                                  args=[None, str(task.id), None, "定时任务"], **cron_item)
            except Exception as e:
                return response_400("启动时报错：{}".format(e))
            else:
                # 3. 更改定时任务状态
                TestTask.m.filter(id=task.id).update(**{"cron_status": "1"})

        else:
            return response_400("cron表达式有误，请检查！")
    else:
        return response_400("cron表达式为空，不可启动！")

    return response_200()


@require_http_methods(["GET"])
@login_required
def stop_cron_task(req):

    task = task_cron_verify(req)

    # 0. 校验是否已经停止
    if task.cron_status == "2":
        return response_400("定时任务已经停止！")

    # 1. 停止定时任务
    try:
        scheduler.remove_job(str(task.id))
    except Exception as e:
        return response_400("停止失败：{}".format(e))

    # 2. 更改定时任务状态
    try:
        TestTask.m.filter(id=task.id).update(**{"cron_status": "2"})
    except Exception as e:
        return response_400("更新失败：{}".format(e))

    return response_200()


@require_http_methods(["GET"])
@login_required
def get_cron_info(req):

    jobs = scheduler.get_jobs()
    job_list = []
    for job in jobs:
        job_list.append({"id": job.id, "n": job.next_run_time.strftime('%Y-%m-%d %H:%M:%S')})
    return response_200(job_list=job_list)

    if not scheduler:
        return response_400("定时任务程序未启动！")

    task_id = req.GET.get("task_id", "")

    if not task_id:
        return response_400("缺少参数: task_id！")

    next_run_time = ""
    job = scheduler.get_job(task_id)
    if job:
        next_run_time = job.next_run_time.strftime('%Y-%m-%d %H:%M:%S')

    return response_200(next_run_time=next_run_time)


@require_http_methods(["GET"])
@login_required
def get_test_task_list(req):
    project_id = req.GET.get("project_id", "")
    filter_item = {}
    if project_id:
        filter_item["project_id"] = project_id

    try:
        info = TestTask.m.filter(**filter_item).order_by("-c_date")    # "cron_status",

    except Exception as e:
        return response_400("错误信息:{}".format(e))

    else:
        list1 = []
        list2 = []
        ret = page_handel(req, info, False)
        for i in ret["data"]:
            item = test_task_handle(i)

            if item["isValid"]:
                list1.append(item)
            else:
                list2.append(item)
        ret["data"] = list2 + list1

        return response_200(**ret)


def test_task_handle(model_item):
    item = model_to_dict_custom(model_item)
    try:
        job = scheduler.get_job(str(model_item.id))  # 获取定时任务列表
        item["next_run_time"] = job.next_run_time.strftime('%Y-%m-%d %H:%M:%S')
    except Exception as e:
        item["next_run_time"] = ""

    # 验证全局环境标签
    global_env_id_list = str_to_list(model_item.global_env_id_list)
    item["global_env"] = []
    for global_env_id in global_env_id_list:
        try:
            item["global_env"].append({
                "id": global_env_id,
                "title": GlobalEnv.m.get(id=global_env_id).title}
            )
        except:
            item["msg"] = "不存在的全局环境标签id：{}".format(global_env_id)
            item["isValid"] = False
            break

    # 验证 分组、接口、用例id
    else:
        if model_item.test_type == "场景测试":
            case_ids_handle(item)
        else:
            api_ids_handle(item)

    return item


@require_http_methods(["GET"])
@login_required
def get_test_task_detail(req):

    task_id = req.GET.get("task_id", "")
    # 验证并获取 task模型对象
    task = test_task_verify_id(task_id)
    # 获取task详情并处理
    data = test_task_handle(task)

    return response_200(data=data)


@require_http_methods(["POST"])
@login_required
def add_test_task(req):

    item = test_task_verify(req)
    if item["msg"]:
        return response_400(item["msg"])
    get_user_info_for_session(req, item, create=True)
    try:
        TestTask.m.create(**item)
    except Exception as e:
        return response_400("创建时出错:{}".format(e))
    return response_200()


@require_http_methods(["POST"])
@login_required
def update_test_task(req):

    task_id = req.POST.get("task_id", "")
    task = test_task_verify_id(task_id)
    item = test_task_verify(req)

    if item["msg"]:
        return response_400(item["msg"])

    get_user_info_for_session(req, item)

    try:
        TestTask.m.filter(id=task.id).update(**item)
    except Exception as e:
        return response_400("更新时出错:{}".format(e))

    try:
        # 如果 有定时表达式，定时任务为启动状态 则更新定时任务
        # 如果 定时表达式为空，定时任务为启动状态 则删除此定时任务
        # 其他情况不用处理
        if item["cron"]:
            cron_item = cron_handel(item["cron"])
            if cron_item and task.cron_status == "1":
                job = scheduler.get_job("{}".format(task.id))
                if job:
                    scheduler.reschedule_job("{}".format(task.id), trigger='cron', **cron_item)
            elif not cron_item:
                return response_400("cron表达式有误，请检查！")
        elif not item["cron"] and task.cron_status == "1":
            TestTask.m.filter(id=task.id).update(**{"cron_status": "2"})
            scheduler.remove_job("{}".format(task.id))
    except Exception as e:
        return response_400("修改定时任务出错:{}".format(e))

    return response_200()


@require_http_methods(["POST"])
@login_required
def delete_test_task(req):

    task_id = req.POST.get("task_id", "")
    task_id = test_task_verify_id(task_id).id
    try:
        job = scheduler.get_job(str(task_id))
        if job:
            return response_400("请先停止定时任务!")
    except Exception as e:
        return response_400("删除出错!{}".format(e))

    try:
        item = {"isDelete": True}
        get_user_info_for_session(req, item)
        TestTask.m.filter(id=task_id).update(**item)
    except Exception as e:
        return response_400("错误：{}".format(e))

    return response_200()


def test_task_verify_id(task_id):
    """
        只验证测试任务id
    """
    if not task_id:
        response_400_raise_exception("未选择任务!")
    try:
        task = TestTask.m.get(id=task_id)
    except Exception as e:
        response_400_raise_exception("没有此测试任务:{}".format(e))

    return task


def test_task_verify(req):

    p = req.POST

    item = {
        "title": p.get("title", ""),
        "task_desc": p.get("task_desc", ""),
        "test_type": p.get("test_type", ""),

        "project_id": p.get("project_id", ""),
        "project_title": p.get("project_title", ""),

        # "global_host_id": p.get("global_host_id", ""),
        # "global_host_title": p.get("global_host_title", ""),
        # "global_variable_id": p.get("global_variable_id", ""),
        # "global_variable_title": p.get("global_variable_title", ""),
        # "global_header_id": p.get("global_header_id", ""),
        # "global_header_title": p.get("global_header_title", ""),
        # "global_cookie_id": p.get("global_cookie_id", ""),
        # "global_cookie_title": p.get("global_cookie_title", ""),

        "global_env_id_list": p.get("global_env_id_list", ""),

        "group_ids": p.get("group_ids", ""),
        "group_title_list": "",
        "api_ids": p.get("api_ids", ""),
        "api_title_list": "",
        "case_ids": p.get("case_ids", ""),
        "case_title_list": "",

        "workwx_user_group_id": p.get("workwx_user_group_id", None) or None,
        "workwx_user_group_title": p.get("workwx_user_group_title", ""),
        "workwx_group_chat_id": p.get("workwx_group_chat_id", None) or None,
        "workwx_group_chat_title": p.get("workwx_group_chat_title", ""),
        "email_user_group_id": p.get("email_user_group_id", None) or None,
        "email_user_group_title": p.get("email_user_group_title", ""),

        "cron": p.get("cron", ""),
        "next_execute_time": "",
        # "cron_status": "2",  # 1启用，2停止
        "msg": "",
        "isValid": True,
    }

    must_field = ["title", "test_type", "project_id", "global_env_id_list",
                  # "global_host_id", "global_variable_id", "global_header_id", "global_cookie_id",
                  # "workwx_user_group_id", "workwx_group_chat_id", "email_user_group_id"
                  ]
    for field in must_field:
        if not item[field]:
            response_400_raise_exception("缺少参数：{}！".format(field))
    if item["cron"]:
        c = len(item["cron"].strip().split(" "))

        if c != 6 and c != 7:
            response_400_raise_exception("cron表达式 长度不正确！应为6或7,当前{}".format(c))

        cron_item = cron_handel(item["cron"])
        if not cron_item:
            response_400_raise_exception("cron表达式 有误，请检查！")
    test_task_verify2(item)
    return item


def test_task_verify2(item):

    if item["test_type"] == "全量测试" or item["test_type"] == "冒烟测试":

        item["case_ids"] = ""  # 不需要此值，手动置空
        # api_id_list = api_ids_handle(item)
        api_ids_handle(item)

    elif item["test_type"] == "场景测试":

        item["group_ids"] = ""  # 不需要此值，手动置空
        item["api_ids"] = ""  # 不需要此值，手动置空
        # case_title_list = case_ids_handle(item)
        case_ids_handle(item)


class TaskGroup:
    def __init__(self, req=None):
        self.req = req
        p = req.POST
        self.item = {
            "title": p.get("title", ""),
            "desc": p.get("desc", ""),
            "project_id": p.get("project_id", ""),
            "project_title": p.get("project_title", ""),
            "test_task_id_list": p.get("test_task_id_list", ""),
            "cron": p.get("cron", ""),
        }

    @staticmethod
    def verify_id(req, method="POST"):
        if method == "POST":
            task_group_id = req.POST.get("task_group_id", "")
        else:
            task_group_id = req.GET.get("task_group_id", "")

        if not task_group_id:
            response_400_raise_exception("未选择任务组!")
        try:
            task_group = TestTaskGroup.m.get(id=task_group_id)
        except Exception as e:
            return response_400_raise_exception("没有此测试任务:{}".format(e))

        return task_group


    @staticmethod
    def verify_content(task_id_list, item=None):

        content = []
        erro_msg = ""
        isValid = True
        task_id_list = str_to_list(task_id_list)

        if not task_id_list:
            erro_msg = "没有测试任务id！"
            isValid = False
        else:
            for task_id in task_id_list:
                try:
                    task = TestTask.m.get(id=task_id)
                    content.append({
                        "id": task.id,
                        "title": task.title,
                        # "project_id": task.project_id,
                        # "project_title": ApiProject.m.get(id=task.project_id).title,
                        "global_env_id_list": task.global_env_id_list
                    })
                except:
                    erro_msg = "不存在的测试任务id:{}".format(task_id)
                    isValid = False
                    content = []
                    break

        if item is not None:
            item["isValid"] = isValid
            item["erro_msg"] = erro_msg
            item["content"] = content

        return isValid, erro_msg, content

    def verify_default_params(self):
        item = self.item

        must_field = ["title", "test_task_id_list", "project_id"]
        for field in must_field:
            if not item[field]:
                response_400_raise_exception("缺少参数：{}！".format(field))

        cron_erro, cron_item = cron_verify(item["cron"])
        if cron_erro:
            response_400_raise_exception(cron_erro)

        self.verify_content(item["test_task_id_list"], item)
        if not item["isValid"]:
            response_400_raise_exception(item["erro_msg"])
        return item


@require_http_methods(["GET"])
@login_required
def get_task_group_list(req):

    project_id = req.GET.get("project_id", "")
    filter_item = {}
    if project_id:
        filter_item["project_id"] = project_id

    list1 = []
    list2 = []

    try:
        info = TestTaskGroup.m.filter(**filter_item).order_by("-c_date")

    except Exception as e:
        return response_400("获取测试任务组出错：{}".format(e))

    else:
        for i in info[:50]:
            item = model_to_dict_custom(i)
            try:
                job = scheduler.get_job("task_group_{}".format(i.id))  # 获取定时任务列表
                item["next_run_time"] = job.next_run_time.strftime('%Y-%m-%d %H:%M:%S')
            except Exception as e:
                item["next_run_time"] = ""
            TaskGroup.verify_content(item["test_task_id_list"], item)

            if item["isValid"]:
                list1.append(item)
            else:
                list2.append(item)

    return response_200(data=list2 + list1)


@require_http_methods(["GET"])
@login_required
def get_task_group_detail(req):
    task_group_id = req.GET.get("task_group_id", "")

    if not task_group_id:
        return response_400("缺少参数：task_group_id")

    task_group_model = TestTaskGroup.m.get(id=task_group_id)
    data = model_to_dict_custom(task_group_model)

    return response_200(data=data)


@require_http_methods(["POST"])
@login_required
def add_task_group(req):
    test_group = TaskGroup(req)
    item = test_group.verify_default_params()
    try:
        get_user_info_for_session(req, item, create=True)
        TestTaskGroup.m.create(**item)
    except Exception as e:
        return response_400("创建时出错:{}".format(e))

    return response_200()


@require_http_methods(["POST"])
@login_required
def update_task_group(req):

    task_group_ = TaskGroup(req)
    task_group = TaskGroup.verify_id(req)
    item = task_group_.verify_default_params()

    try:
        get_user_info_for_session(req, item)
        TestTaskGroup.m.filter(id=task_group.id).update(**item)
    except Exception as e:
        return response_400("更新时出错:{}".format(e))

    try:
        # 如果 有定时表达式，定时任务为启动状态 则更新定时任务
        # 如果 定时表达式为空，定时任务为启动状态 则删除此定时任务
        # 其他情况不用处理
        if item["cron"]:
            cron_item = cron_handel(item["cron"])
            if cron_item and task_group.cron_status == "1":
                job = scheduler.get_job("task_group_{}".format(task_group.id))
                if job:
                    scheduler.reschedule_job("task_group_{}".format(task_group.id), trigger='cron', **cron_item)
            elif not cron_item:
                return response_400("cron表达式有误，请检查！")
        elif not item["cron"] and task_group.cron_status == "1":
            scheduler.remove_job("task_group_{}".format(task_group.id))
            TestTaskGroup.m.filter(id=task_group.id).update(**{"cron_status": "2"})

    except Exception as e:
        return response_400("修改定时任务出错:{}".format(e))

    return response_200()


@require_http_methods(["POST"])
@login_required
def delete_task_group(req):

    task_group = TaskGroup.verify_id(req)
    try:
        job = scheduler.get_job("task_group_{}".format(task_group.id))
        if job or task_group.cron_status == "1":
            return response_400("请先停止定时任务!")
    except Exception as e:
        return response_400("删除出错!{}".format(e))

    try:
        item = {"isDelete": True}
        get_user_info_for_session(req, item)
        TestTaskGroup.m.filter(id=task_group.id).update(**item)
    except Exception as e:
        return response_400("错误：".format(e))

    return response_200()


@require_http_methods(["GET"])
@login_required
def execute_task_group_now(req):
    task_group_id = req.GET.get("task_group_id", "")
    if not task_group_id:
        return response_400("未选择测试任务组id")
    execute_task_group(task_group_id, req, "手动测试")   # 定时任务

    return response_200()


def execute_task_group(task_group_id, req, trigger_way):

    try:
        task_group = TestTaskGroup.m.get(id=task_group_id)
    except:
        erro_msg = "{}:不存在的测试组id：{}！！！".format(trigger_way, task_group_id)
        send_workwx_user_group(erro_msg)
        response_400_raise_exception(erro_msg)
    else:
        isValid, erro_msg, content = TaskGroup.verify_content(task_group.test_task_id_list)
        if not isValid:
            response_400_raise_exception(erro_msg)

        for c in content:
            for global_env_id in str_to_list(c["global_env_id_list"] or ""):
                execute_task(req, c["id"], global_env_id, trigger_way=trigger_way, task_group_id=task_group_id)


@require_http_methods(["GET"])
@login_required
def start_cron_task_group(req):
    task_group = TaskGroup.verify_id(req, method="GET")

    if not task_group.cron:
        return response_400("cron表达式为空，不可启动！!")

    # 1. 校验是否已经启动
    if task_group.cron_status == "1":
        return response_400("定时任务已经启动!")

    cron_erro, cron_item = cron_verify(task_group.cron)
    if cron_erro:
        return response_400(cron_erro)

    if cron_item:  # 如果处理完的corn表达式 不为空
        try:
            # 2. 添加定时任务
            scheduler.add_job(execute_task_group, 'cron', id="task_group_{}".format(task_group.id),
                              args=[task_group.id, None, "定时任务"], **cron_item)
        except Exception as e:
            return response_400("启动时报错：{}".format(e))
        else:
            # 3. 更改定时任务状态
            TestTaskGroup.m.filter(id=task_group.id).update(**{"cron_status": "1"})

    return response_200()


@require_http_methods(["GET"])
@login_required
def stop_cron_task_group(req):
    task_group = TaskGroup.verify_id(req, method="GET")

    # 0. 校验是否已经停止
    if task_group.cron_status == "2":
        return response_400("定时任务已经停止！")

    # 1. 停止定时任务
    try:
        scheduler.remove_job("task_group_{}".format(task_group.id))
    except Exception as e:
        return response_400("停止失败：{}".format(e))

    # 2. 更改定时任务状态
    try:
        TestTaskGroup.m.filter(id=task_group.id).update(**{"cron_status": "2"})
    except Exception as e:
        return response_400("更新失败：{}".format(e))

    return response_200()


def cron_verify(cron):
    erro_msg = ""
    cron_item = {}
    if cron:
        c = len(cron.strip().split(" "))
        if c not in [6, 7]:
            erro_msg = "cron表达式 长度不正确！应为6或7,当前{}".format(c)

        else:
            cron_item = cron_handel(cron)
            if not cron_item:
                erro_msg = "cron表达式 有误，请检查！"

    return erro_msg, cron_item


def cron_handel(cron):
    """

    :param cron:
    :return: 有错误会返回空
    """

    cron_item = {}

    try:
        c = cron.strip().split(" ")
        cron_item["second"] = c[0]
        cron_item["minute"] = c[1]
        cron_item["hour"] = c[2]
        if c[3] == "?":
            c[3] = "*"
        cron_item["day"] = c[3]
        cron_item["month"] = c[4]
        if c[5] == "?":
            c[5] = "*"
        cron_item["day_of_week"] = c[5]

        try:
            cron_item["year"] = c[6]

        except:
            pass

    except:
        pass

    return cron_item


if settings.CRON_TASK_START:
    _start_cron_program()


if __name__ == '__main__':
    pass
    # scheduler = BackgroundScheduler()  # 非阻塞
    # scheduler.start()                 # 立即启动程序
    # scheduler.shutdown(wait=False)    # 等待所有任务完成后停止程序 wait:立即停止所有任务
    # cron_item = corn_handel("* * 17 * * ?")
    # scheduler = scheduler.add_job(func, 'cron', id='my_job_id1', **cron_item)
    # scheduler.add_job(job_function, CronTrigger.from_crontab('0 0 1-15 may-aug *'))
    # scheduler.remove_job('my_job_id1')  # 删除任务方法
    # scheduler.pause_job("my_job_id1")   # 暂停任务方法
    # scheduler.resume_job("my_job_id1")  # 恢复任务方法
    # scheduler.reschedule_job('my_job_id', trigger='cron', minute='*/5')   # 修改任务

    # ls = scheduler.get_jobs()         # 获取定时任务列表
    # for i in ls:
    #     print(i.id, i.next_run_time)  #  获取


"""
表达式
参数类型
描述




*
所有
通配符。例：minutes=*即每分钟触发


*/a
所有
可被a整除的通配符。


a-b
所有
范围a-b触发


a-b/c
所有
范围a-b，且可被c整除时触发


xth y
日
第几个星期几触发。x为第几个，y为星期几


last x
日
一个月中，最后个星期几触发


last
日
一个月最后一天触发


x,y,z
所有
组合表达式，可以组合确定值或上方的表达式

作者：Nuance__
链接：https://www.jianshu.com/p/4f5305e220f0/
来源：简书
简书著作权归作者所有，任何形式的转载都请联系作者获得授权并注明出处。
"""










