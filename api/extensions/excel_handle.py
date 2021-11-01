import xlrd
import xlwt
import json
from django.conf import settings


def excel_handle(file_path):
    try:
        rbook = xlrd.open_workbook(file_path)
    except xlrd.biffh.XLRDError:
        return "不支持的格式"
    except Exception as e:
        return "xlrd打开文件异常".format(e)
    table = rbook.sheets()[0]  # 表示获取第一个表格

    nrows = table.nrows  # 有效行数

    for row in range(11):
        for col in range(1, nrows):
            try:
                if row == 2 or row == 6 or row == 10:
                    continue
                elif row == 7:
                    try:
                        json.loads(table.cell_value(col, row))
                    except:
                        # print("{},{}不是json格式！".format(row + 1, col + 1))
                        return "{},{}不是json格式！".format(row + 1, col + 1)
                elif str(table.cell_value(col, row)).strip() == "":

                    return "{},{}不能为空：{}".format(row + 1, col + 1, format(table.cell_value(col, row)))
            except:
                print("异常：" + "{},{}不能为空：{}".format(row, col, format(table.cell_value(col, row))))
    else:
        for row in range(1, nrows):  # 从第二行开始遍历
            item = {}
            item["node_name"] = str(table.cell_value(row, 0))

            item["api_title"] = str(table.cell_value(row, 1))
            item["api_desc"] = str(table.cell_value(row, 2))
            item["method"] = str(table.cell_value(row, 3))
            item["url"] = str(table.cell_value(row, 4))

            item["case_title"] = str(table.cell_value(row, 5))
            item["case_desc"] = str(table.cell_value(row, 6))
            item["params"] = str(table.cell_value(row, 7))
            item["verify_key"] = str(table.cell_value(row, 8))
            item["verify_method"] = str(int(table.cell_value(row, 9)))
            shi = table.cell_value(row, 10)
            if type(shi) == float:
                if int(shi) == shi:
                    shi = str(int(shi))
            else:
                shi = str(shi)
            item["verify_expect_ret"] = shi

            # excel_insert_db_handle(item)

        return "导入数据库成功！"


# 将数据写入表
class WriteTable:

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
        self.msg = ""

        try:
            self.wbook = xlwt.Workbook(encoding='utf-8')        # 创建excel文件，声明编码
            self.wbook.add_sheet(sheet_name)                    # 创建表
            self.ws =self.wbook.get_sheet(sheet_name)          # 使用表
        except Exception as e:
            self.msg = "创建表时出错：{}".format(e)

    def write(self):
        if not self.msg:               # 初始化
            self.write_sheet_header()   # 写头
            if not self.msg:
                self.wirte_sheet_body()     # 写身体
                if not self.msg:
                    self.save_table()   # 保存
        return self.msg

    def save_table(self):
        # 保存
        self.wbook.save(self.file_path)

    def write_sheet_header(self):

        try:
            for colnum in range(0, len(self.header)):
                self.ws.write(0, colnum, self.header[colnum], xlwt.easyxf('font: bold on'))  # 将表头部信息写入表头:行,列,数据,字体

        except Exception as e:
            self.msg = "写入数据头异常！{}".format(self.header)

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
        font = xlwt.Font()
        font.underline = True   # 下划线
        font.colour_index = 4   # 蓝色字体
        style0 = xlwt.XFStyle()
        style0.font = font

        # 写入数据
        row = 1     # 从第二行开始写
        for item in self.data_list:
            # 写入数据参数
            for index, value in enumerate(item):
                try:
                    # 用例id添加超链接
                    if index == 6:
                        # self.ws.write(row, index, filed, style)
                        self.ws.write(row, index, xlwt.Formula(
                            'HYPERLINK("{}/html/api/api_detail?case_id={}"; "{}")'.format(
                                settings.IP, value, "链接")), style0)
                    else:
                        self.ws.write(row, index, value)
                except Exception as e:
                    self.msg = "写入数据体异常：(第{}行{}列)：{}".format(row, index, e)
                    return
            row += 1


if __name__ == '__main__':
    pass
    # print(excel_handle("/home/python/Desktop/SoftwareTest/static/upload/全国营业执照/2019-08-12 17-40-47.xls"))
