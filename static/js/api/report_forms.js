

var get_task_list = function () {
    var params = {
        "project_id": $("#choose_project").val()
    }
    var res_data = send_get_report_form_list(params);

    if(res_data.ret){
        $("#task_info_part tbody").html("");
        if (res_data.datas.length == 0){
            pop_danger("无数据！")
            $("#task_info_part tbody").html("<span class='color_red center' style='font-size: 18px'>无数据！</span>");
            return
        }
        for(i in res_data.datas){
            var rf_id = res_data.datas[i].id;
            var api_tr = $(task_tr_html.getMultiLine());
            api_tr.find(".rf_id").html(rf_id);
            api_tr.find(".title").html(res_data.datas[i].title);
            api_tr.find(".project").html(res_data.datas[i].project_title);
            api_tr.find(".env").html(res_data.datas[i].env);
            api_tr.find(".sync_type").html(res_data.datas[i].sync_type);

            api_tr.find(".execute_export_url").html(res_data.datas[i].execute_export_url);
            api_tr.find(".execute_export_method").html(res_data.datas[i].execute_export_method);
            api_tr.find(".execute_export_params").html(res_data.datas[i].execute_export_params);

            api_tr.find(".start_line").html(res_data.datas[i].start_line);
            api_tr.find(".sql").html(res_data.datas[i].sql);

            // api_tr.find(".next_run_time").html(res_data[i].next_run_time || "无");

            api_tr.find(".execute_task_now").attr("rf_id", rf_id);
            api_tr.find(".task_report").attr("rf_id", rf_id);
            api_tr.find(".task_report").attr("href", "/html/api/report_form_result?index_flag=1&rf_id="+rf_id);

            var tr = api_tr.prop("outerHTML");
            // console.log(api_tr)
            // console.log(tr)
            $("#task_info_part tbody").append(tr);
        }
    }
};

var task_tr_html = function () {
    /*
     <tr>
        <td class="line34 rf_id"></td>
        <td class="line34 title"></td>
        <td class="line34 project"></td>
        <td class="line34 env"></td>
        <td class="line34 sync_type"></td>

        <td class="line34"><div class="execute_export_url width_200"></div></td>
        <td class="line34 execute_export_method"></td>
        <td class="line34"><div class="execute_export_params width_200"></div></td>

        <td class="line34"><div class="start_line"></div></td>
        <td class="line34"><div class="sql width_200"></div></td>
        <td class="line34">
            <button type="button" class="btn btn-primary execute_task_now">立即对比</button>
            <button type="button" class="btn btn-info task_report">
                <a class="task_report" target="_blank">对比记录</a>
            </button>
        </td>
    </tr>
     */
};


$("#task_info_part").on("click", ".execute_task_now", function () {
    var rf_id = $(this).attr("rf_id");
    if (rf_id) {
        var msg = "确定立即执行？";

        Modal.confirm(
            {
                msg: msg
            }).on(function (e) {
            // 这里是异步的，有什么操作只能写这里
            if (e) {
                pop_success("任务执行中...", 200);
                var params = {
                        rf_id: rf_id
                    };
                var url = "/api/rf_verify";
                $.get(url, params, function (r_data) {
                    if(r_data.ret){
                        var s = '验证完成，验证结果：<sapn style="color:green">成功！</sapn><br>详情请查看报告。'
                        pop_success(s, 15);
                    }
                    else{
                        var s = '验证完成，验证结果：<sapn style="color:red">失败</sapn><br>错误信息：{0} <br>详情请查看报告'.format(
                            r_data.msg
                        )
                        pop_danger(s, 15);
                    }
                }).fail(function (response_data) {
                   response_pop_msg(response_data);
               });
            }
        });
    }else {
        pop_danger("未选择任务！")
    }
});

$("#choose_project").change(function () {
    get_task_list()

});

// 获取项目列表
var get_all_project = function () {
    var res_data = send_get_all_project();

    if(res_data.ret){
        var data = res_data.data;
        var option_text = '';
        for(i in data){
            option_text += '<option value="{0}">{1}</option>'.format(data[i].id, data[i].title);
        }

        var default_option2 = '<option value="">全部项目</option>';
        $("#choose_project").html("").append(default_option2 + option_text);

        get_task_list();
        // if (data){
        //     $("#choose_project").val(data[0].id);
        //
        // }
    }
};

set_header_middle("报表自动化测试对比")


get_user_info();
get_all_project();


