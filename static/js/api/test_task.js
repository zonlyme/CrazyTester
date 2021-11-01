
// 获取测试任务列表
var get_test_task_list = function (page, page_size) {
    page = page || 1;
    page_size = page_size || 10;
    var params = {
        project_id: $("#choose_project").val(),
        page: page,
        page_size: page_size
    };
    var res_data = send_get_test_task_list(params);
    if(res_data.ret){
        set_task_list_info(res_data.data);
        page_handle(res_data.count, page, page_size)
        return res_data
    }
};

var api_tr_html = function () {
    /*
     <tr>
        <td class="line34 task_id"></td>
        <td class="line34"><div class="title width_200"></div></td>
        <td class="line34 test_type"></td>
        <td class="line34 project_title"></td>
        <td class="line34 global_env"></td>
        <td class="line34"><div class="test_content"></div></td>
        <td class="line34 cron"></td>
        <td class="line34 next_run_time"></td>
        <td class="line34">
            <div class="btn-group">
                <button type="button" class="btn btn-primary dropdown-toggle" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                    立即执行 <span class="caret"></span>
                </button>
                <ul class="dropdown-menu global_env_ul">
                </ul>
            </div>
            <button type="button" class="btn btn-success start_cron_task">开始定时任务</button>
            <button type="button" class="btn btn-warning stop_cron_task">停止定时任务</button>
            <br>
            <button type="button" class="btn btn-info">
                <a href="" class="task_report" target="_blank">执行记录</a>
            </button>
            <button type="button" class="btn btn-info task_detail">详情</button>
            <button type="button" class="btn btn-warning update_test_task">编辑</button>
            <button type="button" class="btn btn-danger delete_test_task">删除</button>
        </td>
    </tr>
     */
};

var test_content_handel = function (task_data) {

        var test_content1 = ""; // 任务列表中展示的内容
        var test_content2 = ""; // title和详情中展示的内容
        var test_content3 = ""; // 任务列表中展示的内容(用例超链接)

        if (!task_data.isValid){
            var str1 = "<span class='label label-warning'>失效!</span>   ";
            test_content2 = str1 + task_data.msg;
            test_content1 = str1 + task_data.msg;
        }
        else{
            var group_title_list = task_data.group_title_list;
            if(group_title_list){
                test_content1 += "分组: " + task_data.group_ids + "<br>";
                test_content3 += "分组: " + task_data.group_ids + "<br>";
                group_title_list = JSON.parse(group_title_list);
                for(n in group_title_list){
                    test_content2 += group_title_list[n] + "\n";
                }
            }

            var api_title_list = task_data.api_title_list;
            if(api_title_list){
                test_content1 += "接口: " + task_data.api_ids + "<br>";
                test_content3 += "接口: ";
                api_title_list = JSON.parse(api_title_list);
                for(a in api_title_list){
                    test_content2 += api_title_list[a] + "\n"
                }
            }
            if (task_data.api_ids){
                var api_id_list = new Array();
                var api_id_list = task_data.api_ids.split(","); //字符分割
                for (j in api_id_list) {
                    if (api_id_list[j]){
                        test_content3 += '<a href="/html/api/api_detail?id={0}" target="_blank">{1}</a>,'.format(api_id_list[j], api_id_list[j])
                    }
                }
            }

            var case_title_list = task_data.case_title_list;
            if(case_title_list){
                test_content1 += "用例: " + task_data.case_ids;
                test_content3 += "用例: ";
                case_title_list = JSON.parse(case_title_list);
                for(l in case_title_list){
                    test_content2 += case_title_list[l] + "\n"

                }
            }
            if (task_data.case_ids){
                var case_id_list= new Array();
                var case_id_list=task_data.case_ids.split(","); //字符分割
                for (k in case_id_list) {
                    if (case_id_list[k]){
                        test_content3 += '<a href="/html/api/api_detail?case_id={0}" target="_blank">{1}</a>,'.format(case_id_list[k], case_id_list[k])
                    }
                }
            }
        }
        return [test_content1, test_content2, test_content3]
};

// 设置任务列表信息
var set_task_list_info = function (res_data) {

    $("#test_task_info_part tbody").html("");

    if (res_data.length == 0){
        // pop_danger("无数据！")
        $("#test_task_info_part tbody").html("<span class='color_red center' style='font-size: 18px'>无数据！</span>");
        return
    }

    for(i in res_data){
        var task_id = res_data[i].id;
        var api_tr = $(api_tr_html.getMultiLine());
        api_tr.find(".task_id").html(task_id);
        api_tr.find(".title").html(res_data[i].title);
        api_tr.find(".test_type").html(res_data[i].test_type);
        api_tr.find(".next_run_time").html(res_data[i].next_run_time);
        api_tr.find(".project_title").html(res_data[i].project_title);

        var global_env_html = "";
        for (l in res_data[i].global_env){
            global_env_html += '<p style="margin: -10px 0 -10px;"><span class="label label-info" global_env_id="{0}">{1}</span></p>'.format(
                res_data[i].global_env[l].id, res_data[i].global_env[l].title
            );
        }
        api_tr.find(".global_env").html(global_env_html);

        if(res_data[i].isValid){
            var test_content = test_content_handel(res_data[i]);
            api_tr.find(".test_content").html(test_content[2]);
            api_tr.find(".test_content").attr("title", test_content[1]);
        }
        else{
            api_tr.find(".test_content").html("<span class='color_red'>{0}</span>".format(res_data[i].msg));
        }
        api_tr.find(".cron").html(res_data[i].cron);

        var global_env_ul = "";
        if (res_data[i].global_env){
            for( k in res_data[i].global_env){
                global_env_ul += '<li class="execute_task_now" global_env_id="{0}" task_id="{1}"><a>{2}</a></li>'.format(
                    res_data[i].global_env[k].id, task_id, res_data[i].global_env[k].title
                )
            }
        }
        api_tr.find(".global_env_ul").html(global_env_ul);
        api_tr.find(".start_cron_task").attr("task_id", task_id);
        api_tr.find(".stop_cron_task").attr("task_id", task_id);
        // api_tr.find(".execute_task_now").attr("task_id", task_id);
        api_tr.find(".task_report").attr("href", "/html/api/test_report_list?index_flag=1&task_id="+task_id);
        api_tr.find(".update_test_task").attr("task_id", task_id);
        api_tr.find(".task_detail").attr("task_id", task_id);
        api_tr.find(".delete_test_task").attr("task_id", task_id);

        if(res_data[i].cron_status=="1"){
            api_tr.find(".start_cron_task").attr("disabled", "disabled");
        }
        else if(res_data[i].cron_status=="2"){
            api_tr.find(".stop_cron_task").attr("disabled", "disabled");
        }

        var tr = api_tr.prop("outerHTML");
        $("#test_task_info_part tbody").append(tr);
    }
};


// 选择测试类型，加载对应数据
$("#add_test_task_panel .test_type").change(function () {
    test_task_panel_switch($(this).val(), "#add_test_task_panel")
});

$("#update_test_task_panel .test_type").change(function () {
    test_task_panel_switch($(this).val(), "#update_test_task_panel")
});

var test_task_panel_switch = function (test_type, type){

    if (test_type == "全量测试" || test_type == "冒烟测试") {
        $(type + " .group_tr").show()
        $(type + " .api_tr").show()
        $(type + " .case_tr").hide()
        // $(type + " .group_ids").removeAttr("disabled");
        // $(type + " .api_ids").removeAttr("disabled");
        // $(type + " .case_ids").attr("disabled", "disabled");
    }
    else if (test_type == "场景测试") {
        $(type + " .group_tr").hide()
        $(type + " .api_tr").hide()
        $(type + " .case_tr").show()
        // $(type + " .group_ids").attr("disabled", "disabled");
        // $(type + " .api_ids").attr("disabled", "disabled");
        // $(type + " .case_ids").removeAttr("disabled");
    }
};

// 查看测试任务详情
$("#test_task_info_part").on("click", ".task_detail", function () {
    open_zhe();
    $("#test_task_detail_panel").show();

    var params = {
        task_id: $(this).attr("task_id")
    };
    var res_data1 = send_get_test_task_detail(params);
    if(res_data1.ret){
        for(i in res_data1.data){
            $("#test_task_detail_panel ."+i).val('').val(res_data1.data[i]);
        }
        $("#test_task_detail_panel .test_content_detail").val(
            test_content_handel(res_data1.data)[1]);
        var global_env = "";
        if (res_data1.data.global_env){
            for (j in res_data1.data.global_env){
                global_env += '{0}\n'.format(res_data1.data.global_env[j].title)
            }
        }
        $("#test_task_detail_panel .global_env").val('').val(global_env);
    }

    var res_data2 = send_get_cron_info(params);
    if(res_data2.ret){
        $("#test_task_detail_panel .next_run_time").val(res_data2.next_run_time);
    }
});

// 更新测试任务
$("#test_task_info_part").on("click", ".update_test_task", function () {

    open_zhe();
    $("#update_test_task_panel").show();

    var params = {
        task_id: $(this).attr("task_id")
    };
    var res_data = send_get_test_task_detail(params);
    if(res_data.ret){

        var data = res_data.data;

        $("#update_test_task_submit").attr("task_id", data.id);

        $("#update_test_task_panel .title").val(data.title);
        $("#update_test_task_panel .test_type").val(data.test_type);
        $("#update_test_task_panel .task_desc").val(data.task_desc);
        $("#update_test_task_panel .group_ids").val(data.group_ids);
        $("#update_test_task_panel .api_ids").val(data.api_ids);
        $("#update_test_task_panel .case_ids").val(data.case_ids);
        $("#update_test_task_panel .cron").val(data.cron);

        $("#update_test_task_panel .project").val(data.project_id);

        var res_data2 = send_get_global_env({project_id: data.project_id});
        if (res_data2.ret) {

            var data2 = res_data2.data;
            if (data2.length === 0){
                $("#update_test_task_panel .global_env_checkbox").html("").html("无")
            }
            else{
                var checkbox = '';
                for (i in data2) {
                    var global_env_id_list = [];
                    if (data.global_env_id_list){
                       global_env_id_list  = data.global_env_id_list.split(",")
                    }

                    var checked = ""
                    if (global_env_id_list.includes(data2[i].id.toString())) {
                        checked = "checked"
                    }
                    checkbox += '<div><input class="global_env" type="checkbox" value="{0}" {2}><label>{1}</label></div>'.format(
                        data2[i].id, data2[i].title, checked
                    )
                }
                $("#update_test_task_panel .global_env_checkbox").html("").html(checkbox);
            }
        }


        // $("#update_test_task_panel .global_host").val(data.global_host_id);
        // $("#update_test_task_panel .global_variable").val(data.global_variable_id);
        // $("#update_test_task_panel .global_header").val(data.global_header_id);
        // $("#update_test_task_panel .global_cookie").val(data.global_cookie_id);

        $("#update_test_task_panel .workwx_user_group").val(data.workwx_user_group_id);
        $("#update_test_task_panel .workwx_group_chat").val(data.workwx_group_chat_id);
        $("#update_test_task_panel .email_user_group").val(data.email_user_group_id);

        test_task_panel_switch(data.test_type, "#update_test_task_panel")
    }


});

// 删除测试任务
$("#test_task_info_part").on("click", ".delete_test_task", function () {
    var task_id = $(this).attr("task_id");
    if (task_id) {
        var msg = "确定删除？";

        Modal.confirm(
            {
                msg: msg
            }).on(function (e) {
            // 这里是异步的，有什么操作只能写这里
            if (e) {

                var params = {
                        task_id: task_id
                    };
                var res_data = send_delete_test_task(params);
                if(res_data.ret){
                    pop_success("删除成功!");
                    close_pop_panel();
                    get_test_task_list(get_page(), get_page_size());
                }
            }
        });
    }else {
        pop_danger("未选择任务！")
    }
});

// 执行测试任务
$("#test_task_info_part").on("click", ".execute_task_now", function () {

    var global_env_id = $(this).attr("global_env_id");
    var task_id = $(this).attr("task_id");

    if (!global_env_id) {
        pop_danger("没有全局环境，请新建全局环境！")
        return
    }
    if (!task_id) {
        pop_danger("未选择任务！")
        return
    }

    var msg = "确定立即执行？";

    Modal.confirm(
        {
            msg: msg
        }).on(function (e) {
        // 这里是异步的，有什么操作只能写这里
        if (e) {
            pop_success("任务执行中...", 200);
            var params = {
                task_id: task_id,
                global_env_id: global_env_id
            };
            var url = "/api/execute_task_now";
            $.get(url, params, function (r_data) {
                if(r_data.ret){
                    var text = '<a href="' +
                        r_data.info.report_url + '" target="_blank">查看测试报告</a>';
                    pop_success("执行完成 !  "+text, 15);
                }
                else{
                    pop_danger(r_data.msg);
                }
            }).fail(function (response_data) {
                   response_pop_msg(response_data);
               });
        }
    });

});

// 添加测试任务
$("#add_test_task").click(function () {
    $("#add_test_task_panel").show();
    open_zhe();
});

$("#add_test_task_submit").click(function () {
    var params = get_test_task_panel_params("#add_test_task_panel");
    if (params) {
        var res_data = send_add_test_task(params);
        if (res_data.ret) {
            pop_success("新增成功!", 10);
            close_pop_panel();
            get_test_task_list(get_page(), get_page_size());
        }
    }
});

var get_page = function (){
    return $("#page_div").find("._active_1").text()
}
var get_page_size = function (){
    return $("#page_div").find("._sizes_select_active").text().split("条")[0]
}

$("#update_test_task_submit").click(function () {

    var task_id = $(this).attr("task_id");
    if (task_id) {
        var params = get_test_task_panel_params("#update_test_task_panel");
        params.task_id = task_id;
        if (params){
            var res_data = send_update_test_task(params);
            if(res_data.ret) {
                pop_success("更新成功!", 10);
                close_pop_panel();
                get_test_task_list(get_page(), get_page_size());
            }
        }
    }
    else{
        pop_danger("未选择任务！")
    }
});

var get_test_task_panel_params = function (panel_name) {

    var panel = $(panel_name);

    var global_env_raw = panel.find(".global_env");
    var global_env_id_list = [];
    for(i in global_env_raw){
        if(global_env_raw[i].checked)
            global_env_id_list.push(global_env_raw[i].value);
    }
    if (global_env_id_list.length === 0){
        pop_danger("请选择全局环境标签!");
        return
    }
    var params = {
        title: panel.find(".title").val(),
        task_desc: panel.find(".task_desc").val(),

        test_type: panel.find(".test_type").val(),

        global_env_id: panel.find(".global_env").val(),
        global_env_title: panel.find(".global_env").find("option:selected").text(),

        global_env_id_list: global_env_id_list.join(","),

        // global_host_id: panel.find(".global_host").val(),
        // global_variable_id: panel.find(".global_variable").val(),
        // global_header_id: panel.find(".global_header").val(),
        // global_cookie_id: panel.find(".global_cookie").val(),
        //
        // global_host_title: panel.find(".global_host").find("option:selected").text(),
        // global_variable_title: panel.find(".global_variable").find("option:selected").text(),
        // global_header_title: panel.find(".global_header").find("option:selected").text(),
        // global_cookie_title: panel.find(".global_cookie").find("option:selected").text(),

        project_id: panel.find(".project").val(),
        project_title: panel.find(".project").find("option:selected").text(),

        group_ids: panel.find(".group_ids").val(),
        api_ids: panel.find(".api_ids").val(),
        case_ids: panel.find(".case_ids").val(),

        cron: panel.find(".cron").val(),

        workwx_user_group_id: panel.find(".workwx_user_group").val(),
        workwx_user_group_title: panel.find(".workwx_user_group").find("option:selected").text(),
        workwx_group_chat_id: panel.find(".workwx_group_chat").val(),
        workwx_group_chat_title: panel.find(".workwx_group_chat").find("option:selected").text(),
        email_user_group_id: panel.find(".email_user_group").val(),
        email_user_group_title: panel.find(".email_user_group").find("option:selected").text()
    };
    if(!params.title){
        pop_danger("请输入标题!");
        return
    }
    return params

};


// 定时任务相关
$("#start_cron_program").click(function () {
    pop_success("定时程序启动中...", 200);
    var res_data = send_start_cron_program();
    if(res_data.ret){
        pop_success("启动成功!");
    }
});

$("#pause_cron_program").click(function () {
    pop_success("定时程序暂停中...", 200);
    var res_data = send_pause_cron_program();
    if(res_data.ret){
        pop_success("暂停成功!");
    }
});

$("#resume_cron_program").click(function () {
    pop_success("定时程序恢复中...", 200);
    var res_data = send_resume_cron_program();
    if(res_data.ret){
        pop_success("恢复成功!");
    }
});

$("#stop_cron_program").click(function () {
    pop_success("定时程序停止中...", 200);
    var res_data = send_stop_cron_program();
    if(res_data.ret){
        pop_success("停止成功!");
    }
});

$("#test_task_info_part").on("click", ".start_cron_task", function () {
    var button = $(this);

    var params = {
            task_id: $(this).attr("task_id")
        };

    var res_data = send_start_cron_task(params);
    if(res_data.ret){
        pop_success("定时任务开始！");
        button.attr("disabled", "disabled");
        button.parent().find(".stop_cron_task").removeAttr("disabled");
        get_test_task_list(get_page(), get_page_size());
    }
});

$("#test_task_info_part").on("click", ".stop_cron_task", function () {
    var button = $(this);
    var params = {
        task_id: $(this).attr("task_id")
    };
    var res_data = send_stop_cron_task(params);

    if(res_data.ret){
        pop_success("定时任务停止！");
        button.attr("disabled", "disabled");
        button.parent().find(".start_cron_task").removeAttr("disabled");
        get_test_task_list(get_page(), get_page_size());
    }
});

$("#get_cron_info").click(function () {
    var res_data = send_get_cron_info();
    if(res_data.ret){
        pop_success(json_stringify(res_data.tasks), 10);
    }
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
        var default_option = '<option value="">请选择</option>';
        $("#add_test_task_panel .project").html("").append(default_option + option_text);
        $("#update_test_task_panel .project").html("").append(default_option + option_text);

        var default_option2 = '<option value="">全部项目</option>';
        $("#choose_project").html("").append(default_option2 + option_text);
        if (data){
            $("#choose_project").val(data[0].id);
            get_test_task_list(1, 10);
        }
    }
};

$("#choose_project").change(function () {
    get_test_task_list(1, 10);

});




var set_global_host = function () {
    var res_data = send_get_global_host();
    if (res_data.ret) {
        var data = res_data.data;
        var option_text = '';
        for (i in data) {
            option_text += '<option value="{0}">{1}</option>'.format(data[i].id, data[i].title);
        }
        $("#add_test_task_panel .global_host").html("").html(option_text);
        $("#update_test_task_panel .global_host").html("").html(option_text);

        // $("#add_test_task_panel .global_host").val(2);
    }
};

var set_global_variable = function () {
    var res_data = send_get_global_variable();
    if (res_data.ret) {
        var data = res_data.data;
        var option_text = '';
        for (i in data) {
            option_text += '<option value="{0}">{1}</option>'.format(data[i].id, data[i].title);
        }
        $("#add_test_task_panel .global_variable").html("").html(option_text);
        $("#update_test_task_panel .global_variable").html("").html(option_text);

        // $("#add_test_task_panel .global_host").val(2)
    }
};

var set_global_header = function () {
    var res_data = send_get_global_header();
    if (res_data.ret) {
        var data = res_data.data;
        var option_text = '';
        for (i in data) {
            option_text += '<option value="{0}">{1}</option>'.format(data[i].id, data[i].title);
        }
        $("#add_test_task_panel .global_header").html("").html(option_text);
        $("#update_test_task_panel .global_header").html("").html(option_text);

        // $("#add_test_task_panel .global_host").val(2);
    }
};

var set_global_cookie = function () {
    var res_data = send_get_global_cookie();
    if (res_data.ret) {
        var data = res_data.data;
        var option_text = '';
        for (i in data) {
            option_text += '<option value="{0}">{1}</option>'.format(data[i].id, data[i].title);
        }
        $("#add_test_task_panel .global_cookie").html("").html(option_text);
        $("#update_test_task_panel .global_cookie").html("").html(option_text);
    }
};




// 设置全局环境部分
var set_global_env = function () {
    var res_data = send_get_global_env();
    if (res_data.ret) {
        var data = res_data.data;
        var option_text = '';
        for (i in data) {
            option_text += '<option value="{0}">{1}</option>'.format(data[i].id, data[i].title);
        }
        var default_option = '<option value="">请选择</option>'
        $("#add_test_task_panel .global_env").html("").html(default_option + option_text);
        $("#update_test_task_panel .global_env").html("").html(default_option + option_text);
    }
};

$(".pop_panels").on("change", ".project", function () {
    var global_env_checkbox = $(this).parent().parent().parent().find(".global_env_checkbox")

    if ($(this).val()){
        var params = {
            project_id: $(this).val()
        }
        set_global_env_tag(params, global_env_checkbox);
    }
    else{
        global_env_checkbox.html("");
    }
});

var set_global_env_tag = function (params, global_env_checkbox){
    var res_data = send_get_global_env(params);
    if (res_data.ret) {
        var data = res_data.data;
        if (data.length === 0){
            global_env_checkbox.html("").html("无")
        }
        else{
            var checkbox = '';
            for (i in data) {
                checkbox += '<div><input class="global_env" type="checkbox" value="{0}"><label>{1}</label></div>'.format(
                    data[i].id, data[i].title
                )
            }
            global_env_checkbox.html("").html(checkbox);
        }
    }
};




// 报告接收部分
var set_workwx_user_group = function () {
    var res_data = send_get_workwx_user_group();
    if (res_data.ret) {
        var data = res_data.data;
        var option_text = '';
        option_text += '<option value="">不使用</option>'
        for (i in data) {
            option_text += '<option value="{0}">{1}</option>'.format(data[i].id, data[i].title);
        }
        $("#add_test_task_panel .workwx_user_group").html("").html(option_text);
        $("#update_test_task_panel .workwx_user_group").html("").html(option_text);
    }
};

var set_workwx_group_chat = function () {
    var res_data = send_get_workwx_group_chat();
    if (res_data.ret) {
        var data = res_data.data;
        var option_text = '';
        option_text += '<option value="">不使用</option>'
        for (i in data) {
            option_text += '<option value="{0}">{1}</option>'.format(data[i].id, data[i].title);
        }
        $("#add_test_task_panel .workwx_group_chat").html("").html(option_text);
        $("#update_test_task_panel .workwx_group_chat").html("").html(option_text);
    }
};

var set_email_user_group = function () {
    var res_data = send_get_email_user_group();
    if (res_data.ret) {
        var data = res_data.data;
        var option_text = '';
        option_text += '<option value="">不使用</option>'
        for (i in data) {
            option_text += '<option value="{0}">{1}</option>'.format(data[i].id, data[i].title);
        }
        $("#add_test_task_panel .email_user_group").html("").html(option_text);
        $("#update_test_task_panel .email_user_group").html("").html(option_text);
    }
};


var page_handle = function (count, pageIndex, pageSize){
    // 重新生成分页器div，之前的不要了
    var random_pagination = "pagination" + random().toString()
    $("#page_div").html("").html('<div id="' + random_pagination + '"></div>')

    new Pagination({
	    /**
		 * layout 参数说明：
		 *
		 * total： 总条数
		 * sizes: 显示每页条数选择框， TODO:pageSizes参数必填,否则无法生效
		 * home： 首页按钮
		 * prev： 上一页按钮
		 * pager： 页码
		 * last： 尾页按钮
		 * next： 下一页按钮
		 * jumper： 输入框跳转（包含事件：失去焦点，回车）触发
		 *
		 * */
        element: '#{0}'.format(random_pagination), // 渲染的容器  [必填]
        type: 1, // 样式类型，默认1 ，目前可选 [1,2] 可自行增加样式   [非必填]
        layout: 'total, sizes, home, prev, pager, next, last, jumper', // [必填]
        pageIndex: pageIndex || 1, // 当前页码 [非必填]
        pageSize: pageSize || 5, // 每页显示条数   TODO: 默认选中sizes [非必填]
        pageCount: 9, // 页码显示数量，页码必须大于等于5的奇数，默认页码9  TODO:为了样式美观，参数只能为奇数， 否则会报错 [非必填]
        total: count, // 数据总条数 [必填]
        singlePageHide: false, // 单页隐藏， 默认true  如果为true页码少于一页则不会渲染 [非必填]
        pageSizes: [5, 10, 20, 30, 40, 50], // 选择每页条数  TODO: layout的sizes属性存在才生效
        prevText: '上一页', // 上一页文字，不传默认为箭头图标  [非必填]
        nextText: '下一页', // 下一页文字，不传默认为箭头图标 [非必填]
        ellipsis: true, // 页码显示省略符 默认false  [非必填]
        disabled: true, // 显示禁用手势 默认false  [非必填]
        currentChange: function(index, pageSize) { // 页码改变时回调  TODO:第一个参数是当前页码，第二个参数是每页显示条数数量，需使用sizes第二参数才有值。
            get_test_task_list(index, pageSize)
        }
    });
}

get_user_info();

get_all_project();

set_global_env();
// set_global_host();
// set_global_variable();
// set_global_header();
// set_global_cookie();

set_workwx_user_group();
set_workwx_group_chat();
set_email_user_group();

set_header_middle("测试任务")



