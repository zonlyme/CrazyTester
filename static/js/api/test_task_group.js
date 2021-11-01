

var get_task_group_list = function () {
    var params = {
        project_id: $("#choose_project").val()
    };
    console.log(params)
    var res_data = send_get_task_group_list(params);

    if(res_data.ret){
        set_task_group_list_info(res_data.data);
    }
};

var task_group_tr_html = function () {
    /*
     <tr>
        <td class="line34 task_group_id"></td>
        <td class="line34"><div class="title width_200"></div></td>
        <td class="line34"><div class="task_group_desc width_200"></div></td>
        <td class="line34"><div class="content"></div></td>
        <td class="line34 cron"></td>
        <td class="line34 next_run_time"></td>
        <td class="line34">
            <button type="button" class="btn btn-primary execute_task_group_now">立即执行</button>
            <button type="button" class="btn btn-success start_cron_task_group">开始定时任务</button>
            <button type="button" class="btn btn-info stop_cron_task_group">停止定时任务</button>
            <button type="button" class="btn btn-warning update_task_group">编辑</button>
            <button type="button" class="btn btn-danger delete_task_group">删除</button>
            <button type="button" class="btn btn-info">
                <a class="task_report" target="_blank">执行记录</a>
            </button>
        </td>
    </tr>
     */
};

var set_task_group_list_info = function (res_data) {
    $("#task_group_info_part tbody").html("");
    if (res_data.length == 0){
        pop_danger("无数据！")
        $("#task_group_info_part tbody").html("<span class='color_red center' style='font-size: 18px'>无数据！</span>");
        return
    }
    for(i in res_data){
        var task_group_id = res_data[i].id;
        var api_tr = $(task_group_tr_html.getMultiLine());
        api_tr.find(".task_group_id").html(task_group_id);
        api_tr.find(".title").html(res_data[i].title);
        api_tr.find(".task_group_desc").html(res_data[i].desc);
        api_tr.find(".next_run_time").html(res_data[i].next_run_time || "无");

        if(res_data[i].isValid){
            var content = "";
            var content1 = "";
            for(j in res_data[i].content){
                content += "{0} -- {1}\n".format(res_data[i].content[j].id, res_data[i].content[j].title)
                content1 += "{0} -- {1}<br>".format(res_data[i].content[j].id, res_data[i].content[j].title)
            }
            api_tr.find(".content").html(res_data[i].test_task_id_list);
            api_tr.find(".content").attr("title", content);
        }
        else{
            api_tr.find(".content").html("<span class='color_red'>{0}</span>".format(res_data[i].erro_msg));
        }
        api_tr.find(".cron").html(res_data[i].cron);

        api_tr.find(".start_cron_task_group").attr("task_group_id", task_group_id);
        api_tr.find(".stop_cron_task_group").attr("task_group_id", task_group_id);
        api_tr.find(".execute_task_group_now").attr("task_group_id", task_group_id);
        api_tr.find(".update_task_group").attr("task_group_id", task_group_id);
        api_tr.find(".delete_task_group").attr("task_group_id", task_group_id);
        api_tr.find(".task_report").attr("href", "/html/api/test_report_list?index_flag=1&task_group_id="+task_group_id);

        if(res_data[i].cron_status == "1"){
            api_tr.find(".start_cron_task_group").attr("disabled", "disabled");
        }
        else if(res_data[i].cron_status == "2"){
            api_tr.find(".stop_cron_task_group").attr("disabled", "disabled");
        }

        var tr = api_tr.prop("outerHTML");
        $("#task_group_info_part tbody").append(tr);
    }
};

$("#add_test_task_group").click(function () {
    $("#add_task_group_panel").show();
    open_zhe();
});

$("#add_task_group_submit").click(function () {
    var params = get_task_group_panel_params("#add_task_group_panel");
    if (params) {
        var res_data = send_add_task_group(params);
        if (res_data.ret) {
            pop_success("新增成功!", 10);
            close_pop_panel();
            get_task_group_list();
        }
    }
});

$("#update_task_group_submit").click(function () {

    var task_group_id = $(this).attr("task_group_id");
    if (task_group_id) {
        var params = get_task_group_panel_params("#update_task_group_panel");
        params.task_group_id = task_group_id;

        if (params){
            var res_data = send_update_task_group(params);
            if(res_data.ret) {
                pop_success("更新成功!", 10);
                close_pop_panel();
                get_task_group_list();
            }
        }
    }
    else{
        pop_danger("未选择任务！")
    }
});

var get_task_group_panel_params = function (panel_name) {

    var panel = $(panel_name);
    var params = {
        title: panel.find(".title").val(),
        desc: panel.find(".desc").val(),
        project_id: panel.find(".project").val(),
        project_title: panel.find(".project").find("option:selected").text(),
        test_task_id_list: panel.find(".test_task_id_list").val(),
        cron: panel.find(".cron").val()
    };

    if(!params.title){
        pop_danger("请输入标题!");
        return
    }
    if(!params.project_id){
        pop_danger("请选择所属项目!");
        return
    }
    if(!params.test_task_id_list){
        pop_danger("请输入任务id!");
        return
    }
    return params

};


$("#task_group_info_part").on("click", ".update_task_group", function () {

    open_zhe();
    $("#update_task_group_panel").show();
    var params = {
        task_group_id: $(this).attr("task_group_id")
    };
    var res_data = send_get_task_group_detail(params);
    if(res_data.ret){
        var data = res_data.data;
        $("#update_task_group_submit").attr("task_group_id", data.id);
        $("#update_task_group_panel .title").val("").val(data.title);
        $("#update_task_group_panel .desc").val("").val(data.desc);
        $("#update_task_group_panel .project").val(data.project_id);
        $("#update_task_group_panel .test_task_id_list").val("").val(data.test_task_id_list);
        $("#update_task_group_panel .cron").val("").val(data.cron);
    }


});

$("#task_group_info_part").on("click", ".delete_task_group", function () {
    var task_group_id = $(this).attr("task_group_id");
    console.log(111, task_group_id)
    if (task_group_id) {
        var msg = "确定删除？";

        Modal.confirm(
            {
                msg: msg
            }).on(function (e) {
            // 这里是异步的，有什么操作只能写这里
            if (e) {
                var params = {
                        task_group_id: task_group_id
                    };
                var res_data = send_delete_task_group(params);
                if(res_data.ret){
                    pop_success("删除成功!");
                    close_pop_panel();
                    get_task_group_list();
                }
            }
        });
    }else {
        pop_danger("未选择任务！")
    }
});

$("#task_group_info_part").on("click", ".execute_task_group_now", function () {
    var task_group_id = $(this).attr("task_group_id");
    if (task_group_id) {
        var msg = "确定立即执行？";

        Modal.confirm(
            {
                msg: msg
            }).on(function (e) {
            // 这里是异步的，有什么操作只能写这里
            if (e) {
                pop_success("任务组执行中...", 200);
                var params = {
                        task_group_id: task_group_id
                    };
                var url = "/api/execute_task_group_now";
                $.get(url, params, function (r_data) {
                    if(r_data.ret){
                        pop_success("执行完成 !", 15);
                    }
                    else{
                        pop_danger(r_data.msg);
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

$("#task_group_info_part").on("click", ".start_cron_task_group", function () {
    var button = $(this);

    var params = {
            task_group_id: $(this).attr("task_group_id")
        };

    var res_data = send_start_cron_task_group(params);
    if(res_data.ret){
        pop_success("定时任务开始！");
        // button.attr("disabled", "disabled");
        // button.parent().find(".stop_cron_task_group").removeAttr("disabled");
        get_task_group_list();
    }
});

$("#task_group_info_part").on("click", ".stop_cron_task_group", function () {
    var button = $(this);
    var params = {
        task_group_id: $(this).attr("task_group_id")
    };
    var res_data = send_stop_cron_task_group(params);

    if(res_data.ret){
        pop_success("定时任务已停止！");
        // button.attr("disabled", "disabled");
        // button.parent().find(".start_cron_task_group").removeAttr("disabled");
        get_task_group_list();
    }
});

var get_all_project = function () {
    var res_data = send_get_all_project();

    if(res_data.ret){
        var data = res_data.data;
        var option_text = '';
        for(i in data){
            option_text += '<option value="{0}">{1}</option>'.format(data[i].id, data[i].title);
        }
        var default_option = '<option value="">请选择</option>';
        $("#add_task_group_panel .project").html("").append(default_option + option_text);
        $("#update_task_group_panel .project").html("").append(default_option + option_text);

        var default_option2 = '<option value="">全部项目</option>';
        $("#choose_project").html("").append(default_option2 + option_text);

        if (data){
            $("#choose_project").val(data[0].id);
            get_task_group_list();
        }
    }
};

$("#choose_project").change(function () {
    get_task_group_list();
});



get_user_info();
get_all_project();
// get_task_group_list();

set_header_middle("测试任务组")


