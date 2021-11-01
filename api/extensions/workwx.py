import requests
from api.models import WorkWXApply, WorkWxUserGroup, WorkWxGroupChat
from api.view_basic import str_to_list
import datetime
import time

"""
    企业微信开放api
"""

# corpid = "wwcaca99303b016ebc"   # 公司id
# corpsecret = "IdrI0KP2mbhV2GA_jiFfU4eQ9GgGWroBCRqKX0KRvfE"  # 应用的凭证密钥
# agentid = "1000014"    # 应用id


class WorkWeixinApi:

    def __init__(self, id):
        self.msg = None
        self.ret = True
        self.id = id

        try:
            info = WorkWXApply.m.get(pk=id)
        except Exception as e:
            self.set_erro_msg("数据不存在！id:{}，{}".format(id, e))
        else:
            self.corpid = info.corpid
            self.corpsecret = info.corpsecret
            self.agentid = info.agentid
            self.token = info.token

            now = datetime.datetime.now()

            now = time.mktime(now.timetuple()) * 1000 + now.microsecond / 1000
            u_date = time.mktime(info.u_date.timetuple()) * 1000 + info.u_date.microsecond / 1000
            spend_time = (now - u_date) / 1000

            # print(now, u_date, spend_time)
            # 1. token有效时间7200秒，大于一定有效期才准备更新toekn
            if not self.token or spend_time >= 7199:
                time.sleep(2)
                new_token = self.get_token()
                if new_token:
                    # 2. token官方两小时会更新一次,token发生变化才更新入库
                    if new_token != self.token:
                        WorkWXApply.m.filter(id=id).update(
                            **{"token": new_token, "u_date": datetime.datetime.now()})
                        self.token = new_token

    def set_erro_msg(self, msg):
        self.ret = False
        self.msg = msg

    def get_token(self):

        # 获取token地址（每个应用的access_token是彼此独立的） get https://work.weixin.qq.com/api/doc/90000/90135/91039
        url = "https://qyapi.weixin.qq.com/cgi-bin/gettoken"
        params = {
            "corpid": self.corpid,
            "corpsecret": self.corpsecret
        }

        try:
            res = requests.get(url, params=params)
        except Exception as e:
            self.set_erro_msg("请求企业微信开放api:get_token 时出错！{}".format(e))
        else:
            res_body = res.json()
            if res_body["errcode"] == 0:    # 成功的响应
                return res_body["access_token"]

            else:
                self.set_erro_msg(res_body["errmsg"])

    def send_msg(self, touser, content, toparty=None, totag=None):
        """
        touser	否	成员ID列表（消息接收者，多个接收者用‘|’分隔，最多支持1000个）。特殊情况：指定为@all，则向关注该企业应用的全部成员发送
        toparty	否	部门ID列表，多个接收者用‘|’分隔，最多支持100个。当touser为@all时忽略本参数
        totag	否	标签ID列表，多个接收者用‘|’分隔，最多支持100个。当touser为@all时忽略本参数
        msgtype	是	消息类型，此时固定为：textcard
        agentid	是	企业应用的id，整型。企业内部开发，可在应用的设置页面查看；第三方服务商，可通过接口 获取企业授权信息 获取该参数值
        title	是	标题，不超过128个字节，超过会自动截断（支持id转译）
        description	是	描述，不超过512个字节，超过会自动截断（支持id转译）
        url	是	点击后跳转的链接。最长2048字节，请确保包含了协议头(http/https)
        btntxt	否	按钮文字。 默认为“详情”， 不超过4个文字，超过自动截断。
        enable_id_trans	否	表示是否开启id转译，0表示否，1表示是，默认0
        enable_duplicate_check	否	表示是否开启重复消息检查，0表示否，1表示是，默认0
        duplicate_check_interval	否	表示是否重复消息检查的时间间隔，默认1800s，最大不超过4小时
        :return:
        """

        # 发送应用消息地址  post    https://work.weixin.qq.com/api/doc/90000/90135/90236
        url = "https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={}"

        data = {
            "touser": touser,
            "toparty": toparty,
            "totag": totag,
            "msgtype": "text",
            "agentid": self.agentid,
            "text": {
                "content": content
            },
            "safe": 0,
            "enable_id_trans": 0,
            "enable_duplicate_check": 0,
            "duplicate_check_interval": 1800
        }
        # data = {
        #     "touser": touser,
        #     "toparty": toparty,
        #     "totag": totag,
        #     "msgtype": "textcard",
        #     "agentid": self.agentid,
        #     "enable_id_trans": 0,
        #     "enable_duplicate_check": 0,
        #     "duplicate_check_interval": 1800,
        #     "textcard": textcard
        # }

        try:
            res = requests.post(url.format(self.token), json=data)
        except Exception as e:
            self.set_erro_msg("请求企业微信开放api: send_msg 时出错！{}".format(e))
        else:
            res_body = res.json()
            if res_body["errcode"] != 0:    # 成功的响应
                self.set_erro_msg(res_body["errmsg"])
            else:
                return True
        return False


def send_workwx_user_group_(workwx_user_group_id, content):

    if workwx_user_group_id:
        info = WorkWxUserGroup.m.get(id=workwx_user_group_id)
        workwx_user_group = info.params or ""
        return send_workwx_user_group(content, workwx_user_group)
    else:
        return None, "无接收用户组"


def send_workwx_user_group(content, workwx_user_group="guojing02"):

    # 2.2. 发送企业微信用户组
    send_workwx_user_group_flag = None
    send_workwx_user_group_msg = ""
    if workwx_user_group:
        wwx = WorkWeixinApi(2)
        # send_workwx_msg = wwx.msg
        if wwx.msg:
            send_workwx_user_group_flag = False
        else:
            send_workwx_user_group_flag = wwx.send_msg(workwx_user_group, content)
        send_workwx_user_group_msg = wwx.msg
    else:
        send_workwx_user_group_msg = "无接收用户组"

    return send_workwx_user_group_flag, send_workwx_user_group_msg


def send_workwx_group_chat_(workwx_group_chat_id, content):

    if workwx_group_chat_id:
        info = WorkWxGroupChat.m.get(id=workwx_group_chat_id)
        workwx_group_chat = info.params or ""
        return send_workwx_group_chat(content, workwx_group_chat)
    else:
        return None, "无接收群"


def send_workwx_group_chat(content, workwx_group_chat):

    # 2.3 发送企业微信群
    send_workwx_group_chat_flag = None
    send_workwx_group_chat_msg = ""
    body = {
        "msgtype": "text",
        "text": {
            "content": content,
            "mentioned_list": [],
            "mentioned_mobile_list": []
        }
    }
    if workwx_group_chat:
        try:
            res = requests.post(workwx_group_chat, json=body)
            json_res = res.json()
            if json_res["errcode"] == 0:    # errcode=0为成功
                send_workwx_group_chat_flag = True
            else:
                send_workwx_group_chat_flag = False
                send_workwx_group_chat_msg = json_res["errmsg"]
        except Exception as e:
            send_workwx_group_chat_msg = "发送错误：{}".format(e)
    else:
        send_workwx_group_chat_msg = "无接收群"
    return send_workwx_group_chat_flag, send_workwx_group_chat_msg
