import sys
import xlwt
from .view_basic import *
from .view_other_fun import excel_handle

"""
    解析全国各省份执照二维码
"""

# url2 = "http://httpbin.org/post"
MAX_WORKERS = 16
h = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.25 Safari/537.36 Core/1.70.3719.400 QQBrowser/10.5.3715.400',
    'origin': 'https://cli.im',
    'accept-language': 'zh-CN,zh;q=0.9',
    'accept': '*/*',
    'accept-encoding': 'gzip, deflate, br',
    'referer': 'https://cli.im/deqr'
}

c_path = sys.path[0]


# 获取图片绝对路径
def get_img_path(img_name):
    return os.path.join(c_path, img_name)


# 使用草料接口获取远程图片路径
def get_caoliao_img_path(img_path):
    url = "https://upload.api.cli.im/upload.php?kid=cliim"

    # print("img path ", img_path)
    files = {"Filedata":open(img_path, "rb")}
    res = requests.post(url, headers=h, files=files)
    try:
        return [1, res.json()["data"]["path"]]
    except:
        try:
            return [0, "异常：" + res.json()["info"]]
        except:
            return [0, "异常：上传图片失败！{}".format(res.text)]


# 使用远程图片解析图片
def parse_img(img_path):
    url = "https://cli.im/apis/up/deqrimg"

    img_url = get_caoliao_img_path(img_path)
    if img_url[0]:
        data = {'img': img_url}
        res = requests.post(url, data=data, headers=h)
        try:
            content = res.json()["info"]["data"][0]
            return content
        except:
            return "异常：解析图片内容失败！{}".format(res.text)
    else:
        return img_url[1]


def start_parse_img(img_path, title, all_data):
    # print(img_path)
    content = parse_img(img_path)       # 单线程方式
    item = [title, content]
    all_data.append(item)


# 调用本地图片，并发送获取响应结果
def get_img(file_dir):
    futures = Futures(MAX_WORKERS)  # 创建线程池，限定最大线程数量
    all_data = []
    # 获取当前目录下文件夹 1.当前目录路径 2.当前路径下所有子目录 3.当前路径下所有非目录子文件
    fodler_list = list(os.walk(file_dir))[0][1]
    for fodler_name in fodler_list:
        if fodler_name == "report":
            continue
        img_list = list(os.walk(os.path.join(file_dir, fodler_name)))[0][2]
        # print(img_list)
        for img_name in img_list:

            img_path = os.path.join(file_dir, fodler_name, img_name)
            title = fodler_name + " - " + img_name
            futures.submit(start_parse_img, img_path, title, all_data)  # 多线程方式

    futures.as_completed()  # 全部请求发送完毕，并处理完成后才能进行下一步

    return all_data


# 将数据写入表
class WriteTable():

    def __init__(self, data_list, file_path):
        self.data_list = data_list
        self.file_path = file_path
        nowTime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # 现在时间
        self.newTable1 = "{}.xls".format(nowTime.replace(":", "-"))  # 表格名称
        self.newTable2 = "{}.xls".format(nowTime.replace(":", "-") + "(2)")  # 表格名称
        self.newTable1 = os.path.join(self.file_path, self.newTable1)
        self.newTable2 = os.path.join(self.file_path, self.newTable2)

    def start(self):
        return self.open_table()

    def open_table(self):

        self.sheet_name1 = "init"                   # 表名

        self.wbook = xlwt.Workbook(encoding='utf-8')        # 创建excel文件，声明编码
        self.wbook.add_sheet(self.sheet_name1)              # 创建表
        self.ws1 =self.wbook.get_sheet(self.sheet_name1)    # 使用表

        headData1 = ['目录名字', '接口名字', '接口描述', '请求方式', '请求地址', '用例名字', '用例描述', 'headers', '入参', '断言信息']  # 表头部信息
        for colnum in range(0, len(headData1)):
            self.ws1.write(0, colnum, headData1[colnum], xlwt.easyxf('font: bold on'))  # 将表头部信息写入表头:行,列,数据,字体

        self.wbook2 = xlwt.Workbook(encoding='utf-8')        # 创建excel文件，声明编码
        self.wbook2.add_sheet(self.sheet_name1)              # 创建表
        self.ws2 =self.wbook2.get_sheet(self.sheet_name1)    # 使用表

        headData1 = ['路径', '识别内容']  # 表头部信息
        for colnum in range(0, len(headData1)):
            self.ws2.write(0, colnum, headData1[colnum], xlwt.easyxf('font: bold on'))  # 将表头部信息写入表头:行,列,数据,字体

        # 调用写入表的方法
        return self.wirte_sheet()

    def wirte_sheet(self):
        # 设置字体颜色
        style = xlwt.XFStyle()  # 初始化样式
        font = xlwt.Font()  # 为样式创建字体
        # 设置字体颜色
        font.colour_index = 10
        style.font = font

        # 写入数据
        print("数据写入表格1...")
        row = 1     # 从第二行开始写
        data_tm = ['电子营业执照', '根据二维码内容获取执照信息（全国）', '', 'post', '/distinguish/businessLicense',
                   '用例名字', '', '', '入参', '']
        for item in self.data_list:
            data = data_tm
            data[5] = item[0]
            data[8] = json.dumps({"qrCodeContent":item[1]}, indent=4, ensure_ascii=False)

            # 写入数据参数
            for index, filed in enumerate(data):
                try:
                    # 调用写表方法
                    if "异常：" in item[1]:
                        self.ws1.write(row, index, filed, style)
                    else:
                        self.ws1.write(row, index, filed)
                except Exception as e:
                    print("异常：({}：{})：{}".format(row, index, e))
            row += 1
        print("写入表1完成...")

        # 保存
        self.wbook.save(self.newTable1)

        # 写入数据
        print("数据写入表格2...")
        row = 1     # 从第二行开始写
        except_count = 0
        for item in self.data_list:

            # 写入数据参数
            for index, filed in enumerate(item):
                try:
                    # 调用写表方法
                    if "异常：" in item[1]:
                        except_count += 1
                        self.ws2.write(row, index, filed, style)
                    else:
                        self.ws2.write(row, index, filed)
                except Exception as e:
                    print("异常：({}：{})：{}".format(row, index, e))
            row += 1

        # 保存
        self.wbook2.save(self.newTable2)

        flag = False if except_count else True      # 有异常则flase，无异常True
        ret = "写入表完成, 总共识别：{}， 异常：{}".format(len(self.data_list), int(except_count/2))
        if not flag:
            ret = ret + "\n异常详情请查看：{}".format(self.newTable2)
        print(ret)

        return [ret, flag, self.newTable1]


def start(file_path):
    all_data = get_img(file_path)
    report_path = os.path.join(file_path, "report")
    w = WriteTable(all_data, report_path)
    ret = w.start()
    return ret


# 识别全国二维码执照主函数
def license_recognit(req):
    user = verify_user(req)
    if not user:
        return HttpResponse("未登陆或者用户名密码错误！")
    file_path = os.path.join(settings.MEDIA_ROOT, "全国营业执照")
    ret = start(file_path)  # [识别结果统计信息, 是否有异常]
    # 没有异常，将表导入库中
    if ret[1]:
        ret_msg = excel_handle(ret[2])
        return HttpResponse(ret[0] + "\n" + ret_msg)

    # 有异常返回识别统计信息
    return HttpResponse(ret[0])


if __name__ == '__main__':
    # img_path = get_img_path("2016.png")
    # img_path = "/home/python/Desktop/0b928698f64052d31b027283e315b3c0bc190026-1200.jpg"

    # content = parth_img(get_caoliao_img_path(img_path))
    # print(content)
    ret = start("./")
    # ret = start("../../新建文件夹/新建文件夹/")
    # ret = start("C:/资料/中数智汇/电子营业执照项目/新建文件夹/新建文件夹/")
    print(ret[0])


