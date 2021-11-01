
var get_all_group = function () {
    // 获取首层节点
    var params = {id:get_project_id()};
    var res_data = send_get_all_group(params);
    if(res_data.ret) {
        // parent.window.frames["iframe_html"].func();
        // parent.window.frames["iframe_html"].document.getElementById('header_middle').innerHTML = res_data.pro_title;
        // top.window.frames[2].document.getElementById('兄弟页面3中的元素ID');
        top.window.document.getElementById('header_middle').innerHTML = res_data.pro_title;
        // $("#header_middle").html("").append(res_data.pro_title);
        $("title").html("项目:" + res_data.pro_title);

        var data = res_data.data;
        var group_json = [];
        for (i in data) {
            var group_item = {
                text: "<span class='group' value='" + data[i].id + "'>" + data[i].id + " -- " + data[i].title + "</span>",
                tags: [data[i].case_count]
            };
            group_json.push(group_item)
        }
        group_json = json_stringify(group_json);

        $('#treeview').treeview({
            // enableLinks:true,
            // tree节点的字体颜色
            color: "#428bca",
            // tree节点左侧的展开图标，折叠的图标，节点的图标
            //	expandIcon: "glyphicon glyphicon-stop",
            //	collapseIcon: "glyphicon glyphicon-unchecked",
            //	groupIcon: "glyphicon glyphicon-user",
            // 是否显示标签
            showTags: true,
            // tree中的数据
            data: group_json,
            // 这里设置tree的展开层级l
            levels: 1,
            // tree 的节点背景颜色
            //  backColor:'aqua',
            onNodeSelected: function (event, data) {
                var api_id = $(data.text).attr("value");
                console.log(1111, api_id);
                get_apis_for_group(api_id)
            }
        });
        $('#treeview').treeview('selectNode', [0, {silent: true}]);


        $("#update_group_select").html("").append("<option value=''>请选择</option>");
        $("#delete_group_select").html("").append("<option value=''>请选择</option>");
        $("#ownload_group_select").html("").append("<option value=''>请选择</option>");
        $("#group_select").html("").append("<option value=''>请选择</option>");

        if (data.length > 0){
            $.each(data, function (index, item) {
                $("#update_group_select").append("<option value='" + item.id + "'>" + item.title + "</option>")
                $("#delete_group_select").append("<option value='" + item.id + "'>" + item.title + "</option>")
                $("#download_group_select").append("<option value='" + item.id + "'>" + item.title + "</option>")
                $("#group_select").append("<option value='{0}'>{1}</option>".format(item.id, item.title))

            });

            get_apis_for_group(data[0].id);
        }
    }
};

var api_tr_html = function () {
    /*
     <tr>
        <td width="4%" class="line34"><span class="label label-info api_id"></span></td>
        <td width="8%" class="line34"><span class="label label-info api_method"></span></td>
        <td width="8%" class="line34"><span class="label label-info case_count"></span></td>
        <td width="16%" class="api_title line34"></td>
        <td width="35%" class="api_desc line34"></td>
        <td width="29%" class="api_operation line34">
            <button type="button" class="btn btn-warning update_api">编辑</button>
            <button type="button" class="btn btn-danger delete_api">删除</button>
            <button type="button" class="btn btn-info dl_api">下载接口用例</button>
        </td>
    </tr>
     */
};

var get_apis_for_group = function (group_id) {
    var params = {group_id: group_id};
    var res_data = send_get_api_list(params);

    if (res_data.ret)

        $("#add_api").attr("group_id", group_id);
        $("#apis_part tbody").html("");
        $("#apis_part thead").html("");
        $("#apis_part_header thead").html("");

        var th_html = '<tr class="bg_color1">'+
                    '<td class="" width="4%">id</td>'+
                    '<td class="" width="8%">请求方式</td>'+
                    '<td class="" width="8%">用例数量</td>'+
                    '<td class="" width="16%">标题</td>'+
                    '<td class="" width="35%">描述</td>'+
                    '<td class="" width="29%">操作</td>'+
                '</tr>';
        $("#apis_part_header thead").append(th_html);

        var datas = res_data.datas;
        for(i in datas){
            // title = '<a href="/html/api/api_detail?api_id='+datas[i].id+'">'+datas[i].title+'</a>';
            var title = '<a href="/html/api/api_detail?api_id={0}&index_flag=1" target="_blank">{1}</a>'.format(
                datas[i].id, datas[i].title
            );
            // title = '<a href="/html/api/api_detail?api_id='+datas[i].id+'" target="_blank">'+datas[i].title+'</a>';
            api_tr = $(api_tr_html.getMultiLine());
            api_tr.find(".api_id").html(datas[i].id);
            api_tr.find(".api_method").html(datas[i].method);
            api_tr.find(".api_title").html(title);
            api_tr.find(".api_desc").html(datas[i].desc);
            api_tr.find(".case_count").html(datas[i].case_count);
            api_tr.find(".update_api").attr("api_id", datas[i].id);
            api_tr.find(".update_api").attr("method", datas[i].method);
            api_tr.find(".update_api").attr("api_title", datas[i].title);
            api_tr.find(".update_api").attr("api_desc", datas[i].desc);
            api_tr.find(".delete_api").attr("api_id", datas[i].id);
            api_tr.find(".dl_api").attr("api_id", datas[i].id);
            tr = api_tr.prop("outerHTML");
            $("#apis_part tbody").append(tr);
        }
};


var get_project_id = function () {

    // var project_id = getUrlQueryString("project_id");
    // $("#project_id").attr("project_id", project_id);
    // var project_id = $("#project_id").attr("project_id");
    return getUrlQueryString("project_id")
};

$("#add_group_button").click(function () {
    open_zhe();
    $("#add_group_panel").show();
    $("#add_group_title").val("");
});

$("#update_group_button").click(function () {
    open_zhe();
    $("#update_group_panel").show();
    $("#update_group_title").val("");
});

$("#delete_group_button").click(function () {
    open_zhe();
    $("#delete_group_panel").show();
});

$("#delete_group").click(function () {
    var group_id = $("#delete_group_select").val();
    if (group_id) {
        msg = "确定删除？";

        Modal.confirm(
            {
                msg: msg
            }).on(function (e) {
            // 这里是异步的，有什么操作只能写这里
            if (e) {
                params = {
                    id: group_id
                };
                var res_data = send_delete_group(params);
                if(res_data.ret){
                    pop_success("删除成功!");
                    close_pop_panel();
                    get_all_group();
                }
            }
        });
    }else {
        pop_danger("请选择分组！")
    }
});


$("#download_group_button").click(function () {
    open_zhe();
    $("#download_group_panel").show();
});

$("#download_group").click(function () {
    var group_id = $("#download_group_select").val();
    if (!group_id) {
        pop_danger("请选择分组！");
        return
    }
    var params = {
        group_id: group_id
    };
    close_pop_panel();
    var res_data = send_download_group(params);
    if(res_data.ret){
        if (res_data.ret) {
            $("#dl").attr("href", "/api/download/" + res_data.file_path);
            $("#dl span").trigger('click');
        }
    }
});

$("#add_group_submit").click(function () {
    var project_id = get_project_id();
    var group_title = $("#add_group_title").val();
    if (project_id && group_title) {

        var params = {
            project_id:project_id,
            title: group_title
        };
        var res_data = send_add_group(params);
        if(res_data.ret){
            pop_success("新增成功!");
            close_pop_panel();
            get_all_group();
        }
    }else {
        pop_danger("请输入新增的分组名称!")
    }
});

$("#update_group_submit").click(function () {
    var group_id = $("#update_group_select").val();
    var group_title = $("#update_group_title").val();

    if (group_id && group_title) {
        var params = {
            id: group_id,
            title: group_title
        };
        var res_data = send_update_group(params);
        if(res_data.ret){
            pop_success("更新成功!");
            close_pop_panel();
            get_all_group();
        }
    }else {
        pop_danger("请选则分组并输入新的名称！")
    }
});


$("#apis_part").on("click", ".delete_api", function () {
    var api_id = $(this).attr("api_id");
    if (api_id) {
        msg = "确定删除？";

        Modal.confirm(
            {
                msg: msg
            }).on(function (e) {
            if (e) {
                var params = {
                        api_id: api_id
                    };
                var res_data = send_delete_api(params);
                if(res_data.ret){
                    pop_success("删除成功!");
                    close_pop_panel();
                    get_apis_for_group($("#add_api").attr("group_id"))
                }
            }
        });
    }else {
        pop_danger("请选择分组！")
    }
});

$("#add_api").click(function () {
    $("#group_select").val("");
    $("#method").val("GET");
    $("#api_title").val("");
    $("#api_desc").val("");
    $("#add_api_panel").show();
    open_zhe();
    // var group_id = $("#add_api").attr("group_id");
    // if (group_id) {
    // }else {
    //     pop_danger("请先选择分组!")
    // }
});

$("#add_api_submit").click(function () {
    // var group_id = $("#add_api").attr("group_id");
    var params = {
        group_id: $("#group_select").val(),
        api_title: $("#api_title").val(),
        api_desc: $("#api_desc").val(),
        method: $("#method").val()
    };
    if(!params.group_id){
        pop_danger("请选择分组!");
        return
    }
    if(!params.method){
        pop_danger("请选择请求方式!");
        return
    }
    if(!params.api_title){
        pop_danger("请输入接口名称");
        return
    }

    var res_data = send_add_api(params);
    if(res_data.ret){
        pop_success("新增成功!");
        close_pop_panel();
        get_all_group();
        // get_apis_for_group(group_id);
    }

});

$("#apis_part").on("click", ".update_api", function () {
    var api_id = $(this).attr("api_id");
    if (api_id) {
        $("#update_method").val($(this).attr("method"));
        $("#update_api_title").val($(this).attr("api_title"));
        $("#update_api_desc").val($(this).attr("api_desc"));

        $("#update_api_submit").val(api_id);
        $("#update_api_panel").show();
        open_zhe();
    }else {
        pop_danger("请选择接口!")
    }
});

$("#update_api_submit").click(function () {
    var api_id = $(this).val();
    var method = $("#update_method").val();
    var api_title = $("#update_api_title").val();
    var api_desc = $("#update_api_desc").val();

    if(!api_id){
        pop_danger("请选择接口!!");
        return
    }
    if(!method){
        pop_danger("请选择请求方式!");
        return
    }
    if(!api_title){
        pop_danger("请输入接口名称");
        return
    }
    var params = {
            api_id: api_id,
            method: method,
            api_title: api_title,
            api_desc: api_desc
        };
    var res_data = send_update_api(params)
    if(res_data.ret){
        pop_success("新增成功!");
        close_pop_panel();
        get_apis_for_group($("#add_api").attr("group_id"));
    }
});

$("#apis_part").on("click", ".dl_api", function () {
    var api_id = $(this).attr("api_id");
    if (api_id) {
        var params = {api_id: api_id};
        var res_data = send_dl_api(params);
        if (res_data.ret) {
            $("#dl").attr("href", "/api/download/" + res_data.file_path);
            $("#dl span").trigger('click');
        }
    }
    else {
        pop_danger("没有选择接口!")
    }
});



set_height_auto("treeview", 60)
set_height_auto("apis_part_div", 60+35)

get_user_info();

// 获取所有分组
get_all_group();
