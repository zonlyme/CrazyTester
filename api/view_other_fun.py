# import os
import xlrd
from api.extensions.excel_handle import WriteTable
from api.view_basic import *
import re


@require_http_methods(["POST"])
@login_required
# excel用例导入数据库主函数
def upload_case(req):

    obj = req.FILES.get('case_file')
    if not obj:
        return response_400("没有选择文件")

    # 组合文件目录
    file_path = os.path.join(settings.MEDIA_ROOT_VIRTUAL, "case_file", "upload")
    if not os.path.exists(file_path):
        os.makedirs(file_path)      # 没有目录先创建目录
    file_path = os.path.join(file_path, obj.name)

    ret = os.path.isfile(file_path)
    if ret:
        temp = file_path.rsplit(".", 1)
        file_path = "{}{}.{}".format(temp[0], time.time(), temp[1])

    # 读取文件
    f = open(file_path, 'wb')
    for line in obj.chunks():
        f.write(line)
    f.close()

    # 处理文件
    res_data = excel_handle(req, file_path)

    return response_200(**res_data)


# excel数据格式检测
def excel_handle(req, file_path):

    try:
        rbook = xlrd.open_workbook(file_path)
    except xlrd.biffh.XLRDError:
        return response_400_raise_exception("不支持的格式")
    except Exception as e:
        return response_400_raise_exception("xlrd打开文件异常".format(e))

    table = rbook.sheets()[0]  # 表示获取第一个表格

    nrows = table.nrows  # 有效行数

    # 全部行：项目名  目录名	接口名	接口描述	请求方式	请求地址
    #       用例状态    用例名字	用例描述	headers	入参	请求体 断言信息    前置操作    响应设置全局变量
    # 不可为空的字段
    not_none = ["项目名", "目录名", "接口名", "请求方式", "用例状态", "用例名字", "请求地址"]
    # 必须为json格式的字段
    is_json = ['get请求参数', 'post请求体', '样例数据',
               "headers", "cookies", "断言信息", "前置操作", "响应设置全局变量", "响应设置全局请求头"]
    # 可以为空的字段
    allow_is_none = ["接口描述", "用例描述", "get请求参数", "post请求体", "样例数据",
                     "headers", "cookies", "断言信息", "前置操作", "响应设置全局变量"]

    # sheet_header = ['目录名字', '接口名字', '接口描述', '请求方式',
    #                 '用例状态', '用例名字', '用例描述', '请求地址',
    #                 'get请求参数', 'post请求体', '样例数据',
    #                 'headers', 'cookies',
    #                 '断言信息', "前置操作", "响应设置全局变量"]  # 表头部信息

    for row in range(17):
        for col in range(1, nrows):
            try:
                field_name = table.cell_value(0, row)
                this = str(table.cell_value(col, row))
                if field_name in not_none:
                    if not str(this).strip():
                        response_400_raise_exception("{}-第{}行不能为空：{}".format(field_name,
                                                       col + 1, format(table.cell_value(col, row))))
                    continue
                elif field_name in is_json:
                    if str(this).strip():
                        try:
                            temp = json.loads(this)
                            if type(temp) == str:
                                response_400_raise_exception(
                                    "{}-第{}行是字符串！应为json格式".format(field_name, col + 1))
                        except:
                            response_400_raise_exception("{}-第{}行不是json格式！".format(field_name, col + 1))

            except Exception as e:
                response_400_raise_exception("异常:{}".format(e))

    else:

        add_case_count = 0
        update_case_count = 0

        for row in range(1, nrows):  # 从第二行开始遍历
            item = dict()
            item["project_title"] = str(table.cell_value(row, 0)).strip()
            item["group_title"] = str(table.cell_value(row, 1)).strip()
            item["api_title"] = str(table.cell_value(row, 2)).strip()
            item["api_desc"] = str(table.cell_value(row, 3)).strip()
            item["method"] = str(table.cell_value(row, 4)).strip()

            try:
                case_id = str(int(table.cell_value(row, 5)))
            except:
                case_id = table.cell_value(row, 5)
            item["case_id"] = case_id

            # case_href = table.cell_value(row, 6)    # 用例链接
            try:
                case_status = str(int(table.cell_value(row, 7)))
            except:
                case_status = table.cell_value(row, 7)

            item["case_status"] = case_status
            item["case_id"] = case_id
            item["case_title"] = str(table.cell_value(row, 8)).strip()
            item["case_desc"] = str(table.cell_value(row, 9)).strip()
            item["url"] = str(table.cell_value(row, 10)).strip()

            item["params"] = str(table.cell_value(row, 11)).strip()
            item["data"] = str(table.cell_value(row, 12)).strip()
            item["sample_data"] = str(table.cell_value(row, 13)).strip()

            item["headers"] = str(table.cell_value(row, 14)).strip()
            item["cookies"] = str(table.cell_value(row, 15)).strip()

            item["asserts"] = str(table.cell_value(row, 16)).strip()
            item["prefix"] = str(table.cell_value(row, 17)).strip()
            item["rsgv"] = str(table.cell_value(row, 18)).strip()
            item["rsgh"] = str(table.cell_value(row, 19)).strip()

            try:
                set_global_cookies = str(int(table.cell_value(row, 20)))
            except:
                set_global_cookies = table.cell_value(row, 20)
            item["set_global_cookies"] = set_global_cookies

            try:
                clear_global_cookies = str(int(table.cell_value(row, 21)))
            except:
                clear_global_cookies = table.cell_value(row, 21)
            item["clear_global_cookies"] = clear_global_cookies

            handle_ret = excel_insert_db_handle(req, item)
            if handle_ret["msg"]:
                response_400_raise_exception(handle_ret["msg"])
            if handle_ret["update_case_flag"]:
                update_case_count += 1
            if handle_ret["add_case_flag"]:
                add_case_count += 1

        r_data = {
            "msg": "导入成功！",
            "update_case_count": update_case_count,
            "add_case_count": add_case_count,
        }

        return r_data


# excel数据入库
def excel_insert_db_handle(req, item):
    msg = ""
    add_case_flag = False
    update_case_flag = False

    user_info = get_user_info_for_session(req, create=False if item["case_id"] else True)
    """
        :param item: excel表中数据组合出来的item
       
        # 如果有用例id并且存在，则直接更新，
        # 如果有用例id但不存在，则报错
        # 如果没有用例id，则创建
            项目不可创建
            分组，接口依次创建
    """
    try:
        case_item = {
            "status": True if item["case_status"] == "1" else False,
            "title": item["case_title"],
            "desc": item["case_desc"],
            "url": item["url"],
            "params": item["params"],
            "data": item["data"],
            "sample_data": item["sample_data"],
            "headers": item["headers"],
            "cookies": item["cookies"],
            "asserts": item["asserts"],
            "prefix": item["prefix"],
            "rsgv": item["rsgv"],
            "rsgh": item["rsgh"],
            "set_global_cookies": True if item["set_global_cookies"] == "1" else False,
            "clear_global_cookies": True if item["clear_global_cookies"] == "1" else False,
        }

        if item["case_id"]:
            try:
                ApiCase.m.get(id=item["case_id"])
            except:
                response_400_raise_exception("不存在的用例id：{}，请检查！".format(item["case_id"]))
            else:
                ApiCase.m.filter(id=item["case_id"]).update(**case_item)
                update_case_flag = True
                return {
                    "msg": msg,
                    "add_case_flag": add_case_flag,
                    "update_case_flag": update_case_flag,
                }

        try:
            project_data = ApiProject.m.get(title=item["project_title"])
            project_id = project_data.id
        except Exception as e:
            response_400_raise_exception("不存在的项目！")
            return
            # project_item = {"title": item["project_title"]}
            # project_item.update(user_info)
            # new_project = ApiProject.m.create(**project_item)
            # project_id = new_project.id

        try:
            group_data = ApiGroup.m.get(title=item["group_title"], project=project_id)
            group_id = group_data.id
        except Exception as e:
            group_item = {"title": item["group_title"], "project_id": project_id}
            group_item.update(user_info)
            new_group = ApiGroup.m.create(**group_item)
            group_id = new_group.id

        try:
            api_data = ApiApi.m.get(title=item["api_title"], group=group_id)
            api_id = api_data.id
        except Exception as e:
            api_item = {
                "title": item["api_title"],
                "desc": item["api_desc"],
                "method": item["method"].capitalize(),
                "group_id": group_id,
            }
            api_item.update(user_info)
            new_api = ApiApi.m.create(**api_item)
            api_id = new_api.id

        case_item["api_id"] = api_id
        ApiCase.m.create(**case_item)
        add_case_flag = True

    except Exception as e:
        msg = "错误:{}".format(e)

    return {
        "msg": msg,
        "add_case_flag": add_case_flag,
        "update_case_flag": update_case_flag,
    }


@require_http_methods(["GET"])
# 接口下所有用例数据导入表
def dl_api(req):
    """
    :param req:
    1. 验证是否有此api
    2. 根据api整理出用例数据
    3. 将数据写入表
    4. 返回此函数验证结果，
        r_data = {
            "ret": False,   成功：ｊｓ再次发起请求，请求文件，失败：ｊｓ前段其实错误信息
            "msg": None,   错误信息
            "file_name": None   文件名字
        }
    :return:
    """
    # 1. 验证是否有此api
    api_id = req.GET.get('api_id', "")
    if not api_id:
        return response_400("缺少参数id！")

    try:
        api_data = ApiApi.m.get(pk=api_id)
    except:
        return response_400("不存在的接口：{}".format(api_id))
    else:
        group_data = ApiGroup.m.get(pk=api_data.group_id)
        project_data = ApiProject.m.get(pk=group_data.project_id)
        items = get_case_down_data(api_data, group_data, project_data)
        file_name = "接口用例_{}.xls".format(api_data.title.replace(":", "-"))

        # 相对目录：CrazyTester/static/upload     /case_file/download/project_title/group_title/api_title
        file_path_relative = os.path.join(
            "case_file", "download", project_data.title, group_data.title, api_data.title, file_name)
        # 文件存放的真实位置： /var/www/CrazyTester/static/upload     /case_file/download/project_title/group_title/api_title
        file_path_real_dir = os.path.join(
            settings.MEDIA_ROOT_VIRTUAL, "case_file", "download", project_data.title, group_data.title, api_data.title)
        if not os.path.exists(file_path_real_dir):
            os.makedirs(file_path_real_dir)
        file_path_real = os.path.join(file_path_real_dir, file_name)

        return write_case_download_data(file_name, items, file_path_relative, file_path_real)


def get_case_down_data(api_data, group_data, project_data):
    items = []

    # 2. 根据api整理出用例数据
    case_datas = ApiCase.m.filter(api_id=api_data.id)

    for case_data in case_datas:
        temp_item = {
            "url": case_data.url,
            "params": case_data.params,
            "data": case_data.data,
            # "sample_data": case_data.sample_data,
            "headers": case_data.headers,
            # "cookies": case_data.cookies,
            # "prefix": case_data.prefix,
            # "rsgv": case_data.rsgv,
            "asserts": case_data.asserts,
        }
        use_global_variable = []
        new_dict1 = {}
        try:
            for k, v in temp_item.items():
                new_dict1[k] = json_dumps(v)  # 所有python格式转换成json字符串

            for i in new_dict1.keys():
                if new_dict1[i]:
                    key = re.compile(r'[{][{](.*?)[}][}]', re.S)
                    value = re.findall(key, new_dict1[i])
                    if value:
                        use_global_variable.extend(value)
        except:
            response_400_raise_exception("匹配出错！")
        use_global_variable = list(set(use_global_variable))

        set_global_variable = []
        rsgvs = json.loads(case_data.rsgv) if case_data.rsgv else []
        for rsgv in rsgvs:
            set_global_variable.append(rsgv["rsgv_name"])

        set_global_headers = []
        rsghs = json.loads(case_data.rsgh) if case_data.rsgh else []
        for rsgh in rsghs:
            set_global_headers.append(rsgh["rsgh_name"])

        item = [
            project_data.title or "",
            group_data.title or "",
            api_data.title or "",
            api_data.desc or "",
            api_data.method or "",

            case_data.id or "",
            case_data.id or "",     # 做用例链接用
            "1" if case_data.status else "0",
            case_data.title or "",
            case_data.desc or "",
            case_data.url or "",

            case_data.params or "",
            case_data.data or "",
            case_data.sample_data or "",

            case_data.headers or "",
            case_data.cookies or "",

            case_data.asserts or "",
            case_data.prefix or "",
            case_data.rsgv or "",
            case_data.rsgh or "",
            "1" if case_data.set_global_cookies else "0",
            "1" if case_data.clear_global_cookies else "0",
            ",".join(use_global_variable) if use_global_variable else "",
            ",".join(set_global_variable) if set_global_variable else "",
            ",".join(set_global_headers) if set_global_headers else "",
        ]
        items.append(item)
    return items


def write_case_download_data(file_name, items: [], file_path_relative, file_path_real):
    # 3. 将数据写入表
    sheet_header = ['项目名', '目录名', '接口名', '接口描述', '请求方式',
                    '用例id', '用例链接', '用例状态', '用例名字', '用例描述', '请求地址',
                    'get请求参数', 'post请求体', '样例数据', 'headers', 'cookies',
                    '断言信息', "前置操作", "响应设置全局变量", "响应设置全局请求头",
                    '响应cookies全部设置到当前全局cookies中', '清空全局cookies',
                    '使用全局变量', '设置全局变量', '设置全局请求头']  # 表头部信息

    sheet_name = "数据"
    wt = WriteTable(file_path_real, sheet_header, items, sheet_name)
    msg = wt.write()

    if msg:
        return response_400(msg)

    else:
        r_data = {
            "file_path": file_path_relative,
            "file_name": file_name
        }

        return response_200(**r_data)


@require_http_methods(["GET"])
@login_required
# 接口下所有用例数据导入表
def download_group(req):
    # 1. 验证是否有此分组
    group_id = req.GET.get('group_id', "")
    if not group_id:
        return response_400("缺少参数 group_id！")

    try:
        group_data = ApiGroup.m.get(pk=group_id)
    except:
        return response_400("不存在的接口：{}".format(group_id))
    else:
        project_data = ApiProject.m.get(pk=group_data.project_id)
        items = []
        for api_data in ApiApi.m.filter(group_id=group_id):
            items += get_case_down_data(api_data, group_data, project_data)
        file_name = "分组用例_{}.xls".format(group_data.title.replace(":", "-"))

        # 相对目录：CrazyTester/static/upload     /case_file/download/project_title/group_title/api_title
        file_path_relative = os.path.join("case_file", "download", project_data.title, group_data.title, file_name)
        # 文件存放的真实位置： /var/www/CrazyTester/static/upload     /case_file/download/project_title/group_title/api_title
        file_path_real_dir = os.path.join(settings.MEDIA_ROOT_VIRTUAL, "case_file", "download", project_data.title,
                                          group_data.title)
        if not os.path.exists(file_path_real_dir):
            os.makedirs(file_path_real_dir)
        file_path_real = os.path.join(file_path_real_dir, file_name)

        return write_case_download_data(file_name, items, file_path_relative, file_path_real)