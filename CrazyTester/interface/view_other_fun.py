from .view_basic import *
import xlrd
import os
import sys
import xlwt

@login_required
# excel用例导入数据库主函数
def upload_case(req):

    obj = req.FILES.get('case_file')
    if not obj:
        return HttpResponse("没有选择文件")
    # 组合文件目录
    file_path = os.path.join(settings.MEDIA_ROOT_VIRTUAL, "case_file", "upload", obj.name)
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
    ret_msg = excel_handle(file_path)
    return HttpResponse(ret_msg)


# excel数据格式检测
def excel_handle(file_path):
    try:
        rbook = xlrd.open_workbook(file_path)
    except xlrd.biffh.XLRDError:
        return "不支持的格式"
    except Exception as e:
        return "xlrd打开文件异常".format(e)
    table = rbook.sheets()[0]  # 表示获取第一个表格

    nrows = table.nrows  # 有效行数

    # 全部行：目录名字	接口名字	接口描述	请求方式	请求地址
    #       用例状态    用例名字	用例描述	headers	入参	请求体 断言信息    前置操作    响应设置全局变量
    # 不可为空的字段
    not_none = ["目录名字", "接口名字", "请求方式", "请求地址", "用例名字"]
    # 必须为json格式的字段
    is_json = ["headers", '入参-url参数', '入参-请求体', "断言信息", "前置操作", "响应设置全局变量"]
    # 可以为空的字段
    allow_is_none = ["接口描述", "用例状态", "用例描述", "headers", "入参", "断言信息", "前置操作", "响应设置全局变量"]
    for row in range(14):
        for col in range(1, nrows):
            try:
                field_name = table.cell_value(0, row)
                this = table.cell_value(col, row)
                if field_name in not_none:
                    if not str(this).strip():
                        return "{}-第{}行不能为空：{}".format(field_name, col + 1, format(table.cell_value(col, row)))
                    continue
                elif field_name in is_json:
                    if str(this).strip():
                        try:
                            temp = json.loads(this)
                            if type(temp) == str:
                                return "{}-第{}行是字符串！".format(field_name, col + 1)
                        except:
                            return "{}-第{}行不是json格式！".format(field_name, col + 1)
            except Exception as e:
                return "异常:{}".format(e)

    else:
        for row in range(1, nrows):  # 从第二行开始遍历
            item = {}
            item["node_name"] = str(table.cell_value(row, 0)).strip()

            item["api_title"] = str(table.cell_value(row, 1)).strip()
            item["api_desc"] = str(table.cell_value(row, 2)).strip()
            item["method"] = str(table.cell_value(row, 3)).strip()
            item["url"] = str(table.cell_value(row, 4)).strip()


            item["case_status"] = str(table.cell_value(row, 5)).strip()
            item["case_title"] = str(table.cell_value(row, 6)).strip()
            item["case_desc"] = str(table.cell_value(row, 7)).strip()

            item["headers"] = str(table.cell_value(row, 8)).strip()
            item["params"] = str(table.cell_value(row, 9)).strip()
            item["data"] = str(table.cell_value(row, 10)).strip()
            item["asserts"] = str(table.cell_value(row, 11)).strip()
            item["prefix"] = str(table.cell_value(row, 12)).strip()
            item["rsgv"] = str(table.cell_value(row, 13)).strip()

            erro_msg = excel_insert_db_handle(item)
            if erro_msg:
                return erro_msg

        return "导入数据库成功！"


# excel数据入库
def excel_insert_db_handle(item):
    erro_msg = ""

    """
        :param item: excel表中数据组合出来的item
        :return:节点，接口：根据标题筛选，没有则创建
                用例：根据标题筛选，有此标题则更新，没有则创建
    """
    try:
        try:
            node_data = NavNode.m.get(node_name=item["node_name"])
            node_id = node_data.id
        except Exception as e:
            node_item = {"node_name":item["node_name"]}
            new_node = NavNode.m.create(**node_item)
            node_id = new_node.id

        try:
            api_data = APIData.m.get(title=item["api_title"], parent_id=node_id)
            api_id = api_data.id
        except Exception as e:
            api_item = {
                "title": item["api_title"],
                "desc": item["api_desc"],
                "method": item["method"].capitalize(),
                "parent_id_id": node_id,
            }
            new_api = APIData.m.create(**api_item)
            api_id = new_api.id

        case_item = {
            "status":item["case_status"],
            "title":item["case_title"],
            "desc": item["case_desc"],
            "url": item["url"],
            "headers": item["headers"],
            "params": item["params"],
            "data": item["data"],
            "asserts": item["asserts"],
            "prefix": item["prefix"],
            "rsgv": item["rsgv"],
            "parent_id_id": api_id,
        }
        ret = CaseData.m.filter(parent_id=api_id, title=item["case_title"])
        # ret = CaseData.m.get(parent_id=api_id, title=item["case_title"], params=item["params"])
        if ret:
            CaseData.m.filter(id=ret[0].pk).update(**case_item)
        else:
            CaseData.m.create(**case_item)
    except Exception as e:
        erro_msg = "{}".format(e)

    return erro_msg


# 接口下所有用例数据导入表
def dl_api_case_data(req):
    """
    :param req:
    1. 验证是否有此api
    2. 根据api整理出用例数据
    3. 将数据写入表
    4. 返回此函数验证结果，
        r_data = {
            "ret": False,   成功：ｊｓ再次发起请求，请求文件，失败：ｊｓ前段其实错误信息
            "erro_msg": None,   错误信息
            "file_name": None   文件名字
        }
    :return:
    """
    r_data = {
        "ret": False,
        "erro_msg": None,
        "file_path": None,
        "file_name": None
    }

    #　1. 验证是否有此api
    api_id = req.GET.get('api_id', None)
    if api_id:
        try:
            api_data = APIData.m.get(pk=api_id)
        except Exception as e:
            r_data["erro_msg"] = "没有此接口：{}，{}".format(api_id, e)
        else:
            # 2. 根据api整理出用例数据
            node_data = NavNode.m.get(pk=api_data.parent_id_id)
            case_datas = CaseData.m.filter(parent_id=api_id)
            items = []
            for case_data in case_datas:
                item = [node_data.node_name,
                        api_data.title,
                        api_data.desc,
                        api_data.method,
                        case_data.url or "",
                        case_data.status or "",
                        case_data.title or "",
                        case_data.desc or "",
                        case_data.headers or "",
                        case_data.params or "",
                        case_data.data or "",
                        case_data.asserts or "",
                        case_data.prefix or "",
                        case_data.rsgv or ""
                ]
                items.append(item)

            # 3. 将数据写入表
            sheet_header = ['目录名字', '接口名字', '接口描述', '请求方式', '请求地址',
                            '用例状态', '用例名字', '用例描述', 'headers',
                            '入参-url参数', '入参-请求体', '断言信息', "前置操作", "响应设置全局变量"]  # 表头部信息

            file_name = "{}.xls".format(api_data.title.replace(":", "-"))
            # 目录：SoftwareTest/static/upload     /case_file/download/node_name/api_title
            file_path = os.path.join(settings.MEDIA_ROOT_VIRTUAL, "case_file", "download", node_data.node_name)
            if not os.path.exists(file_path):
                os.makedirs(file_path)
            file_path = os.path.join(file_path, file_name)
            sheet_name = api_data.title
            wt = WriteTable(file_path, sheet_header, items, sheet_name)
            erro_msg = wt.write()
            if erro_msg:
                r_data["erro_msg"] = erro_msg
            else:
                r_data["ret"] = True
                r_data["file_path"] = os.path.join("case_file", "download", node_data.node_name, file_name)
                r_data["file_name"] = file_name

    else:
        r_data["erro_msg"] = "接口id不能为空！"
    return JsonResponse(json.dumps(r_data), safe=False)


# # 接口下所有用例数据导入表
# def dl_api_case_data2(req):
#     """
#     :param req:
#     :param file_name:
#     :return:
#     """
#
#     def file_iterator(file_name, chunk_size=512):  # 用于形成二进制数据
#         with open(file_name, 'rb') as f:
#             while True:
#                 c = f.read(chunk_size)
#                 if c:
#                     yield c
#                 else:
#                     break
#
#     file_name = req.GET.get('file_name', None)
#     if not file_name:
#         return HttpResponse("没有文件名！")
#     file_name = "ce111shi1.xls"
#     file_path = os.path.join(settings.MEDIA_ROOT, "case_file", file_name) # "测试返回本地ip地址-2019-11-08 18-42-42.xlsx"
#     file = open(file_path, 'rb')
#     # file_data = file.read()
#     response = FileResponse(file.read())
#     response['Content-Type'] = 'application/octet-stream'
#     # response['Content-Type'] = 'application/vnd.ms-excel'  # 注意格式
#     response['Content-Disposition'] = 'attachment;filename="{}"'.format(file_name)
#     # response = StreamingHttpResponse(file.read())  # 这里创建返回
#     # response['Content-Type'] = 'application/vnd.ms-excel'  # 注意格式
#     # response['Content-Disposition'] = 'attachment;filename="模板.xls"'  # 注意filename 这个是下载后的名字
#
#     return response

# 将数据写入表
class WriteTable():

    def __init__(self, file_path, sheet_header, data_list, sheet_name="init"):
        """
        :param file_path:  excel保存位置，包括路径和表的名字
        :param sheet_header:   表格头信息 格式[str,str,str,str,]
        :param data_list:      表身体信息 格式[[str,str,str,str,],[],]
        :param sheet_name:     表名，默认init
        """
        self.data_list = data_list
        self.file_path = file_path
        self.header = sheet_header

        # 写完表 要返回写表结果，是否有错误信息
        self.erro_msg = ""

        try:
            self.wbook = xlwt.Workbook(encoding='utf-8')        # 创建excel文件，声明编码
            self.wbook.add_sheet(sheet_name)                    # 创建表
            self.ws =self.wbook.get_sheet(sheet_name)          # 使用表
        except Exception as e:
            self.erro_msg = "创建表时出错：{}".format(e)

    def write(self):
        if not self.erro_msg:               # 初始化
            self.write_sheet_header()   # 写头
            if not self.erro_msg:
                self.wirte_sheet_body() # 写身体
                if not self.erro_msg:
                    self.save_table()   # 保存
        return self.erro_msg

    def save_table(self):
        # 保存
        self.wbook.save(self.file_path)

    def write_sheet_header(self):

        try:
            for colnum in range(0, len(self.header)):
                self.ws.write(0, colnum, self.header[colnum], xlwt.easyxf('font: bold on'))  # 将表头部信息写入表头:行,列,数据,字体

        except Exception as e:
            self.erro_msg = "写入数据头异常！{}".format(self.header)


    def style(self):
        # 设置字体颜色
        style = xlwt.XFStyle()  # 初始化样式
        font = xlwt.Font()  # 为样式创建字体
        # 设置字体颜色
        font.colour_index = 10
        style.font = font
        return style

    def wirte_sheet_body(self):
        # style = self.style()

        # 写入数据
        row = 1     # 从第二行开始写
        for item in self.data_list:
            # 写入数据参数
            for index, filed in enumerate(item):
                try:
                    # 调用写表方法
                    # if "异常：" in item[1]:
                    #     self.ws.write(row, index, filed, style)
                    # else:
                    self.ws.write(row, index, filed)
                except Exception as e:
                    self.erro_msg = "写入数据体异常：(第{}行{}列)：{}".format(row, index, e)
                    return
            row += 1












