import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
import socket
"""
    发送邮件模块
        可发送标题，内容，附件
    使用：
        传入发送人，邮箱host，邮箱授权码，收件人s，标题，正文，文件可空
    注意：
        如果添加附件可能会被发送到垃圾箱中
"""

def send_email(sender, mail_host, mail_pass, receivers, title, body_text, file_path=None):

    # 创建一个带附件的实例
    message = MIMEMultipart()
    message['From'] = "{}".format(sender)   # 发件人
    message['To'] = ";".join(receivers)     # 收件人(list)
    message['Cc'] = sender    # 抄送(list)
    message['Subject'] = Header(title, 'utf-8')
    # 邮件正文内容
    # message.attach(MIMEText('这里是正文', 'plain', 'utf-8'))
    message.attach(MIMEText(body_text, 'plain', 'utf-8'))

    if file_path:
        # 构造附件1，传送当前目录下的 test.txt 文件
        att = MIMEText(open(file_path, 'rb').read(), 'base64', 'utf-8')
        att["Content-Type"] = 'application/octet-stream'
        # 这里的filename可以任意写，写什么名字，邮件中显示什么名字
        filename = file_path.split("/")[-1]
        att["Content-Disposition"] = 'attachment; filename="{}"'.format(filename)
        message.attach(att)

    try:
        smtpObj = smtplib.SMTP_SSL(mail_host, 465)  # 启用SSL发信, 端口一般是465
        smtpObj.login(sender, mail_pass)  # 登录验证
        smtpObj.sendmail(sender, receivers, message.as_string())
        print("邮件发送成功")
        return True
    except Exception as e:
        print("Error: 无法发送邮件:{}".format(e))
        return False

if __name__ == '__main__':
    MAIL_HOST = "smtp.163.com"  # SMTP服务器
    SENDER = 'a1159015630@163.com'
    MAIL_PASS = "guo0605"  # 授权密码，非登录密码
    receivers = ['547684776@qq.com', "1159015630@qq.com"]  # 接收邮件，可设置为你的QQ邮箱或者其他邮箱
    # receivers = ["庸人自扰° <547684776@qq.com>", "没希望、绝望﹏ 噬心 <1159015630@qq.com>"]  # 接收邮件，可设置为你的QQ邮箱或者其他邮箱
    file_path = "./urls.py"
    title = "这里是标题"
    body_text = "这里是正文"
    send_email(SENDER, MAIL_HOST, MAIL_PASS, receivers, title, body_text)

