from .view_basic import *

def report(req):
    """
        :param req:
        :return: 返回空的页面，通过页面的js发起获取数据请求
    """

    return render(req, 'interface/test_report.html')


def report2(req):
    """
        :param req:
        :return: 返回空的页面，通过页面的js发起获取数据请求
    """

    return render(req, 'interface/test_report2.html')


def get_report_data(req, id):
    """
        :param req:
        :param id: 根据报告id返回此条报告数据
        :return:
        id, title,tester, c_date
        nav_tree,
    """
    r_data = {}
    try:
        testreport = TestReport.m.get(id=id)
        dict_testreport = model_to_dict(testreport)
    except Exception as e:
        r_data["erro_msg"] = "获取报告信息出错：{}".format(e)
        r_data["ret"] = False
    else:
        try:
            dict_testreport["report"] = json.loads(dict_testreport["report"])
        except Exception as e:
            r_data["erro_msg"] = "报告数据转换字典格式出错：{}".format(e)
            r_data["ret"] = False
        else:
            report_tree = get_report_tree(dict_testreport)
            r_data["ret"] = True
            r_data["report_tree"] = json.dumps(report_tree)
            dict_testreport["c_date"] = str(testreport.c_date)[:19]# 2019-05-29 07:16:44+00:00 ==> 2019-05-29 07:16:44
            r_data.update(dict(dict_testreport))

    return JsonResponse(json.dumps(r_data), safe=False)


# 获取测试报告的左侧导航tree
def get_report_tree(dict_testreport):
    report_tree = []
    for api in dict_testreport["report"]["api_list"]:
        api_text = "<span class='api' value='{}'>{}</span>".format(api["id"], api["title"])
        api_item = {
            "text": api_text,
            "nodes": [],
        }
        assert_fail = 0
        for case in api["case_list"]:
            case_item = {}
            if not case["asserts_flag"]:
                assert_fail += 1
                # case_item["text"] = "<span class='case' value='{}' api_id='{}' style='color:red'>{}</span>".format(
                #     case["id"], api["id"],case["title"])
                case_item["tags"] = ["fail"]
            # else:
            case_item["text"] = "<span class='case' value='{}'>{}</span>".format(
                case["report_detail_id"], case["title"])

            api_item["nodes"].append(case_item)
        if assert_fail:
            api_item["tags"] = [str(assert_fail)]
        report_tree.append(api_item)
    return report_tree


def get_case_detail(req):
    """
    根据task_id,api_id,查找对应批次中对应api的所有失败的用例的数据
    :param req:
    :return:
    """
    r_data = {}

    task_id = req.GET.get('task_id', None)
    api_id = req.GET.get('api_id', None)

    if not task_id or not api_id:
        r_data["erro_msg"] = "没有此数据!"
        r_data["ret"] = False
        return JsonResponse(json.dumps(r_data), safe=False)

    try:
        datas = TestReportDetail.m.filter(task_id=task_id, api_id=api_id, final_ret=False)
        datas2 = []
        for data in datas:
            datas2.append(data.case_info)
    except Exception as e:
        r_data["erro_msg"] = "获取数据出错：{}".format(e)
        r_data["ret"] = False
    else:
        r_data["ret"] = True
        r_data["datas"] = datas2
        return JsonResponse(json.dumps(r_data), safe=False)


def get_report_detail(req):
    r_data = {}

    report_detail_id = req.GET.get('report_detail_id', None)

    if not report_detail_id:
        r_data["erro_msg"] = "没有此数据!"
        r_data["ret"] = False
        return JsonResponse(json.dumps(r_data), safe=False)

    try:
        data = TestReportDetail.m.get(id=report_detail_id)
        data = model_to_dict(data)
    except Exception as e:
        r_data["erro_msg"] = "获取数据出错：{}".format(e)
        r_data["ret"] = False
    else:
        r_data["ret"] = True
        r_data["case_info"] = data["case_info"]
        return JsonResponse(json.dumps(r_data), safe=False)

def get_all_report(req):
    """
    :param req:
    :return: 返回最后五十条报告
    """
    r_data = []
    test_report = TestReport.m.filter().order_by('-id')[:50]
    for i in test_report:
        r_data.append(model_to_dict(i, ["id", "title"]))

    return JsonResponse(json.dumps(r_data), safe=False)

