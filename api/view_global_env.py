from api.view_basic import *

# @require_http_methods(["GET"])
# def get_global_host(req):
#
#     try:
#         raw_data = GlobalHost.m.filter()
#         item = page_handel(req, raw_data)
#
#     except Exception as e:
#         return response_400("错误信息：{}".format(e))
#
#     return response_200(**item)


@require_http_methods(["GET"])
def get_global_env(req):

    project_id = req.GET.get("project_id", "")
    item = {}
    if project_id:
        item["project_id"] = project_id

    return customer_get_list(GlobalEnv, item)


@require_http_methods(["GET"])
def get_global_host(req):

    return customer_get_list(GlobalHost)


@require_http_methods(["GET"])
def get_global_variable(req):

    return customer_get_list(GlobalVariable)


@require_http_methods(["GET"])
def get_global_header(req):

    return customer_get_list(GlobalHeader)


@require_http_methods(["GET"])
def get_global_cookie(req):

    return customer_get_list(GlobalCookie)


class GlobalConfig:

    host = None
    variable = None
    header = None
    cookie = None
    # session = None

    # def __init__(self, global_host_id, global_variable_id, global_header_id, global_cookie_id):
    def __init__(self, global_env_id):

        self.msg = None
        try:
            self.env = GlobalEnv.m.get(pk=global_env_id)
        except:
            self.msg = "不存在的环境id：{}".format(global_env_id)
        # self.get_global_env(global_env_id)
        # self.session = requests.session()
        # self.global_host_id = global_host_id
        # self.global_variable_id = global_variable_id
        # self.global_header_id = global_header_id
        # self.global_cookie_id = global_cookie_id

    def get_global_config(self):
        self._global_host_handle(self.env.global_host_id)
        self._global_variable_handle(self.env.global_variable_id)
        self._global_header_handle(self.env.global_header_id)
        self._global_cookie_handle(self.env.global_cookie_id)
        # print(self.get_global_config_dict())

    def get_global_config_dict(self):
        return {
            "global_host": {
                "id": self.host.id,
                "title": self.host.title,
                "params": self.host.host,
            } if self.host else None,
            "global_variable": {
                "id": self.variable.id,
                "title": self.variable.title,
                "params": self.variable.params,
            } if self.variable else None,
            "global_header": {
                "id": self.header.id,
                "title": self.header.title,
                "params": self.header.params,
            } if self.header else None,
            "global_cookie": {
                "id": self.cookie.id,
                "title": self.cookie.title,
                "params": self.cookie.params,
            } if self.cookie else None,
        }

    def global_variable_append_and_save(self, key, value, set_method, global_save_flag):

        """
        :param key:         type: str
        :param value:       type: str
        :param set_method:      True 覆盖同名变量, False:追加到已有同名变量值中
        :param global_save_flag:  是否保存数据入库
        :return:
        """
        if self.variable is not None:
            for i in self.variable.params:
                if i["key"] == key:
                    if set_method:
                        i["value"] = [value]
                    else:
                        i["value"].append(value)
                    break
            else:
                params_item = {
                    "key": key,
                    "value": [value],
                    "description": "",
                    "enabled": True
                }
                self.variable.params.append(params_item)

            if global_save_flag:
                self._save_global_variable_params()
            # self.append_params(self.variable.params, key, value, set_method)

    def global_header_update_and_save(self, item, global_save_flag):
        if self.header is not None:
            self.header.params.update(item)
            if global_save_flag:
                self._save_global_header_params()

    def global_cookie_update_and_save(self, item, global_save_flag):
        if self.cookie is not None:
            self.cookie.params.update(item)
            if global_save_flag:
                self._save_global_cookie_params()

    def global_cookie_clear_params(self, global_save_flag):
        if self.cookie is not None:
            self.cookie.params = {}
            if global_save_flag:
                self._save_global_cookie_params()

    def _save_global_variable_params(self):
        # 保存入库
        GlobalVariable.m.filter(
            id=self.variable.id).update(
            params=json_dumps_indent4(self.variable.params),
            u_date=get_now_time())

    def _save_global_header_params(self):
        # 保存入库
        GlobalHeader.m.filter(
            id=self.header.id).update(
            params=json_dumps_indent4(self.header.params),
            u_date=get_now_time())

    def _save_global_cookie_params(self):
        # 保存入库
        GlobalCookie.m.filter(
            id=self.cookie.id).update(
            params=json_dumps_indent4(self.cookie.params),
            u_date=get_now_time())

    def _global_host_handle(self, global_host_id):
        if global_host_id:
            try:
                self.host = GlobalHost.m.get(pk=global_host_id)
            except:
                self.msg = "不存在的全局域名: {}".format(global_host_id)
            else:
                self.host.host = self.host.host or ""
        else:
            # self.msg = "全局域名id不可为空！"
            self.host = None

    def _global_variable_handle(self, global_variable_id):
        if global_variable_id:
            try:
                self.variable = GlobalVariable.m.get(pk=global_variable_id)
            except:
                self.msg = "不存在的全局变量: {}".format(global_variable_id)
            else:
                try:
                    self.variable.params = json.loads(self.variable.params) if self.variable.params else []
                except Exception as e:
                    self.msg = "全局变量数据格式有误, 应为json格式, 请检查!"
                else:

                    if type(self.variable.params) != list:
                        self.msg = "全局请求头数据, 应为list格式, 请检查!"
                        return
                    try:
                        for i in self.variable.params:
                            i.get("key")
                            i.get("value")
                            i.get("enabled")
                            i.get("description")
                    except:
                        self.msg = "全局变量数据有误! id:{}".format(global_variable_id)
        else:
            # self.msg = "全局变量id不可为空！"
            self.variable = None

    def _global_header_handle(self, global_header_id):
        if global_header_id:
            try:
                self.header = GlobalHeader.m.get(pk=global_header_id)
            except:
                self.msg = "不存在的全局请求头: {}".format(global_header_id)
            else:
                try:
                    self.header.params = json.loads(self.header.params) if self.header.params else {}
                except Exception as e:
                    self.msg = "全局请求头数据格式有误, 应为json格式, 请检查!"
                else:
                    if type(self.header.params) != dict:
                        self.msg = "全局请求头数据, 应为dict格式, 请检查!"
                        return
                    # for k, v in self.header.params.items():
                    #     if type(v) != str:
                    #         self.msg = "全局请求头数据 变量的值只可为字符串！"
                    #         return
        else:
            # self.msg = "全局请求头id不可为空！"
            self.header = None

    def _global_cookie_handle(self, global_cookie_id):
        if global_cookie_id:
            try:
                self.cookie = GlobalCookie.m.get(pk=global_cookie_id)
            except:
                self.msg = "不存在的全局cookie: {}".format(global_cookie_id)
            else:
                try:
                    self.cookie.params = json.loads(self.cookie.params) if self.cookie.params else {}
                except Exception as e:
                    self.msg = "全局cookie数据格式有误, 应为json格式, 请检查!"
                else:
                    if type(self.cookie.params) != dict:
                        self.msg = "全局cookie数据, 应为dict格式, 请检查!"
                        return
                    for k, v in self.cookie.params.items():
                        if type(v) != str:
                            self.msg = "全局cookie数据 变量值只可为字符串格式！"
                            return
        else:
            # self.msg = "全局cookie id不可为空！"
            self.cookie = None
