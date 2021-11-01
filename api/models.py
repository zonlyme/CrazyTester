from django.db import models
# from django.contrib.auth.models import AbstractUser

"""
https://blog.csdn.net/Great_Zhou/article/details/82560343

AutoField	自动增长的IntegerField，通常不用指定，不指定时Django会自动创建属性名为id的自动增长属性
BooleanField	布尔字段，值为True或False
NullBooleanField	支持Null、True、False三种值
CharField	字符串，参数max_length表示最大字符个数
TextField	大文本字段，一般超过4000个字符时使用
IntegerField	整数
DecimalField	十进制浮点数， 参数max_digits表示总位数， 参数decimal_places表示小数位数
FloatField	浮点数
DateField	日期， 参数auto_now表示每次保存对象时，自动设置该字段为当前时间，用于"最后一次修改"的时间戳，它总是使用当前日期，默认为False； 参数auto_now_add表示当对象第一次被创建时自动设置当前时间，用于创建的时间戳，它总是使用当前日期，默认为False; 参数auto_now_add和auto_now是相互排斥的，组合将会发生错误
TimeField	时间，参数同DateField
DateTimeField	日期时间，参数同DateField
FileField	上传文件字段
ImageField	继承于FileField，对上传的内容进行校验，确保是有效的图片

null	如果为True，表示允许为空，默认值是False
blank	如果为True，则该字段允许为空白，默认值是False
db_column	字段的名称，如果未指定，则使用属性的名称
db_index	若值为True, 则在表中会为此字段创建索引，默认值是False
default	默认
primary_key	若为True，则该字段会成为模型的主键字段，默认值是False，一般作为AutoField的选项使用
unique	如果为True, 这个字段在表中必须有唯一值，默认值是False

外键：
在设置外键时，需要通过on_delete选项指明主表删除数据时，对于外键引用表数据如何处理，在django.db.models中包含了可选常量：
CASCADE级联，删除主表数据时连通一起删除外键表中数据
PROTECT保护，通过抛出ProtectedError异常，来阻止删除主表中被外键应用的数据
SET_NULL设置为NULL，仅在该字段null=True允许为null时可用
SET_DEFAULT设置为默认值，仅在该字段设置了默认值时可用
SET()设置为特定值或者调用特定方法
DO_NOTHING不做任何操作，如果数据库前置指明级联性，此选项会抛出IntegrityError异常

"""


s_len = 100     # 标题类
m_len = 500     # 描述类
b_len = 1000     # 描述类


# class User(AbstractUser):
#     is_superuser2 = models.BooleanField(default=False, verbose_name='管理用户2：用于可见项目')


# 自定义常用模型管理器
class CustomManager(models.Manager):

    def get_queryset(self):
        return super(CustomManager, self).get_queryset().filter(isDelete=False)


# 通用的模型字段
class CustomModel(models.Model):
    # https://zhuanlan.zhihu.com/p/82818334
    # 但上述代码有个小问题owner字段的related_name属性在模型继承时丢失了。我们需要根据子类模型的名字，生成差异化的related_name。
    # 这时我们只需在父类模型中设置related_name时引用应用名app_label（%(app_label)s)或者子类的类名(%(class)s)。
    # 这里我们使用了%(class)s，表示小写形式的当前子类的类名。这样模型继承后，每个子类模型会生成自己专属的related_name,
    # 比如articles_related和courses_related。
    # owner = models.ForeignKey(User, related_name='%(class)s_related', on_delete=models.CASCADE)

    id = models.AutoField(primary_key=True, auto_created=True)
    title = models.CharField(max_length=s_len, verbose_name="标题", help_text="标题")

    isDelete = models.BooleanField(default=False, verbose_name='逻辑删除', help_text="逻辑删除")
    create_user = models.CharField(max_length=s_len, null=True, blank=True, verbose_name='创建人')
    create_user_id = models.CharField(max_length=s_len, null=True, blank=True, verbose_name='创建人id')
    latest_update_user = models.CharField(max_length=s_len, null=True, blank=True, verbose_name='最后更新者名称')
    latest_update_user_id = models.CharField(max_length=s_len, null=True, blank=True, verbose_name='最后更新者id')
    c_date = models.DateTimeField(auto_now_add=True, null=True, blank=True, verbose_name='创建时间')
    u_date = models.DateTimeField(auto_now=True, null=True, blank=True, verbose_name='修改时间')

    class Meta:
        abstract = True

    def __str__(self):
        return self.title

    m = CustomManager()


# 项目数据
class ApiProject(CustomModel):

    desc = models.CharField(max_length=s_len, null=True, blank=True, verbose_name='描述')
    version = models.CharField(max_length=s_len, null=True, blank=True, verbose_name='版本号')
    users = models.CharField(max_length=b_len, null=True, blank=True, verbose_name='可见用户')

    # global_host = models.ForeignKey(GlobalHost, on_delete=models.PROTECT, null=True, blank=True, verbose_name='默认全局域名', help_text="默认全局域名")
    # global_variable = models.ForeignKey(GlobalVariable, on_delete=models.PROTECT, null=True, blank=True, verbose_name='默认全局变量', help_text="默认全局变量")
    # global_header = models.ForeignKey(GlobalHeader, on_delete=models.PROTECT, null=True, blank=True, verbose_name='默认全局请求头', help_text="默认全局请求头")
    # global_cookie = models.ForeignKey(GlobalCookie, on_delete=models.PROTECT, null=True, blank=True, verbose_name='默认全局cookie', help_text="默认全局cookie")


    class Meta:
        db_table = "api_project"
        verbose_name = '项目'
        verbose_name_plural = '项目'


# 分组数据
class ApiGroup(CustomModel):

    project = models.ForeignKey(ApiProject, on_delete=models.PROTECT)

    class Meta:
        db_table = "api_group"
        verbose_name = '分组'
        verbose_name_plural = '分组'


# 接口数据
class ApiApi(CustomModel):
    # api_data = APIData.m.get(id=int(api_id)) api_data.parent_id是等于self.node_name
    group = models.ForeignKey(ApiGroup, on_delete=models.PROTECT)

    desc = models.CharField(max_length=m_len, null=True, blank=True, verbose_name='API描述')
    method = models.CharField(max_length=s_len, verbose_name='请求方式')

    params_example = models.TextField(null=True, blank=True, verbose_name='请求参数示例&解释')
    res_body_example = models.TextField(null=True, blank=True, verbose_name='响应体示例')

    class Meta:
        db_table = "api_api"
        verbose_name = '接口数据'
        verbose_name_plural = '接口数据'


# 用例数据
class ApiCase(CustomModel):
    """
        asserts格式：
            [
                {
                    "assert_method": "1",
                    "assert_key": "123",
                     "assert_expect_value": "123"
                 },
             ]
    """
    api = models.ForeignKey(ApiApi, on_delete=models.PROTECT)

    status = models.BooleanField(default=True, verbose_name='是否启用')
    desc = models.CharField(max_length=s_len, null=True, verbose_name='用例描述')

    url = models.CharField(max_length=m_len, verbose_name='请求地址')
    params = models.TextField(null=True, verbose_name='请求参数', help_text="get时 params与data合并,params.update(data)")
    data = models.TextField(null=True, verbose_name='请求体', help_text="post时 params拼到url,data作为数据")
    sample_data = models.TextField(null=True, verbose_name='样例数据', help_text="测试样例数据,分别格式化到params和data上")
    headers = models.TextField(null=True, verbose_name='请求头')
    cookies = models.TextField(null=True, verbose_name='cookies')

    # res_headers = models.TextField(null=True, verbose_name='上一次响应头', help_text="上一次响应头")
    # res_body = models.TextField(null=True, verbose_name='上一次响应体', help_text="上一次响应体")

    asserts = models.TextField(null=True, verbose_name='断言')
    prefix = models.TextField(null=True, verbose_name='前置操作')
    rsgv = models.TextField(null=True, verbose_name='响应体中的参数设置到全局变量')
    rsgh = models.TextField(null=True, verbose_name='响应体中的参数设置到全局请求头')
    set_global_cookies = models.BooleanField(default=True, verbose_name='响应cookies全部设置到当前全局cookies中')
    clear_global_cookies = models.BooleanField(default=True, verbose_name='清空全局cookies')

    class Meta:
        db_table = "api_case"
        verbose_name = '用例数据'
        verbose_name_plural = '用例数据'


# 测试报告
class TestReport(CustomModel):

    title = models.CharField(max_length=s_len, null=True, verbose_name="标题")
    task_id = models.CharField(max_length=s_len, null=True, verbose_name='关联测试任务id')
    task_group_id = models.CharField(max_length=s_len, null=True, verbose_name='关联测试任务组id')

    report = models.TextField(null=True, verbose_name='测试报告统计信息')
    global_env_id = models.CharField(max_length=s_len, null=True, verbose_name='全局环境id')
    global_env_title = models.CharField(max_length=s_len, null=True, verbose_name='全局环境标题')
    global_host = models.CharField(max_length=s_len, null=True, verbose_name='全局域名')
    test_type = models.CharField(max_length=s_len, null=True, verbose_name='测试类型')
    test_ret = models.BooleanField(default=None, null=True, verbose_name='测试结果')
    project_id = models.CharField(max_length=s_len, null=True, verbose_name='所属项目id')
    project_title = models.CharField(max_length=s_len, null=True, verbose_name='所属项目标题')

    trigger_way = models.CharField(max_length=s_len, null=True, verbose_name='执行方式', help_text="执行方式:定时任务/手动测试")

    send_workwx_user_group_flag = models.BooleanField(default=None, null=True, verbose_name='企业微信发送标识')
    send_workwx_user_group_msg = models.CharField(max_length=b_len, null=True, verbose_name='企业微信发送信息(错误信息)')

    send_workwx_group_chat_flag = models.BooleanField(default=None, null=True, verbose_name='企业微信发送标识')
    send_workwx_group_chat_msg = models.CharField(max_length=b_len, null=True, verbose_name='企业微信发送信息(错误信息)')

    send_email_flag = models.BooleanField(default=None, null=True, verbose_name='邮件发送标识')
    send_email_msg = models.CharField(max_length=b_len, null=True, verbose_name='邮件发送信息(错误信息)')

    flag = models.BooleanField(default=None, null=True, verbose_name='测试任务是否正常完成')
    erro_msg = models.CharField(max_length=b_len, null=True, verbose_name='导致测试任务无法正常完成的错误信息')
    execution_time = models.CharField(max_length=s_len, null=True, verbose_name='执行时长')

    class Meta:
        db_table = "api_test_report"
        verbose_name = '测试报告'
        verbose_name_plural = '测试报告'


# 测试报告详情：每一条用例数据
class TestReportDetail(CustomModel):

    title = models.CharField(max_length=s_len, null=True, verbose_name="标题")
    report_id = models.CharField(max_length=s_len, null=True, verbose_name='关联报告id')
    api_id = models.CharField(max_length=s_len, null=True, verbose_name='接口id')
    api_title = models.CharField(max_length=s_len, null=True, verbose_name='接口名称')
    api_desc = models.CharField(max_length=m_len, null=True, verbose_name='接口描述')
    method = models.CharField(max_length=s_len, null=True, verbose_name='请求方式')
    case_id = models.CharField(max_length=s_len, null=True, verbose_name='用例id')
    case_title = models.CharField(max_length=m_len, verbose_name='用例描述')
    final_ret = models.BooleanField(null=True, verbose_name='测试结果')
    case_info = models.TextField(null=True, verbose_name='测试详情数据')

    class Meta:
        db_table = "api_test_report_detail"
        verbose_name = '测试报告详情用例数据'
        verbose_name_plural = '测试报告详情用例数据'

    def __str__(self):
        return str(self.c_date)[:19]


# 测试任务
class TestTask(CustomModel):

    task_desc = models.CharField(max_length=m_len, verbose_name="测试任务描述")
    test_type = models.CharField(max_length=s_len, null=True, verbose_name='测试策略', help_text="测试策略：1全量，2冒烟，3场景")

    global_env_id_list = models.CharField(max_length=b_len, null=True, verbose_name='全局环境id列表')

    global_host_id = models.IntegerField(null=True, verbose_name='全局域名id')
    global_host_title = models.CharField(max_length=s_len, null=True, verbose_name='全局域名标题')

    global_variable_id = models.IntegerField(null=True, verbose_name='全局变量id')
    global_variable_title = models.CharField(max_length=s_len, null=True, verbose_name='全局变量标题')

    global_header_id = models.IntegerField(null=True, verbose_name='全局请求头id')
    global_header_title = models.CharField(max_length=s_len, null=True, verbose_name='全局请求头标题')

    global_cookie_id = models.IntegerField(null=True, verbose_name='全局cookie_id')
    global_cookie_title = models.CharField(max_length=s_len, null=True, verbose_name='全局cookie标题')

    project_id = models.CharField(max_length=s_len, null=True, verbose_name='项目id')
    project_title = models.CharField(max_length=m_len, null=True, verbose_name='项目名称')
    group_ids = models.CharField(max_length=b_len, null=True, verbose_name='分组id', help_text="分组id用,分割")
    group_title_list = models.TextField(null=True, verbose_name='分组名称', help_text="分组名称 json-list格式")
    api_ids = models.CharField(max_length=b_len, null=True, verbose_name='接口id', help_text="接口id用,分割")
    api_title_list = models.TextField(null=True, verbose_name='接口名称', help_text="接口名称 json-list格式")
    case_ids = models.CharField(max_length=4000, null=True, verbose_name='用例id', help_text="用例id用,分割")
    case_title_list = models.TextField(null=True, verbose_name='用例名称', help_text="用例名称 json-list格式")

    cron = models.CharField(max_length=s_len, null=True, verbose_name='cron表达式', help_text="cron表达式")
    next_execute_time = models.CharField(max_length=s_len, null=True, verbose_name='定时任务下次执行时间')
    cron_status = models.CharField(max_length=s_len, default="2", null=True, verbose_name='定时任务状态', help_text="定时任务状态：1.启动，2.未启动")

    workwx_user_group_id = models.IntegerField(null=True, verbose_name='企业微信用户组id')
    workwx_user_group_title = models.CharField(max_length=s_len, null=True, verbose_name='企业微信用户组标题')
    workwx_group_chat_id = models.IntegerField(null=True, verbose_name='企业微信群聊id')
    workwx_group_chat_title = models.CharField(max_length=s_len, null=True, verbose_name='企业微信群聊标题')
    email_user_group_id = models.IntegerField(null=True, verbose_name='邮箱组')
    email_user_group_title = models.CharField(max_length=s_len, null=True, verbose_name='邮箱组')

    isValid = models.BooleanField(default=True, verbose_name='测试内容是否有效', help_text="测试内容是否有效")
    msg = models.CharField(max_length=m_len, null=True, verbose_name='测试内容错误信息', help_text="测试内容错误信息")

    class Meta:
        db_table = "api_test_task"
        verbose_name = '测试任务'
        verbose_name_plural = '测试任务'


# 测试任务组
class TestTaskGroup(CustomModel):

    project_id = models.CharField(max_length=s_len, null=True, verbose_name='项目id')
    project_title = models.CharField(max_length=m_len, null=True, verbose_name='项目名称')

    desc = models.CharField(max_length=m_len, verbose_name="测试任务组描述")

    test_task_id_list = models.CharField(max_length=s_len, null=True, verbose_name='测试任务id')
    content = models.CharField(max_length=4000, null=True, verbose_name='任务内容')

    cron = models.CharField(default="", max_length=m_len, null=True, verbose_name='cron表达式')
    cron_status = models.CharField(default="2", max_length=s_len, null=True, verbose_name='定时任务状态', help_text="定时任务状态：1.启动，2.未启动")

    isValid = models.BooleanField(default=True, verbose_name='测试任务id是否有效')
    erro_msg = models.CharField(default="", max_length=b_len, null=True, verbose_name='测试任务无效错误信息')

    unified_receive_config = models.BooleanField(default=True, verbose_name='统一使用任务组的报告接收配置')
    workwx_user_group_id = models.IntegerField(null=True, verbose_name='企业微信用户组id')
    workwx_user_group_title = models.CharField(max_length=s_len, null=True, verbose_name='企业微信用户组标题')
    workwx_group_chat_id = models.IntegerField(null=True, verbose_name='企业微信群聊id')
    workwx_group_chat_title = models.CharField(max_length=s_len, null=True, verbose_name='企业微信群聊标题')
    email_user_group_id = models.IntegerField(null=True, verbose_name='企业微信应用id')
    email_user_group_title = models.CharField(max_length=s_len, null=True, verbose_name='企业微信应用标题')

    class Meta:
        db_table = "api_test_task_group"
        verbose_name = '测试任务组'
        verbose_name_plural = '测试任务组'


# 报表自动化-对比
class ReportForm(CustomModel):
    default_config = """
        {
            "千丁云账号": "",
            "千丁云密码": "",
            "千丁云验证码": "6666",
            "数据库地址":"",
            "数据库用户":"root",
            "数据库密码":"",
            "数据库使用库":"",
            "数据库端口":"3306"
        }
    """
    env_chooics = (('测试环境', '测试环境'), ('线上环境', '线上环境'))  # ReportForm.get_method_display() = display_name
    method_chooics = (('GET', 'GET'), ('POST', 'POST'))
    sync_type_chooics = (('1', '同步下载'), ('2', '异步下载'))

    project = models.ForeignKey(ApiProject, on_delete=models.PROTECT, default="1")

    # data.get_sync_type_display()
    env = models.CharField(max_length=s_len, choices=env_chooics, default='POST', verbose_name='执行导出地址 请求方式')
    sync_type = models.CharField(max_length=s_len, choices=sync_type_chooics, default='1', verbose_name='同步类型')

    execute_export_url = models.CharField(max_length=s_len, verbose_name='执行导出 地址')
    execute_export_method = models.CharField(max_length=s_len, choices=method_chooics, default='POST', verbose_name='执行导出 请求方式')
    execute_export_params = models.TextField(null=True, verbose_name='执行导出 请求参数', help_text="json格式")

    # 为异步时需要的参数
    # export_list_url = models.CharField(max_length=s_len, verbose_name='导出文件列表 地址', help_text="为异步下载时，必填")
    # export_list_url_method = models.CharField(max_length=s_len, choices=method_chooics, default='POST', verbose_name='导出文件列表 请求方式', help_text="为异步下载时，必填")
    # export_list_url_params = models.TextField(null=True, default='{"pageSize": 20, "pageNum": 1}', verbose_name='导出文件列表 请求参数', help_text="json格式, 为异步下载时，必填")

    start_line = models.CharField(max_length=s_len, default='2', verbose_name='从第x行开始对比')
    sql = models.TextField(verbose_name='sql对比语句')
    config = models.TextField(verbose_name='数据库配置', default=default_config)

    class Meta:
        db_table = "api_report_form"
        verbose_name = '报表自动化对比'
        verbose_name_plural = '报表自动化对比'


# 报表自动化-对比结果
class ReportFormResult(CustomModel):

    report_form = models.ForeignKey(ReportForm, on_delete=models.PROTECT, null=True, blank=True, verbose_name='所属报表')
    task_id = models.CharField(max_length=s_len, null=True, verbose_name='关联测试任务id', help_text="关联测试任务id")

    env = models.CharField(null=True, max_length=s_len, verbose_name='测试环境')
    sync_type = models.CharField(null=True, max_length=s_len, verbose_name='同步类型')
    trigger_way = models.CharField(null=True, max_length=s_len, verbose_name='同步类型')

    db_data = models.TextField(null=True, verbose_name='数据库数据')
    form_data = models.TextField(null=True, verbose_name='表数据')
    # 文件存放的真实位置： /var/www/CrazyTester/static/upload     /case_file/download/project_title/group_title/api_title
    file_path = models.CharField(null=True, max_length=m_len, verbose_name='文件相对地址')

    log = models.TextField(null=True, verbose_name='日志')
    error_msg = models.CharField(max_length=m_len, verbose_name='错误信息')
    test_ret = models.BooleanField(verbose_name='测试结果')

    class Meta:
        db_table = "api_report_form_result"
        verbose_name = '报表自动化对比结果'
        verbose_name_plural = '报表自动化对比结果'


# 报表自动化-任务
class RFTask(CustomModel):

    task_desc = models.CharField(max_length=m_len, verbose_name="测试任务描述")
    project = models.ForeignKey(ApiProject, on_delete=models.PROTECT, default="1")

    rf_ids = models.CharField(max_length=b_len, null=True, verbose_name='分组id')

    cron = models.CharField(max_length=s_len, null=True, verbose_name='cron表达式')
    cron_status = models.CharField(max_length=s_len, null=True, verbose_name='定时任务状态', help_text="定时任务状态：1.启动，2.未启动", default="2")

    workwx_user_group_id = models.IntegerField(null=True, verbose_name='企业微信用户组id')
    workwx_user_group_title = models.CharField(max_length=s_len, null=True, verbose_name='企业微信用户组标题')
    workwx_group_chat_id = models.IntegerField(null=True, verbose_name='企业微信群聊id')
    workwx_group_chat_title = models.CharField(max_length=s_len, null=True, verbose_name='企业微信群聊标题')

    isValid = models.BooleanField(default=True, verbose_name='测试内容是否有效')
    msg = models.CharField(max_length=m_len, null=True, verbose_name='测试内容错误信息')

    class Meta:
        db_table = "api_rf_task"
        verbose_name = '报表测试任务'
        verbose_name_plural = '报表测试任务'


# 报表自动化-任务执行结果
class RFTaskResult(CustomModel):

    rf_task_id = models.CharField(max_length=s_len, null=True, verbose_name='关联测试任务id')
    project_id = models.CharField(max_length=s_len, null=True, verbose_name='所属项目id')
    trigger_way = models.CharField(max_length=s_len, null=True, verbose_name='执行方式', help_text="执行方式:定时任务/手动测试")

    report = models.TextField(null=True, verbose_name='测试报告统计信息')
    success_count = models.CharField(max_length=s_len, null=True, verbose_name='关联测试任务id')
    fail_count = models.CharField(max_length=s_len, null=True, verbose_name='关联测试任务id')
    test_ret = models.BooleanField(default=None, null=True, verbose_name='测试结果')

    flag = models.BooleanField(default=True, null=True, verbose_name='测试任务是否正常完成')
    erro_msg = models.CharField(max_length=b_len, null=True, verbose_name='导致测试任务无法正常完成的错误信息')

    send_workwx_user_group_flag = models.BooleanField(default=None, null=True, verbose_name='企业微信发送标识')
    send_workwx_user_group_msg = models.CharField(max_length=b_len, null=True, verbose_name='企业微信发送信息(错误信息)')

    send_workwx_group_chat_flag = models.BooleanField(default=None, null=True, verbose_name='企业微信发送标识')
    send_workwx_group_chat_msg = models.CharField(max_length=b_len, null=True, verbose_name='企业微信发送信息(错误信息)')

    send_email_flag = models.BooleanField(default=None, null=True, verbose_name='邮件发送标识')
    send_email_msg = models.CharField(max_length=b_len, null=True, verbose_name='邮件发送信息(错误信息)')

    execution_time = models.CharField(max_length=s_len, null=True, verbose_name='执行时长')

    class Meta:
        db_table = "api_rf_task_result"
        verbose_name = '报表测试任务_结果'
        verbose_name_plural = '报表测试任务_结果'


# 全局域名
class GlobalHost(CustomModel):

    project = models.ForeignKey(ApiProject, on_delete=models.PROTECT, null=True, blank=True, verbose_name='所属项目')
    host = models.CharField(null=True, blank=True, max_length=s_len, verbose_name="域名")

    class Meta:
        db_table = "api_global_host"
        verbose_name = '全局域名'
        verbose_name_plural = '全局域名'


# 全局变量
class GlobalVariable(CustomModel):
    """
        params格式:
        [
            {
                "key": "key",
                "value": "value",
                "description": "description",
                "enabled": false
            }
        ]
    """

    project = models.ForeignKey(ApiProject, on_delete=models.PROTECT, null=True, blank=True, verbose_name='所属项目')
    params = models.TextField(null=True, blank=True, verbose_name="json格式全局变量")

    class Meta:
        db_table = "api_global_variable"
        verbose_name = '全局变量'
        verbose_name_plural = '全局变量'


# 全局请求头
class GlobalHeader(CustomModel):
    """
        params格式:
        {
            "key": "value",
            "key": "value",
            "key": "value",
        }
    """

    project = models.ForeignKey(ApiProject, on_delete=models.PROTECT, null=True, blank=True, verbose_name='所属项目')
    params = models.TextField(null=True, blank=True, verbose_name="josn格式请求头参数")

    class Meta:
        db_table = "api_global_header"
        verbose_name = '全局请求头'
        verbose_name_plural = '全局请求头'


# 全局cookie
class GlobalCookie(CustomModel):
    """
        params格式:
        {
            "key": "value",
            "key": "value",
            "key": "value",
        }
    """
    project = models.ForeignKey(ApiProject, on_delete=models.PROTECT, null=True, blank=True, verbose_name='所属项目')
    params = models.TextField(null=True, blank=True, verbose_name="json格式cookie参数")

    class Meta:
        db_table = "api_global_cookie"
        verbose_name = '全局cookie'
        verbose_name_plural = '全局cookie'


# 全局环境标签 + 环境配置详情
class GlobalEnv(CustomModel):
    project = models.ForeignKey(ApiProject, on_delete=models.PROTECT, null=True, verbose_name='所属项目')
    default_uses = models.BooleanField(default=False, verbose_name='默认使用')

    global_host = models.ForeignKey(GlobalHost, on_delete=models.PROTECT, null=True, blank=True, verbose_name='全局域名')
    global_variable = models.ForeignKey(GlobalVariable, on_delete=models.PROTECT, null=True, blank=True, verbose_name='全局变量')
    global_header = models.ForeignKey(GlobalHeader, on_delete=models.PROTECT, null=True, blank=True, verbose_name='全局请求头')
    global_cookie = models.ForeignKey(GlobalCookie, on_delete=models.PROTECT, null=True, blank=True, verbose_name='全局cookie')

    class Meta:
        db_table = "api_global_env"
        verbose_name = '全局环境'
        verbose_name_plural = '全局环境'


# 企业微信用户组配置
class WorkWxUserGroup(CustomModel):

    params = models.TextField(null=True, blank=True, verbose_name="用户名列表", help_text="用|分割，比如guojing02|cuiyongjian")

    class Meta:
        db_table = "workWX_user_group"
        verbose_name = '企业微信用户组配置'
        verbose_name_plural = '企业微信用户组配置'


# 企业微信群聊配置
class WorkWxGroupChat(CustomModel):

    params = models.TextField(null=True, blank=True, verbose_name="群聊webhookurl", help_text="群聊webhookurl，是群聊机器人的地址")

    class Meta:
        db_table = "workwx_group_chat"
        verbose_name = '企业微信群聊配置'
        verbose_name_plural = '企业微信群聊配置'


# 企业微信应用配置
class WorkWXApply(CustomModel):

    desc = models.CharField(max_length=s_len, null=True, blank=True, verbose_name="描述")
    corpid = models.CharField(max_length=s_len, null=True, blank=True, verbose_name="公司id")
    corpsecret = models.CharField(max_length=s_len, null=True, blank=True, verbose_name=" 应用的凭证密钥")
    agentid = models.CharField(max_length=s_len, null=True, blank=True, verbose_name="应用id")
    token = models.CharField(max_length=m_len, null=True, blank=True, verbose_name="应用的token")

    class Meta:
        db_table = "workwx_apply"
        verbose_name = '企业微信应用配置'
        verbose_name_plural = '企业微信应用配置'


# 邮箱用户组配置
class EmailUserGroup(CustomModel):

    params = models.TextField(null=True, blank=True, verbose_name="邮箱用户列表", help_text="例：123@qq.com,456@qq.com")

    class Meta:
        db_table = "email_user_group"
        verbose_name = '邮箱用户组配置'
        verbose_name_plural = '邮箱用户组配置'


# 用户权限配置
class ApiUser(CustomModel):

    type_id = models.CharField(max_length=s_len, verbose_name="类型id")
    type = models.CharField(max_length=s_len, null=True, blank=True, verbose_name="类型描述")
    users_id = models.CharField(max_length=s_len, null=True, blank=True, verbose_name="用户id")
    users = models.CharField(max_length=s_len, null=True, blank=True, verbose_name="用户名")

    class Meta:
        db_table = "api_user"
        verbose_name = '用户权限配置'
        verbose_name_plural = '用户权限配置'


if __name__ == '__main__':
    pass
    # TestTask.m.filter().order_by("-c_date") # 按c_date倒序
