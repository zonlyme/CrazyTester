import jwt
import datetime
from django.conf import settings


def creat_jwt_token(payload, timeout=settings.TOKEN_TIMEOUT):
    """
        jwt生成token由三部分组成： header加密.payload加密.前两者加盐在加密

        header： 固定信息，可以自定义
        payload: 一般都是用户信息，不要放用户隐私信息，密码电话等
        第三段： 根据salt，一般都是django框架的SECRET_KEY，不可泄漏

        解密时，三段信息同时解密，第三段根据solt解出来的信息能和前两段对上就是通过的token
    :return:
    """

    salt = settings.SECRET_KEY
    payload["exp"] = datetime.datetime.utcnow() + datetime.timedelta(minutes=timeout)   # 设置token超时

    headers = {
        "typ": "jwt",
        "alg": "HS256"
    }

    token = jwt.encode(payload=payload, key=salt, algorithm="HS256", headers=headers).decode("utf-8")

    return token

