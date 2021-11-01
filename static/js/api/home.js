
//projects
// <img class="delete_project" src="/static/img/pub/delete.png" alt="删除">
// <img class="update_project" src="/static/img/pub/update.png" alt="重命名">
var pro_div_html = function(){
    /*
        <div class="content col-sm-3" style="margin-bottom: 10px;">
            <div class="list_head">
                <img src="/static/img/pub/atlas.png" alt="">
                <span><a class="color2 project_a" href=""></a></span>
            </div>
        </div>
    */
};

var pro_div_html2 = function(){
    /*
        <div class="content col-sm-3" id="project_mark">
            <div class="list_head">
                <button type="button" id="add_project" class="btn btn-default">新增项目</button>
                <button type="button" id="project_config" class="btn btn-default">项目配置</button>
            </div>
        </div>
    */
};

var get_all_project = function () {
    // 获取首层节点
    var res_data = send_get_all_project();
    if(res_data.ret){
        $("#projects").html("");
        var data = res_data.data;
        for(i in data){
            var pro_div = $(pro_div_html.getMultiLine());
            pro_div.find(".project_a").attr("href", "/html/api/api_dir?project_id=" + data[i].id);
            pro_div.find(".project_a").html(data[i].title);
            pro_div.find(".update_project").attr("project_id", data[i].id);
            pro_div.find(".update_project").attr("title", data[i].title);
            pro_div.find(".delete_project").attr("project_id", data[i].id);
            pro_div.find(".delete_project").attr("title", data[i].title);
            var div = pro_div.prop("outerHTML");
            $("#projects").append(div);
        }
        // $("#projects").append(pro_div_html2.getMultiLine());
        if (res_data.user_permission == "1"){
            $("#add_project").show();
            $("#project_config").show();
        }
    }
};

$("#add_project").click(function () {
    $("#add_project_panel .project_title").val("");
    $("#add_project_panel").show();
    open_zhe();
});

$("#add_project_submit").click(function () {
    var title = $("#add_project_panel .project_title").val();
    if (title) {
        var params = {
                title: title
            };
        var res_data = send_add_project(params);
        if(res_data.ret){
            pop_success("新增成功!");
            close_pop_panel();
            get_all_project();
        }
    }else {
        pop_danger("请输入目录名称!")
    }
});


$("#projects").on("click", ".delete_project", function () {

    var project_id = $(this).attr("project_id");
    if (project_id) {
        var msg = "确定删除？";

        Modal.confirm(
            {
                msg: msg
            }).on(function (e) {
            // 这里是异步的，有什么操作只能写这里
            if (e) {
                var params = {
                        id: project_id
                    };
                var res_data = send_delete_project(params);
                if(res_data.ret){
                    pop_success("删除成功!");
                    get_all_project();
                }
            }
        });
    }else {
        pop_danger("请选择项目！")
    }
});

$("#projects").on("click", ".update_project", function () {
    $("#update_project_panel .project_title").val("");
    $("#update_project_panel").show();
    open_zhe();
    $("#update_project_submit").attr("project_id", $(this).attr("project_id"));
    $("#update_project_panel .project_title").val($(this).attr("title"));
});

$("#update_project_submit").click(function () {
        var project_id = $(this).attr("project_id");
        var title = $("#update_project_panel .project_title").val();
        if (project_id && title) {
            var params = {
                id: project_id,
                title: title
            };
            var res_data = send_update_project(params);
            if(res_data.ret){
                pop_success("更新成功!");
                close_pop_panel();
                get_all_project();
            }
        }
        else {
            pop_danger("请选则项目并输入名称！")
        }
});


// 显示上传用例面板
$("#upload_case").click(function () {
    $('#upload_case_panel').show();
    open_zhe();
});

// 提交用例模板
$("#submit_upload_case").click(function () {
    var formData = new FormData();
    var case_file = document.getElementById('case_file').files[0];
    formData.append("csrfmiddlewaretoken", get_token());
    formData.append("case_file", case_file);
    var res_data = send_upload_case(formData);
    // var params = {
    //     csrfmiddlewaretoken: get_token(),
    //     case_file: document.getElementById('case_file').files[0]
    // };
    // var res_data = send_upload_case(params);
    if (res_data.ret){
        var msg = "{0}<br>新增用例:{1}<br>更新用例:{2}".format(
            res_data.msg, res_data.add_case_count, res_data.update_case_count);
        pop_success(msg, 10);
    }
    close_pop_panel();
});

set_header_middle("项目列表")

get_user_info();

get_all_project();



