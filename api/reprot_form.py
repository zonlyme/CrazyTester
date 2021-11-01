import requests
import xlrd
import pymysql
import hashlib
from urllib.parse import urljoin
from .view_basic import *
from api.extensions.workwx import send_workwx_user_group, send_workwx_user_group_, send_workwx_group_chat, send_workwx_group_chat_


@login_required
@require_http_methods(["GET"])
def get_report_form_list(req):
    project_id = req.GET.get("project_id", "")

    filter_item = {}
    if project_id:
        filter_item["project_id"] = project_id

    data_raw = ReportForm.m.filter(**filter_item)
    datas = []
    for data in data_raw:
        d = model_to_dict_custom(data)
        d["sync_type"] = data.get_sync_type_display()
        try:
            d["project_title"] = ApiProject.m.get(id=data.project_id).title
        except:
            d["project_title"] = "不存在的项目！"
        datas.append(d)

    return response_200(datas=datas)


@login_required
@require_http_methods(["GET"])
def get_rf_result_list(req):
    rf_id = req.GET.get("rf_id")

    filter_item = {}
    if rf_id:
        filter_item["report_form_id"] = rf_id

    data_raw = ReportFormResult.m.filter(**filter_item).order_by("-c_date")

    r_data = []
    for data in data_raw:
        d = model_to_dict(data, exclude=["db_data", "form_data", "log", "isDelete", "c_date", "u_date"])
        d["c_date"] = data.c_date.strftime('%Y-%m-%d %H:%M:%S')
        d["u_date"] = data.u_date.strftime('%Y-%m-%d %H:%M:%S')
        r_data.append(d)

    return response_200(datas=r_data)


@login_required
@require_http_methods(["GET"])
def get_rf_result_detail(req):
    rf_result_id = req.GET.get("rf_result_id", "")

    if not rf_result_id:
        return response_400("缺少参数：rf_result_id")

    raw = ReportFormResult.m.get(id=rf_result_id)
    data = model_to_dict_custom(raw)

    return response_200(data=data)


@login_required
@require_http_methods(["GET"])
def rf_verify(req):
    rf_id = req.GET.get("rf_id")

    if not rf_id:
        return response_400("缺少参数：rf_id")
    try:
        rf_raw = ReportForm.m.get(id=rf_id)
    except:
        response_400("不存在的任务id：{}".format(rf_id))
    else:
        rf = ReportFormTest(rf_raw)
        r_data = rf.start()
        # print(r_data["log"])

        if r_data["msg"]:
            return response_400(**r_data)

        return response_200(**r_data)


@login_required
@require_http_methods(["GET"])
def rf_verify_task(req):
    rf_task_id = req.GET.get("rf_task_id")
    if not rf_task_id:
        return response_400("缺少参数：报表任务id rf_task_id")

    result = rf_verify_task_now(rf_task_id, "手动测试")

    return response_200(data=result)


def rf_verify_task_now(rf_task_id, trigger_way):

    report = RFTaskResult()
    report.trigger_way = trigger_way
    report.rf_task_id = rf_task_id

    start_time = time.time()
    success_count = 0
    fail_count = 0

    try:
        rf_task_raw = RFTask.m.get(id=rf_task_id)
    except:
        report.flag = False
        report.errro_msg = "不存在的报表任务id：{}".format(rf_task_id)
        send_error_msg(report, report.errro_msg)
    else:
        report.project_id = rf_task_raw.project_id

        rf_id_list = str_to_list(rf_task_raw.rf_ids)
        for rf_id in rf_id_list:
            try:
                rf_raw = ReportForm.m.get(id=rf_id)
            except:
                report.flag = False
                report.errro_msg = "不存在的报表id：{}".format(rf_id)
                send_error_msg(report, report.errro_msg)
                break
            else:
                rf = ReportFormTest(rf_raw)
                r_data = rf.start()
                if r_data["error_msg"]:
                    fail_count += 1
                else:
                    success_count += 1
        else:
            report.success_count = success_count
            report.fail_count = fail_count
            report.test_ret = True if fail_count == 0 else False
            ret_msg = "通过" if fail_count == 0 else "失败"

            content = "本次测试{}个报表\r\n" \
                      "成功：{}个，\r\n" \
                      "失败：{}个,\r\n" \
                      "最终结果：{}\r\n" \
                      "执行时间:{}\r\n".format(
                len(rf_id_list), success_count, success_count, success_count, ret_msg, get_now_time()
            )
            if not report.test_ret:
                content += report.errro_msg
            send_msg(report, rf_task_raw, content)

    finally:
        end_time = time.time()
        report.execution_time = int((end_time - start_time) * 1000)
        report.save()

    return report.flag, report.errro_msg


def send_msg(report, rf_task_raw, content):
    content += "报表测试报告 - {}\r\n".format(report.title)

    send_workwx_user_group_flag, send_workwx_user_group_msg = send_workwx_user_group_(content,
                                                                                      rf_task_raw.workwx_user_group_id)
    send_workwx_group_chat_flag, send_workwx_group_chat_msg = send_workwx_group_chat_(content,
                                                                                      rf_task_raw.workwx_group_chat_id)
    report.send_workwx_user_group_flag = send_workwx_user_group_flag
    report.send_workwx_user_group_msg = send_workwx_user_group_msg
    report.send_workwx_group_chat_flag = send_workwx_group_chat_flag
    report.send_workwx_group_chat_msg = send_workwx_group_chat_msg


def send_error_msg(report, content):
    content += "报表测试报告 - {}\r\n出错了！".format(get_now_time())

    send_workwx_user_group_flag, send_workwx_user_group_msg = send_workwx_user_group(content)
    report.send_workwx_user_group_flag = send_workwx_user_group_flag
    report.send_workwx_user_group_msg = send_workwx_user_group_msg

# class ReportFormTest:
#     """"发票管理 - 测试环境"""
#
#     default_config = """
#         {
#             "千丁云账号": "13120009968",
#             "千丁云密码": "temp1234",
#             "千丁云验证码": "6666",
#             "数据库地址":"localhost",
#             "数据库用户":"root",
#             "数据库密码":"Qding@2021",
#             "数据库使用库":"api_auto",
#             "数据库端口":"3306"
#         }
#     """
#     title = "表1"
#     env = "测试环境"  # 1 测试环境    2. 生产环境
#
#     sync_type = "1"
#     # 同步
#     execute_export_url = "/qdp2-polaris-p3-server-api/v1/api/venusWorkOrder/standardStatisticsExport"
#     execute_export_method = "POST"
#     execute_export_params = {"current": 1, "size": 10, "communityIds": [], "modules": [1], "templateIdList": [],
#                              "planStartTimeBegin": "", "planStartTimeEnd": "", "planEndTimeBegin": "",
#                              "planEndTimeEnd": ""}
#
#     # export_type = "2"
#     # # 异步
#     # execute_export_url = "qdp2-virgo-server-api/v1/api/taskinfo/exportNoteManageList"
#     # execute_export_method = "POST"
#     # execute_export_params = {"pageNum": 1, "pageSize": 10, "communityCode": "10011", "taxNoteType": "",
#     #                          "noteAuditType": "", "noteAuditStatus": "", "communityName": "亚如的小区"}
#     #
#
#     start_line = "2"
#     sql = 'select * from api_project;'
#     config = default_config


class ReportFormTest:

    def __init__(self, report_form_data, trigger_way="手动测试"):
        # self.rf = ReportForm()
        self.rf = report_form_data
        self.error_msg = ""
        self.log = []
        self.ret = False
        self.trigger_way = trigger_way
        self.report = ReportFormResult()

    def set_log(self, log, print_flag=False):
        self.log.append(log)

    def r_data(self, data=None):
        """ 返回数据并创建报告 """

        if data is None:
            data = {}

        self.report.report_form_id = self.rf.id
        self.report.title = self.rf.title
        self.report.env = self.rf.env
        self.report.sync_type = self.rf.get_sync_type_display()
        self.report.trigger_way = self.trigger_way

        log = ""
        for i in self.log:
            log += str(i) + "\n"

        self.log = log
        self.report.log = log
        self.report.error_msg = self.error_msg
        self.report.test_ret = False if self.error_msg else True

        # send_workwx_user_group_flag, send_workwx_user_group_msg = []
        # send_workwx_group_chat_flag, send_workwx_group_chat_msg = []
        # send_email_flag, send_email_msg = []

        if data:
            db_data = [[str(y) for y in x] for x in data["db_data"]]
            form_data = [[str(y) for y in x] for x in data["form_data"]]
            self.report.db_data = json_dumps_indent4(db_data)
            self.report.form_data = json_dumps_indent4(form_data)
            self.report.file_path = data["file_path"]

        try:
            self.report.save()
        except Exception as e:
            self.error_msg = "创建报告出错：{}".format(e)

        r_data = {
            "msg": self.error_msg,
            "log": log
        }
        r_data.update(**data)

        return r_data

    def start(self):
        self.set_log("\n☆☆☆☆☆ 报表配置转json格式")
        try:
            self.rf.config = json.loads(self.rf.config)
        except Exception as e:
            self.error_msg = "报表配置不是json格式！{}".format(e)
            return self.r_data()

        self.set_log("\n☆☆☆☆☆ 处理环境")
        self.env_handle()
        if self.error_msg:
            return self.r_data()

        # 登录千丁云
        self.set_log("\n☆☆☆☆☆ 登录千丁云")
        auth = self.login()
        if self.error_msg:
            return self.r_data()

        # 组合接口 header
        self.set_log("\n☆☆☆☆☆ 组合接口 header")
        timestamp = int(time.time() * 1000)
        self.headers = {
            "Authorization": auth,
            "timestamp": timestamp,
            "t1": get_t1(timestamp, auth),
            "Content-Type": "application/json",
        }
        self.set_log("{}".format(json_dumps_indent4(self.headers)))
        # self.set_log("\n☆☆☆☆☆ 请求头为：{}".format(json_dumps_indent4(self.headers)))

        # 同步导出
        if self.rf.sync_type == "1":
            self.set_log("\n☆☆☆☆☆ 同步导出接口")
            file_path = self.sync_export()
            if self.error_msg:
                return self.r_data()

        # 异步导出
        else:
            # 异步导出接口
            self.set_log("\n☆☆☆☆☆ 异步导出接口")
            flag = self.execute_exprot_handle()
            if self.error_msg:
                return self.r_data()

            # 查找导出列表
            self.set_log("\n☆☆☆☆☆ 查找导出列表")
            file_Key = self.export_list_handle()
            if self.error_msg:
                return self.r_data()

            # 下载导出文件 "999999999/1634009703719/开票申请-21101200010.xlsx"
            self.set_log("\n☆☆☆☆☆ 下载导出文件")
            time.sleep(3)
            file_path = self.getPresignedUrl(file_Key)
            if self.error_msg:
                return self.r_data()

        self.set_log("表下载地址：" + file_path)

        # 获取表数据 "开票申请-21101200010.xlsx"
        self.set_log("\n☆☆☆☆☆ 获取表数据")
        form_data = self.form_get_data("api_project.xlsx")
        # form_data = self.form_get_data(file_path)
        if self.error_msg:
            return self.r_data()

        # 获取库数据
        self.set_log("\n☆☆☆☆☆ 获取库数据")
        db_data = self.db_get_data()
        if self.error_msg:
            return self.r_data()

        # 表数据与库数据对比
        self.set_log("\n☆☆☆☆☆ 表数据与库数据对比")
        self.form_vs_db(db_data, form_data)

        if self.error_msg:
            self.set_log("\n☆☆☆☆☆ 对比失败！")
            return self.r_data()
        else:
            self.set_log("\n☆☆☆☆☆ 对比成功！")
            return self.r_data({
                "db_data": db_data,
                "form_data": form_data,
                "file_path": file_path,
            })

    def env_handle(self):

        if self.rf.env == "测试环境":
            host = "https://qd2-gw.qa.qdingnet.com/"

            # 下载文件参数是固定的
            self.rf.dl_file_url = "https://caster.qa.qdingnet.com/v1/api/oss/getPresignedUrl"
            self.rf.bucket = "qa-qding2-saas-private"  # 测试 qa-qding2-saas-private ，生产 qding2-saas-private

            # 下载文件列表地址是固定的
            self.rf.export_list_url = urljoin(host, "/qdp2-cloud-base-saas-api/v1/api/exportRecord/pageExcelExport")

        elif self.rf.env == "线上环境":
            host = "https://s.qdingnet.com"
            host2 = "https://qd2-gw.qdingnet.com/"  # 生产的几个地址不一样，先把测试调试通了，之后在搞

            self.rf.dl_file_url = "https://caster.qdingnet.com/v1/api/oss/getPresignedUrl"
            self.rf.bucket = "qding2-saas-private"

            # self.rf.execute_export_url = urljoin(host2, "/qdp2-virgo-server-api/v1/api/taskinfo/exportNoteManageList")
            self.rf.export_list_url = urljoin(host2, "/qdp2-cloud-base-saas-api/v1/api/exportRecord/pageExcelExport")

        self.rf.config["千丁云登录url"] = urljoin(host, "/qdp2-base-auth-server-api/v1/api/auth/emp/login")

        self.rf.execute_export_url = urljoin(host, self.rf.execute_export_url)
        try:
            self.rf.execute_export_params = json.loads(self.rf.execute_export_params)
        except:
            self.error_msg = "请求参数不是json格式！！"

        self.rf.export_list_url_method = "POST"
        self.rf.export_list_url_params = {"pageSize": 20, "pageNum": 1}

    # 千丁云登录接口
    def login(self):

        url = self.rf.config["千丁云登录url"]
        params = {"phone": self.rf.config["千丁云账号"], "password": self.rf.config["千丁云密码"],
                  "imgVerifyCode": self.rf.config["千丁云验证码"], "channel": 11,
                  "imageToken": "9fa12631-8ddd-4f06-9a8d-1fdb795ab133"}
        h = {"Content-Type": "application/json"}
        try:
            res = requests.post(url, json=params, headers=h).json()
            self.set_log("登录响应体：{}".format(res))
        except Exception as e:
            self.error_msg = "请求登录接口出错：{}".format(e)
            return
        else:
            if res["code"] == "200":
                return res["data"]["auth"]
            else:
                self.error_msg = "请求登录接口出错：{}".format(res["msg"])
                return

    def sync_export(self):
        try:
            if self.rf.execute_export_method == "GET":
                file_data = requests.get(self.rf.execute_export_url, params=self.rf.execute_export_params,
                                         headers=self.headers, stream=True)
            else:
                file_data = requests.post(self.rf.execute_export_url, json=self.rf.execute_export_params,
                                          headers=self.headers, stream=True)

            file_name = "{}_同步导出_{}.xlsx".format(self.rf.title, int(time.time() * 1000))
            # 相对目录：/report_form/file_name
            relative_file_path = os.path.join("report_form", file_name)

            # 文件存放的真实位置： /var/www/CrazyTester/static/upload     /report_form/file_name
            real_file_path_dir = os.path.join(settings.MEDIA_ROOT_VIRTUAL, "report_form")
            if not os.path.exists(real_file_path_dir):
                os.makedirs(real_file_path_dir)
            real_file_path = os.path.join(real_file_path_dir, file_name)

            s = b""
            for chunk in file_data.iter_content(chunk_size=512):
                if chunk:
                    s += chunk
            with open(real_file_path, 'wb') as f:
                # for chunk in file_data.iter_content(chunk_size=512):
                #     if chunk:
                #         f.write(chunk)
                # f.write(file_data.content)
                f.write(s)
            try:
                # 如果可以转成json格式，说明返回的是错误信息，不是json格式说明是二进制文件信息
                dict_res = json.loads(str(s, encoding="utf-8"))
                self.set_log(dict_res)
            except:
                return relative_file_path
            else:
                self.error_msg = "同步导出 下载文件出错：{}".format(str(s, encoding="utf-8"))

        except Exception as e:
            self.error_msg = "同步导出 下载文件出错：{}".format(e)

    def execute_exprot_handle(self):
        headers = self.headers.copy()
        headers["Authorization"] = "Bearer " + headers["Authorization"]

        try:
            if self.rf.execute_export_method == "GET":
                res = requests.get(self.rf.execute_export_url, json=self.rf.execute_export_params,
                                   headers=headers).json()
            else:
                res = requests.post(self.rf.execute_export_url, json=self.rf.execute_export_params,
                                    headers=headers).json()
            self.set_log("执行导出响应体：{}".format(res))
        except Exception as e:
            self.error_msg = "执行导出接口出错：{}".format(e)
        else:
            if res["code"] != "200":
                self.error_msg = "执行导出接口出错：{}".format(res["msg"])
            else:
                return True

    def export_list_handle(self):

        for i in range(60):
            try:
                res = requests.post(self.rf.export_list_url, json=self.rf.export_list_url_params,
                                    headers=self.headers).json()
                self.set_log("导出列表响应体：{}".format(res))
            except Exception as e:
                self.error_msg = "导出文件列表接口出错：{}".format(e)
            else:
                if res["code"] != "200":
                    self.error_msg = "导出文件列表接口出错：{}".format(res["msg"])
                else:
                    first = res["data"]["records"][0]
                    if first["status"] != "100":
                        time.sleep(5)
                        # continue
                    else:
                        # getPresignedUrl(first["fileName"])
                        self.set_log(first["fileKey"])
                        return first["fileKey"]
        else:
            self.error_msg = "请求超时，总共请求时间300s"

    def getPresignedUrl(self, file_Key):

        params = {
            "key": str_to_base64(file_Key),
            "bucket": str_to_base64(self.rf.bucket),
        }

        try:
            res = requests.get(self.rf.dl_file_url, params=params, headers=self.headers).json()
        except Exception as e:
            self.error_msg = "异步导出 下载文件出错：{}".format(e)
            return
        try:
            file_url = res["data"]["url"]
            file_name = file_Key.split("/")[-1]

            # 相对目录：/report_form/file_name
            relative_file_path = os.path.join("report_form", file_name)

            real_file_path_dir = os.path.join(settings.MEDIA_ROOT_VIRTUAL, "report_form")
            if not os.path.exists(real_file_path_dir):
                os.makedirs(real_file_path_dir)
            real_file_path = os.path.join(real_file_path_dir, file_name)

            file_data = requests.get(file_url).content
            with open(real_file_path, 'wb') as f:
                f.write(file_data)

            return relative_file_path

        except Exception as e:
            self.error_msg = "异步导出 保存文件出错：{}\n响应：{}".format(e, res)

    def db_get_data(self):
        try:
            conn = pymysql.connect(self.rf.config["数据库地址"], self.rf.config["数据库用户"],
                                   self.rf.config["数据库密码"], self.rf.config["数据库使用库"], int(self.rf.config["数据库端口"]))
        except Exception as e:
            self.error_msg = "连接数据库失败：{}".format(e)
            return

        try:
            cursor = conn.cursor()
            cursor.execute(self.rf.sql)
            data = cursor.fetchall()
            # self.set_log(data)

            cursor.close()
            conn.close()

            return data
        except Exception as e:
            self.error_msg = "库中查找数据失败：{}".format(e)
            return

    def form_get_data(self, file_path):
        try:
            rbook = xlrd.open_workbook(file_path)
        except xlrd.biffh.XLRDError:
            self.error_msg = "不支持的格式"
            return
        except Exception as e:
            self.error_msg = "xlrd打开文件异常".format(e)
            return

        table = rbook.sheets()[0]  # 表示获取第一个表格

        # nrows = table.nrows  # 有效行数
        # ncols = table.ncols # 有效行数
        form_data = []
        for i in range(table.nrows):
            # print(table.row(i))  # 返回由该行中所有的单元格对象组成的列表
            # print(table.row_slice(i))  # 返回由该列中所有的单元格对象组成的列表
            # print(table.row_types(i, start_colx=0, end_colx=None))  # 返回由该行中所有单元格的数据类型组成的列表
            form_data.append(table.row_values(i, start_colx=0, end_colx=None))  # 返回由该行中所有单元格的数据组成的列表

        # self.set_log(form_data)
        return form_data

    def form_vs_db(self, db_data, form_data):
        len_form = len(form_data) - int(self.rf.start_line) + 1
        len_db = len(db_data)
        if len_form != len_db:
            self.error_msg = "数据总条数不一致，表：{}条， 库：{}条".format(len_form, len_db)
            return

        for i in range(len_db):
            if len(db_data[i]) != len(form_data[i + int(self.rf.start_line) - 1]):
                self.error_msg = "表中第{}行数据量不一致，表：{}条， 库：{}条".format(
                    i + int(self.rf.start_line) - 1, len(form_data[i + int(self.rf.start_line) - 1]), len(db_data[i]))
                return

            for j in range(len(db_data[i])):
                db_value = db_data[i][j]
                form_value = form_data[i + int(self.rf.start_line) - 1][j]

                if db_value is None:
                    db_value = ""

                # 对比原始类型
                if db_value != form_value:
                    # 原始类型不一致则都转成 str字符串格式对比一次
                    if str(db_value) != str(form_value):
                        self.error_msg = "表中第{}行 第{}列 数据值不一致！\n 表：{}：{}; 库：{}".format(
                            i + int(self.rf.start_line) - 1, j,
                            str(form_data[0][j]), str(form_data[i + int(self.rf.start_line) - 1][j]),
                            str(db_data[i][j]),
                        )
                    return


def str_to_base64(s):
    str_encode = base64.b64encode(s.encode('utf8'))
    return str(str_encode, encoding='utf8').replace("+", "-").replace("/", "_").strip("=")


def base64_to_str(s):
    str_decode = base64.b64decode(bytes(s, encoding="utf8"))
    return str(str_decode, encoding='utf8')


def get_t1(timestamp, token):
    mod = 3
    """
    原版js:
      timestamp += '';
      const md5Time = (timestamp % mod) + 1;
      let newToken = token;
      let newTimestamp = timestamp;

      for (let index = 0; index < md5Time; index += 1) {
        newToken = hexMd5(newToken);
        newTimestamp = hexMd5(newTimestamp);
      }
      let result = '';
      for (let index = 0; index < newToken.length && index < newTimestamp.length; index += 1) {
        result += newTimestamp.charAt(index) + newToken.charAt(index);
      }
  """
    md5Time = (timestamp % mod) + 1
    newToken = token
    newTimestamp = str(timestamp)

    for i in range(0, md5Time):
        newToken = hashlib.md5(newToken.encode("utf-8")).hexdigest()
        newTimestamp = hashlib.md5(newTimestamp.encode("utf-8")).hexdigest()

    result = ""
    l = len(newTimestamp) if len(newToken) > len(newTimestamp) else len(newToken)
    for i in range(0, l):
        result += newTimestamp[i] + newToken[i]

    return result


if __name__ == '__main__':
    pass
    fa = ReportFormTest()
    # fa.execute_exprot_handle()
    # fa.db_get_data()
    ret = fa.start()
    print(fa.error_msg)
    if ret:
        print("成功")
    else:
        print(fa.log)
        print(fa.error_msg)

