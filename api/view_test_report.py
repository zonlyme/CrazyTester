from api.view_basic import *


@require_http_methods(["GET"])
@login_required
def get_report_list(req):

    task_id = req.GET.get("task_id", "")
    task_group_id = req.GET.get("task_group_id", "")
    data = []
    filter_item = {}
    if task_id:
        filter_item["task_id"] = task_id
    if task_group_id:
        filter_item["task_group_id"] = task_group_id
    try:
        test_report = TestReport.m.filter(**filter_item).order_by('-c_date')[:100]

        for i in test_report:
            item = model_to_dict(i, exclude=["report", "isDelete"])
            item["c_date"] = i.c_date.strftime('%Y-%m-%d %H:%M:%S')
            data.append(item)
    except Exception as e:
        return response_400("出错了:{}".format(e))

    return response_200(data=data)


@require_http_methods(["GET"])
@login_required
def get_report_data(req):

    id = req.GET.get("id", "")
    if not id:
        return response_400("缺少参数id")

    try:
        testreport = TestReport.m.get(id=id)
    except:
        return response_400("不存在的报告数据")

    try:
        data = model_to_dict(testreport)
        data["c_date"] = testreport.c_date.strftime('%Y-%m-%d %H:%M:%S')
        data["report"] = json.loads(data["report"]) if data["report"] else ""

        # report_tree = get_report_tree(dict_testreport)
        # r_data["report_tree"] = json_dumps(report_tree)

        return response_200(data=data)

    except Exception as e:
        return response_400("报告{}数据转换字典格式出错：{}".format(id, e))


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


@require_http_methods(["GET"])
@login_required
def get_case_detail(req):
    """
    report_detail_id: 有report_detail_id表示场景测试，查询单个报告数据
    根据task_id,api_id,查找对应批次中对应api的所有失败的用例的数据
    """

    report_detail_id = req.GET.get('report_detail_id', None)
    report_id = req.GET.get('report_id', None)
    api_id = req.GET.get('api_id', None)

    if report_detail_id is not None:
        try:
            data_raw = TestReportDetail.m.get(id=report_detail_id)
        except:
            return response_400("不存在的报告！")

        data = {
            "case_id": data_raw.case_id,
            "case_title": data_raw.case_title,
            "case_info": json.loads(data_raw.case_info)
        }

        return response_200(data=data)

    else:
        if not report_id or not api_id:
            return response_400("缺少参数！report_id or api_id!")

        try:
            datas_raw = TestReportDetail.m.filter(report_id=report_id, api_id=api_id)
        except Exception as e:
            return response_400("获取数据出错：{}".format(e))

        datass = []
        for data in datas_raw:
            item = {
                "case_id": data.case_id,
                "case_title": data.case_title,
                "case_info": json.loads(data.case_info)
            }
            datass.append(item)

        return response_200(datas=datass)


@require_http_methods(["GET"])
def get_report_detail(req):

    report_detail_id = req.GET.get('report_detail_id', None)

    if not report_detail_id:
        return response_400("缺少参数：report_detail_id！")

    try:
        data = TestReportDetail.m.get(id=report_detail_id)
    except:
        return response_400("没有此数据！")
    else:
        return response_200(case_info=data.case_info)


@require_http_methods(["GET"])
def get_all_report(req):
    """
    :param req:
    :return: 返回最后五十条报告
    """
    data = []
    test_report = TestReport.m.filter().order_by('-id')[:50]
    for i in test_report:
        data.append(model_to_dict(i, ["id", "title"]))

    return response_200(data=data)

