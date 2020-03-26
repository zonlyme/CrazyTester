from django.db import models


s_len = 100     # 标题类
m_len = 500     # 描述类
b_len = 5000    # 大文本类


class NavNodeManager(models.Manager):
    # get_queryset:所有的查询都会这个方法
    def get_queryset(self):
        # 自定义的管理器重写方法，新增过滤功能
        return super(NavNodeManager, self).get_queryset().filter(isDelete=False)


# 节点模型
class NavNode(models.Model):
    node_name = models.CharField(max_length=s_len, verbose_name='节点名字')  # 节点名字
    isDelete = models.BooleanField(default=False)  # 是否删除 默认没有删除
    c_date = models.DateTimeField(auto_now_add=True, null=True)  # 创建时间
    e_date = models.DateTimeField(auto_now=True, null=True)  # 修改时间

    class Meta:
        # 将表的名字修改为：navnode，默认为项目名+应用名
        db_table = "navnode"
        verbose_name = '节点'
        verbose_name_plural = '节点'

    def __str__(self):
        return self.node_name

    # 自定义的模型管理器
    m = NavNodeManager()


# 接口数据管理器Manager
class APIDataManager(models.Manager):
    # get_queryset:所有的查询都会这个方法
    def get_queryset(self):
        # 自定义的管理器重写方法，新增过滤功能
        return super(APIDataManager, self).get_queryset().filter(isDelete=False)


# 接口数据模型
class APIData(models.Model):
    # 设置外键 父级节点，这里对应的是NavNode表中功能模块的id
    parent_id = models.ForeignKey(NavNode, on_delete=models.CASCADE)

    title = models.CharField(max_length=s_len, verbose_name='API标题')  # API标题
    desc = models.CharField(max_length=m_len, null=True)  # API描述
    method = models.CharField(max_length=s_len)  # 请求方式

    isDelete = models.BooleanField(default=False)  # 是否删除 默认没有删除
    c_date = models.DateTimeField(auto_now_add=True, null=True)  # 创建时间
    e_date = models.DateTimeField(auto_now=True, null=True)  # 修改时间
    # params_example = models.TextField(null=True)  # 请求参数示例或者是请求参数解释，待定字段
    # res_body_example = models.TextField(null=True)  # 返回的响应体示例

    class Meta:
        # 将表的名字修改为：apidata，默认为项目名 + 应用名
        db_table = "apidata"
        verbose_name = '接口数据'
        verbose_name_plural = '接口数据'

    def __str__(self):
        return self.title

    # 自定义的模型管理器
    m = APIDataManager()


# 接口数据管理器Manager
class CaseDataManager(models.Manager):
    # get_queryset:所有的查询都会这个方法
    def get_queryset(self):
        # 自定义的管理器重写方法，新增过滤功能
        return super(CaseDataManager, self).get_queryset().filter(isDelete=False)


# 用例数据模型
class CaseData(models.Model):
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
    # 设置外键 父级节点，这里对应的是apidata表中功能模块的id
    parent_id = models.ForeignKey(APIData, on_delete=models.CASCADE)

    title = models.CharField(max_length=s_len, default="new_cese", verbose_name='case标题')  # case标题
    desc = models.CharField(max_length=m_len, null=True)  # case描述
    url = models.CharField(max_length=m_len)  # 请求地址

    params = models.TextField(null=True)  # get时 params与data合并,params.update(data)
    data = models.TextField(null=True)  # post时 params拼到url,data作为数据
    headers = models.TextField(null=True)  # kv格式的请求头
    cookies = models.TextField(null=True)  # json格式的cookies

    res_headers = models.TextField(null=True)  # 返回的响应头
    res_body = models.TextField(null=True)  # 返回的响应体

    asserts = models.TextField(null=True)  # 验证信息
    prefix = models.TextField(null=True)  # 前置操作数据
    rsgv = models.TextField(null=True)  # 响应设置全局变量数据
    status = models.CharField(max_length=s_len, default="1")  # case状态 true启用,false禁用

    c_date = models.DateTimeField(auto_now_add=True, null=True)  # 创建时间
    e_date = models.DateTimeField(auto_now=True, null=True)  # 修改时间

    isDelete = models.BooleanField(default=False)  # 是否删除 默认没有删除0

    class Meta:
        # 将表的名字修改为：casedata，默认为项目名+应用名
        db_table = "casedata"
        verbose_name = '用例数据'
        verbose_name_plural = '用例数据'

    def __str__(self):
        return self.title

    # 自定义的模型管理器
    m = APIDataManager()


# 测试报告管理器Manager
class TestReportManager(models.Manager):
    # get_queryset:所有的查询都会这个方法
    def get_queryset(self):
        # 自定义的管理器重写方法，新增过滤功能
        return super(TestReportManager, self).get_queryset()

# 测试报告
class TestReport(models.Model):

    task_id = models.CharField(max_length=s_len, null=True)     # 本次测试任务的唯一id,为测试时间戳
    title = models.CharField(max_length=s_len, null=True, verbose_name="测试报告标题")      # 测试报告标题
    report = models.TextField(null=True)                    # 测试报告统计信息
    # node_info = models.TextField(null=True)                    # 测试报告节点数据
    tester = models.CharField(max_length=s_len, null=True)     # 测试员名字
    c_date = models.DateTimeField(auto_now_add=True, null=True)  # 创建时间

    class Meta:
        # 将表的名字修改为：testreport，默认为项目名+应用名
        db_table = "testreport"
        verbose_name = '测试报告'
        verbose_name_plural = '测试报告'

    def __str__(self):
        return str(self.c_date)[:19]

    # 自定义的模型管理器
    m = TestReportManager()


# 测试报告管理器Manager
class TestReportDetailManager(models.Manager):
    # get_queryset:所有的查询都会这个方法
    def get_queryset(self):
        # 自定义的管理器重写方法，新增过滤功能
        return super(TestReportDetailManager, self).get_queryset()


# 测试报告下每一个接口数据
class TestReportDetail(models.Model):

    task_id = models.CharField(max_length=s_len, null=True)     # 本次测试任务的唯一id,为测试时间戳
    api_id = models.CharField(max_length=s_len, null=True)     # 用例所属api的id
    api_title = models.CharField(max_length=s_len, null=True)     # 用例所属api的标题
    api_desc = models.CharField(max_length=m_len, null=True)     # 用例所属api的描述
    method = models.CharField(max_length=s_len, null=True)     # 用例所属api的请求方式
    case_id = models.CharField(max_length=s_len, null=True)     # 用例所属case_id
    case_title = models.CharField(max_length=m_len)             # 用例所属case_id
    final_ret = models.BooleanField(null=True)                  # 此用例最终结果
    case_info = models.TextField(null=True)                     # 调用完的用例数据
    c_date = models.DateTimeField(auto_now_add=True, null=True)  # 创建时间

    class Meta:
        db_table = "testreport_detail"
        verbose_name = '测试报告详情用例数据'
        verbose_name_plural = '测试报告详情用例数据'

    def __str__(self):
        return str(self.c_date)[:19]

    # 自定义的模型管理器
    m = TestReportDetailManager()



# 测试环境参数管理器Manager
class EnvDataManager(models.Manager):
    # get_queryset:所有的查询都会这个方法
    def get_queryset(self):
        # 自定义的管理器重写方法，新增过滤功能
        return super(EnvDataManager, self).get_queryset()


# 测试环境参数
class EnvData(models.Model):
    """
        params格式:
            [
                {
                    "key": "UID",
                    "value": "KIOWDE99",
                    "description": "测试郭靖账号",
                    "enabled": true
                },
                {
                    "key": "SECURITY_KEY",
                    "value": "lK2CNg7wokSCjbDgTYK0DGmOehWY6IXuN2jDpjrS8fkDpgAWFPttlFZso6wFjzmN",
                    "description": "",
                    "enabled": true
                }
            ]
    """

    title = models.CharField(max_length=s_len, verbose_name="测试环境标题")   # 测试环境标题
    host = models.CharField(max_length=s_len)                      # 域名
    params = models.TextField(null=True)                        # 配置参数（参数化参数，像postman一样，之后要把域名也放进来）
    c_date = models.DateTimeField(auto_now_add=True, null=True)  # 创建时间

    class Meta:
        # 将表的名字修改为：testreport，默认为项目名+应用名
        db_table = "envdata"
        verbose_name = '环境参数'
        verbose_name_plural = '环境参数'

    def __str__(self):
        return self.title

    # 自定义的模型管理器
    m = EnvDataManager()



