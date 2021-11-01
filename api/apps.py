from django.apps import AppConfig


class InterfaceConfig(AppConfig):
    name = 'api'

    def ready(self):
        """
        在子类中重写此方法，以便在Django启动时运行代码,但是

            0. uwsig启动会启动多个进程，所以会启动多次以下任务，用socket绑定端口方式标识唯一
            1. 每次程序启动，先启动一个定时程序
            2. 遍历数据库，查看之前启动的任务（cron_status为1是启动）
            3. 定时程序中添加这些任务（如果有错，把定时任务状态改为2停止）
        :return:
        """
        pass
