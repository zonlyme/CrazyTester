import xlrd
import json

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
                print("异常123：" + "{},{}不能为空：{}".format(row, col, format(table.cell_value(col, row))))
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

            print(item)

            # excel_insert_db_handle(item)

        return "导入数据库成功！"

print(excel_handle("/home/python/Desktop/SoftwareTest/static/upload/全国营业执照/2019-08-12 17-40-47.xls"))

