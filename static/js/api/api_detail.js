// 测试用的按钮
$("#test").click(function () {
    // arr=$('#treeview').treeview('getChecked');
    var singleNode = [{text: "<span class='api' value='1'>222</span>"}, {text: "<span class='api' value='2'>333</span>"}];
    //得到选择的节点
    // var nodeId = $("#treeview").treeview('getSelected')[0].nodeId;
    // console.log("t1", $("#treeview").treeview('getSelected')[0].nodeId)
    //获取数据，添加到树中
    $("#treeview").treeview("addNode", [1, {node: singleNode}]);

    // 编辑
    // $("#treeview").treeview("editNode", [nodeData, { text: "新名字" }]);
    // 删除选中的节点,包括他的子节点,如果该节点如果是根节点，不能删除
    // $("#treeview").treeview("deleteNode", nodeId);

    // 删除当前节点下的全部子节点(不懂删除当前节点)
    // $("#treeview").treeview("deleteChildrenNode", nodeId);
    // console.log(typeof nodeData);
    // console.log("t2",$("#treeview").treeview('getSelected')[0].nodeId)

});

// api部分

var set_global_host = function () {
    var res_data = send_get_global_host();
    if (res_data.ret) {
        var data = res_data.data;
        var option_text = '';
        for (i in data) {
            option_text += '<option value="' + data[i].id + '">' + data[i].title + '</option>';
        }
        $("#global_host_select").html(option_text);
    }
};


var set_global_variable = function () {
    var res_data = send_get_global_variable();
    if (res_data.ret) {
        var data = res_data.data;
        var option_text = '';
        for (i in data) {
            option_text += '<option value="' + data[i].id + '">' + data[i].title + '</option>';
        }
        $("#global_variable_select").html(option_text);
    }
};

var set_global_header = function () {
    var res_data = send_get_global_header();
    if (res_data.ret) {
        var data = res_data.data;
        var option_text = '';
        for (i in data) {
            option_text += '<option value="' + data[i].id + '">' + data[i].title + '</option>';
        }
        $("#global_header_select").html(option_text);
    }
};

var set_global_cookie = function () {
    var res_data = send_get_global_cookie();
    if (res_data.ret) {
        var data = res_data.data;
        var option_text = '';
        for (i in data) {
            option_text += '<option value="' + data[i].id + '">' + data[i].title + '</option>';
        }
        $("#global_cookie_select").html(option_text);

    }
};

// 设置全局环境部分
var set_global_env = function (project_id) {
    var params = {project_id: project_id}
    var res_data = send_get_global_env(params);
    if (res_data.ret) {
        var data = res_data.data;
        var option_text = '';
        var index;
        for (i in data) {
            if (data[i].default_uses){
                index = data[i].id
            }
            option_text += '<option value="{0}">{1}</option>'.format(data[i].id, data[i].title);
        }
        // var default_option = '<option value="">请选择</option>'
        // $("#global_env_select").html("").html(default_option + option_text);
        $("#global_env_select").html("").html(option_text);
        $("#global_env_select").val(index);
    }
};

// 用例部分
var get_req_params = function () {
    var params = {
        csrfmiddlewaretoken: get_token(),
        api_id: $("#api_id").val(),
        case_id: $("#case_id").val(),
        method: $("#api_method").val(),
        api_title: $("#api_title").val(),
        case_select: $("#case_select").val(),
        case_status: $("#case_status").prop("checked"),
        set_global_cookies: $("#set_global_cookies").prop("checked"),
        clear_global_cookies: $("#clear_global_cookies").prop("checked"),
        url: $("#url").val(),
        case_title: $("#case_title").val(),
        case_desc: $("#case_desc").val(),

        // 请求参数
        params: $("#params").val(),
        param_key:get_all_value_for_ele_name("param_key"),
        param_value:get_all_value_for_ele_name("param_value"),

        // 断言
        verify_status: get_all_value_for_ele_name("verify_status"),
        verify_key: get_all_value_for_ele_name("verify_key"),
        verify_expect_ret: get_all_value_for_ele_name("verify_expect_ret"),
        verify_method: get_all_value_for_ele_name("verify_method"),
        assert_real_value: get_all_value_for_ele_name("assert_real_value"),
        verify_ret: get_all_value_for_ele_name("verify_ret"),

        // 前置
        prefix_status:get_all_value_for_ele_name("prefix_status"),
        prefix_case_id:get_all_value_for_ele_name("prefix_case_id"),
        prefix_set_var_name:get_all_value_for_ele_name("prefix_set_var_name"),
        prefix_key:get_all_value_for_ele_name("prefix_key"),
        prefix_real_value:get_all_value_for_ele_name("prefix_real_value"),

        // 后置
        rsgv_status:get_all_value_for_ele_name("rsgv_status"),
        rsgv_name:get_all_value_for_ele_name("rsgv_name"),
        rsgv_key:get_all_value_for_ele_name("rsgv_key"),
        rsgv_real_value:get_all_value_for_ele_name("rsgv_real_value")

        // res_body: $("#res_body").val(),  // 响应体与响应头不传
        // res_headers: $("#res_headers").val(),

    };
    return params
};

// 选项卡部分
$("#caseTab a").click(function(e){
    e.preventDefault();
    $(this).tab("show");
});

$("#caseTab").on("show.bs.tab",function(e){
    $(e.target).addClass("tab_li_color_show");
}).on("hide.bs.tab",function(e){
    $(e.target).removeClass("tab_li_color_show");
    // $(e.target).addClass("tab_li_color_none");
});

function get_all_value_for_ele_name(name) {
    var values = [];
    $("[name="+name+"]").each(function () {
        values.push($(this).val());
    });
    return values;
}

function get_req_form_data() {
    var params = new Array();
    var req_form = $('#req_form').serializeArray();
    for(i in req_form){
        params.push(req_form[i])
    }
    var case_status = $("#case_status").prop("checked");
    var set_global_cookies = $("#set_global_cookies").prop("checked");
    var clear_global_cookies = $("#clear_global_cookies").prop("checked");
    params.push({name: "api_id", value: $("#api_id").val()});
    params.push({name: "case_status", value: case_status});
    params.push({name: "set_global_cookies", value: set_global_cookies});
    params.push({name: "clear_global_cookies", value: clear_global_cookies});

    return params
}

// 发送请求的各个参数，获取请求结果
$('.send_req').click(function () {

    if (! $("#global_env_select").val()){
        pop_danger("请选择环境！");
        return
    }
    // console.log($('#req_form').serializeArray());$('#req_form').serializeArray()
    pop_success("正在发送请求,请稍等...", 99);

    // 一定要清空的
    $('#res_body').val("");
    $('#res_headers').val("");
    $('#real_data').val("");
    $('#res_time').html("");
    $('#status_code').html("");
    $('#res_erro').html("");

    $.post("/api/send_req", get_req_form_data(), function (res_data) {

    // 接口参数处理失败
    if (!res_data.ret) {
        $('#res_erro').html(res_data.msg);
        return;
    }

    $('#real_data').val(json_stringify(res_data.req_item_real));

    // if (res_data.ret)
    // 发送请求失败
    if (!res_data.res_part.successful_response_flag){
         $('#res_erro').html(res_data.res_part.fail_req_msg);
        pop_danger(res_data.res_part.fail_req_msg);
        return;
    }

    var res_part = res_data.res_part;
    $('#res_body').val(json_stringify(res_part.res_body));
    $('#res_headers').val(json_stringify(res_part.res_headers));
    $('#res_cookies').val(json_stringify(res_part.res_cookies));

    $('#res_time').html(res_part.time);
    $('#status_code').html(res_part.status_code);

    $("#prefix_tbody .key").remove();
    $("#rsgv_tbody .key").remove();
    $("#rsgh_tbody .key").remove();
    // $("#rsgc_tbody .key").remove();
    $("#verify_tbody .key").remove();
    set_prefix_data(res_data.req_item_real.prefix);
    set_rsgv_data(res_data.req_item_real.rsgv);
    set_rsgh_data(res_data.req_item_real.rsgh);
    set_rsgc_data(res_data.req_item_real.rsgc);
    set_asserts_data(res_data.req_item_real.asserts);

    // 请求成功但响应体不是json格式
    if (!res_data.res_part.res_body_is_json){
        var msg = "响应成功！<br>警告信息:" + res_data.warning;

        msg += "<br><span style='color: red'>但响应体不是josn格式！</span>";
        pop_success(msg);
    }
    // 请求成功,响应体是json格式
    else{
        var msg = "响应成功！";
        if(res_data.warning){
            msg += "<br>警告信息:" + res_data.warning;
        }
        if (!res_part.asserts_flag){
            msg += "<br><span style='color: red'>断言未全部通过!</span>"
        }
        pop_success(msg);
    }
    // $("#params_part").tab("show");

    }).fail(function (response_data) {
       response_pop_msg(response_data);
   });
});

// 前置操作tr数据
var prefix_tr_raw = function () {
    /*
        <tr class="key">
            <td class="width_10">
                <input placeholder="1启用,0禁用" class="form-control"
                id="prefix_status" name="prefix_status" value="" />
            </td>
            <td class="width_15">
                <input placeholder="填写用例id" class="form-control"
                id="prefix_case_id" name="prefix_case_id" value="" />
            </td>
            <td>
                <input placeholder="设置参数名称" class="form-control"
                id="prefix_set_var_name" name="prefix_set_var_name"/>
            </td>
            <td>
                <input placeholder="变量路径" class="form-control"
                id="prefix_key" name="prefix_key"/>
            </td>
            <td>
                <input placeholder="实际值" class="form-control"
                id="prefix_real_value" name="prefix_real_value" readonly/>
            </td>
            <td>
                <button type="button" class="btn btn-info remove remove_prefix">删除</button>
            </td>
        </tr>
     */
};

// 添加一条前置操作
var add_prefix_tr = function (prefix_status, prefix_case_id, prefix_set_var_name,
                              prefix_key, prefix_real_value, prefix_res_body, prefix_erro) {
    // 设置默认参数
    prefix_status = prefix_status || 1;
    prefix_case_id = prefix_case_id || '';
    prefix_set_var_name = prefix_set_var_name || '';
    prefix_key = prefix_key || '';
    prefix_real_value = prefix_real_value || '';
    prefix_res_body = prefix_res_body || '';
    prefix_erro = prefix_erro || '';
    var tr_thml = $(prefix_tr_raw.getMultiLine());
    tr_thml.find("#prefix_status").attr("value", prefix_status);
    tr_thml.find("#prefix_case_id").attr("value", prefix_case_id);
    tr_thml.find("#prefix_set_var_name").attr("value", prefix_set_var_name);
    tr_thml.find("#prefix_key").attr("value", prefix_key);
    if(prefix_erro){
        tr_thml.find("#prefix_real_value").css({"border":"1px solid red","color":"red"});
        tr_thml.find("#prefix_real_value").attr("value", prefix_erro);
    }
    else{
        tr_thml.find("#prefix_real_value").attr("value", prefix_real_value);
    }
    tr_thml.find("#prefix_res_body").attr("value", prefix_res_body);

    // if (prefix_status == 1) {
    //     tr_thml.find("#prefix_status").attr("checked", "checked");
    // }
    // else{
    //     tr_thml.find("#prefix_status").removeAttr("checked");
    // }
    tr = tr_thml.prop("outerHTML");
    $("#prefix_mark").before(tr);
};

//	添加前置参数
$(".add_prefix_tr").click(function () {
    add_prefix_tr();
});

//	删除前置操作
$("#prefix_tbody").on("click", ".remove_prefix", function () {
    $(this).parent().parent().remove();
});

 // 响应体中的参数设置到全局变量
var rsgv_tr_raw = function () {
    /*
        <tr class="key">
            <td class="width_10">
                <input placeholder="1启用,0禁用" class="form-control
                rsgv_status" name="rsgv_status" value="" /></td>
            </td>
            <td>
                <input placeholder="变量名称" class="form-control
                rsgv_name" name="rsgv_name" value="" /></td>
            <td>
                <select class="rsgv_set_method form-control" name="rsgv_set_method">
                    <option value="1">同名变量覆盖</option>
                    <option value="2">同名变量追加(append)</option>
                    <option value="3">同名变量覆盖-自定义代码</option>
                    <option value="4">同名变量追加(append)-自定义代码</option>
                </select></td>
            <td>
                <textarea class="form-control rsgv_key" name="rsgv_key" style="height:34px" placeholder="变量路径"></textarea>
                </td>
            <td>
                <input placeholder="实际值" class="form-control
                rsgv_real_value" name="rsgv_real_value" readonly/></td>
            <td>
                <button type="button" class="btn btn-info remove remove_rsgv">删除</button>
            </td>
        </tr>
     */
};

// 添加一条 响应体设置全局变量 tr
var add_rsgv_tr = function (rsgv_status, rsgv_name, rsgv_set_method, rsgv_key, rsgv_real_value, rsgv_ret, rsgv_erro_msg) {

    // 设置默认参数
    rsgv_status = rsgv_status || 1;
    rsgv_name = rsgv_name || '';
    rsgv_set_method = rsgv_set_method || '';
    rsgv_key = rsgv_key || '';

    rsgv_real_value = rsgv_real_value || '';
    // rsgv_ret = rsgv_ret || null;
    rsgv_erro_msg = rsgv_erro_msg || '';

    var tr_thml = $(rsgv_tr_raw.getMultiLine());
    tr_thml.find(".rsgv_status").attr("value", rsgv_status);
    tr_thml.find(".rsgv_name").attr("value", rsgv_name);
    // tr_thml.find(".rsgv_set_method").val(2);
    // tr_thml.find(".rsgv_set_method").get(0).selectedIndex = rsgv_set_method;
    tr_thml.find(".rsgv_set_method").find("option[value='" + rsgv_set_method + "']").attr("selected", "selected");
    tr_thml.find(".rsgv_key").html(rsgv_key);

    if (rsgv_ret === undefined){
        tr_thml.find(".rsgv_real_value").attr("value", "");
    }
    else if (rsgv_ret){
        tr_thml.find(".rsgv_real_value").attr("value", rsgv_real_value);
        tr_thml.find(".rsgv_real_value").css("border", "1px solid green");
    }
    else{
        tr_thml.find(".rsgv_real_value").attr("value", rsgv_erro_msg);
        tr_thml.find(".rsgv_real_value").css({"border":"1px solid red","color":"red"});
    }


    // if (rsgv_status == 1) {
    //     tr_thml.find(".rsgv_status").attr("checked", "checked");
    // }
    // else{
    //     tr_thml.find(".rsgv_status").removeAttr("checked");
    // }

    tr = tr_thml.prop("outerHTML");
    $("#rsgv_mark").before(tr);
};
//	添加rsgv操作
$(".add_rsgv_tr").click(function () {
    add_rsgv_tr();
});
//	删除rsgv操作
$("#rsgv_tbody").on("click", ".remove_rsgv", function () {
    $(this).parent().parent().remove();
});


 // 响应体中的参数设置到全局请求头
var rsgh_tr_raw = function () {
    /*
        <tr class="key">
            <td class="width_10">
                <input placeholder="1启用,0禁用" class="form-control
                rsgh_status" name="rsgh_status" value="" /></td>
            </td>
            <td>
                <input placeholder="变量名称" class="form-control
                rsgh_name" name="rsgh_name" value="" /></td>
            <td>
                <select class="rsgh_set_method form-control" name="rsgh_set_method">
                    <option value="1">变量路径</option>
                    <option value="2">自定义代码</option>
                </select></td>
            <td>
                <textarea class="form-control rsgh_key" name="rsgh_key" style="height:34px" placeholder="变量路径"></textarea>
                </td>
            <td>
                <input placeholder="实际值" class="form-control
                rsgh_real_value" name="rsgh_real_value" readonly/></td>
            <td>
                <button type="button" class="btn btn-info remove remove_rsgh">删除</button>
            </td>
        </tr>
     */
};

// 添加一条 响应头设置全局请求头 tr
var add_rsgh_tr = function (rsgh_status, rsgh_name, rsgh_set_method, rsgh_key, rsgh_real_value, rsgh_ret, rsgh_erro_msg) {
    // 设置默认参数
    rsgh_status = rsgh_status || 1;
    rsgh_name = rsgh_name || '';
    rsgh_set_method = rsgh_set_method || '';
    rsgh_key = rsgh_key || '';
    rsgh_real_value = rsgh_real_value || '';
    // rsgh_ret = rsgh_ret || null;
    rsgh_erro_msg = rsgh_erro_msg || '';

    var tr_thml = $(rsgh_tr_raw.getMultiLine());
    tr_thml.find(".rsgh_status").attr("value", rsgh_status);
    tr_thml.find(".rsgh_name").attr("value", rsgh_name);
    tr_thml.find(".rsgh_set_method").find("option[value='" + rsgh_set_method + "']").attr("selected", "selected");
    tr_thml.find(".rsgh_key").html(rsgh_key);
    tr_thml.find(".rsgh_real_value").attr("value", rsgh_real_value);
    // if (rsgh_status == 1) {
    //     tr_thml.find(".rsgh_status").attr("checked", "checked");
    // }
    // else{
    //     tr_thml.find(".rsgh_status").removeAttr("checked");
    // }
    if (rsgh_ret === undefined){
        tr_thml.find(".rsgh_real_value").attr("value", "");
    }
    else if (rsgh_ret){
        tr_thml.find(".rsgh_real_value").attr("value", rsgh_real_value);
        tr_thml.find(".rsgh_real_value").css("border", "1px solid green");
    }
    else{
        tr_thml.find(".rsgh_real_value").attr("value", rsgh_erro_msg);
        tr_thml.find(".rsgh_real_value").css({"border":"1px solid red","color":"red"});
    }

    var tr = tr_thml.prop("outerHTML");
    $("#rsgh_mark").before(tr);
};
//	添加rsgh操作
$(".add_rsgh_tr").click(function () {
    add_rsgh_tr();
});
//	删除rsgh操作
$("#rsgh_tbody").on("click", ".remove_rsgh", function () {
    $(this).parent().parent().remove();
});



 // 响应cookies设置全局cookie
var rsgc_tr_raw = function () {
    /*
        <tr class="key">
            <td class="width_10">
                <input placeholder="1启用,0禁用" class="form-control
                rsgc_status" name="rsgc_status" value="" /></td>
            </td>
            <td>
                <input placeholder="变量名称" class="form-control
                rsgc_name" name="rsgc_name" value="" /></td>
            <td>
                <input placeholder="变量" class="form-control
                rsgc_key" name="rsgc_key"/></td>
            <td>
                <input placeholder="实际值" class="form-control
                rsgc_real_value" name="rsgc_real_value" readonly/></td>
            <td>
                <button type="button" class="btn btn-info remove remove_rsgc">删除</button>
            </td>
        </tr>
     */
};

// 添加一条 响应cookies设置全局cookie tr
var add_rsgc_tr = function (rsgc_status, rsgc_name, rsgc_key, rsgc_real_value) {
    // 设置默认参数
    rsgc_status = rsgc_status || 1;
    rsgc_name = rsgc_name || '';
    rsgc_key = rsgc_key || '';
    rsgc_real_value = rsgc_real_value || '';
    var tr_thml = $(rsgc_tr_raw.getMultiLine());
    tr_thml.find(".rsgc_status").attr("value", rsgc_status);
    tr_thml.find(".rsgc_name").attr("value", rsgc_name);
    tr_thml.find(".rsgc_key").attr("value", rsgc_key);
    tr_thml.find(".rsgc_real_value").attr("value", rsgc_real_value);
    // if (rsgc_status == 1) {
    //     tr_thml.find(".rsgc_status").attr("checked", "checked");
    // }
    // else{
    //     tr_thml.find(".rsgc_status").removeAttr("checked");
    // }

    tr = tr_thml.prop("outerHTML");
    $("#rsgc_mark").before(tr);
};
//	添加rsgc操作
$(".add_rsgc_tr").click(function () {
    add_rsgc_tr();
});
//	删除rsgc操作
$("#rsgc_tbody").on("click", ".remove_rsgc", function () {
    $(this).parent().parent().remove();
});


// 校验返回结果部分

var verify_tr_raw = function () {
    /*
        <tr class="key">
            <td class="width_10">
                <input placeholder="1启用,0禁用" class="form-control verify_status" name="verify_status"/>
            </td>
            <td>
                <input class="verify_key form-control" name="verify_key" placeholder="变量路径"/>
            </td>
            <td>
                <textarea class="form-control verify_expect_ret"
                name="verify_expect_ret"style="height:34px" placeholder="期望值"></textarea>
            <td>
                <select name="verify_method" class="verify_method form-control">
                    <option value="0"> 状态码 </option>
                    <option value="1"> = </option>
                    <option value="2"> ！＝ </option>
                    <option value="4"> >= </option>
                    <option value="6"> <= </option>
                    <option value="7"> in </option>
                    <option value="8"> not in </option>
                    <option value="20"> ~in </option>
                    <option value="9"> len = </option>
                    <option value="10"> len != </option>
                    <option value="12"> len >= </option>
                    <option value="14"> len <= </option>
                    <option value="16"> []或{}中的元素in对比 </option>
                    <option value="17"> []或{}中的元素~in对比 </option>
                    <option value="18"> []不计较顺序对比 </option>
                    <option value="19"> {}中的键对比 </option>
                    <option value="90"> 自定义代码(代码写在期望结果里) </option>
                </select>
            </td>
            <td>
                <input class="assert_real_value form-control" name="assert_real_value" placeholder="实际值" readonly/>
            </td>
            <td>
                <input class="verify_ret form-control" name="verify_ret" placeholder="断言结果" readonly/>
            </td>
            <td>
                <button type="button" class="btn btn-info remove remove_verify">删除</button>
            </td>
        </tr>
        */
};

// 设置verify并添加
var add_verify_tr = function (
    verify_status, verify_key, verify_method, verify_expect_ret, verify_ret, assert_real_value, assert_erro) {
    // 设置默认参数
    verify_status = verify_status || "1";
    verify_key = verify_key || '';
    verify_method = verify_method || "1";
    verify_expect_ret = verify_expect_ret || '';
    verify_ret = verify_ret || 3;
    assert_real_value = assert_real_value || "";
    assert_erro = assert_erro || "";
    var tr_thml = $(verify_tr_raw.getMultiLine());
    tr_thml.find(".verify_status").attr("value", verify_status);
    tr_thml.find(".verify_key").attr("value", verify_key);
    tr_thml.find(".verify_method").find("option[value='" + verify_method + "']").attr("selected", "selected");
    tr_thml.find(".verify_expect_ret").html(verify_expect_ret);

    if (verify_ret == 1) {
        tr_thml.find(".verify_ret").css("border", "1px solid green");
        tr_thml.find(".verify_ret").attr("value", "True");
    }
    else if (verify_ret == 2) {
        tr_thml.find(".verify_ret").css({"border":"1px solid red","color":"red"});
        tr_thml.find(".verify_ret").attr("value", assert_erro);
    }
    else if (verify_ret == 3) {
        tr_thml.find(".verify_ret").attr("value", "");
    }
    tr_thml.find(".assert_real_value").attr("value", assert_real_value);
    var tr = tr_thml.prop("outerHTML");

    $("#verify_mark").before(tr);
};

//	添加断言tr
$(".add_verify_tr").click(function () {
    add_verify_tr();
});

//	删除断言tr
$("#verify_tbody").on("click", ".remove_verify", function () {
    $(this).parent().parent().remove();
});


// 参数名称部分

// 设置param_tr并添加
var set_param_tr = function (k, v) {
    var tr = '<tr class="key"><td width="40%"><input name="param_key" class="form-control k" value="' + k + '" type="text" maxlength="100" placeholder="参数名称"></td><td width="50%"><input name="param_value" class="form-control v" type="text" maxlength="5000" value=' + '\'' + v + '\'' + ' placeholder="参数数值"></td><td width="10%"><button type="button" class="btn btn-info remove remove_param">删除</button></td></tr>';
    $("#param_mark").before(tr);
};

//	添加请求参数
$(".addParamenter").click(function () {
    set_param_tr("", "");
});

//	删除请求参数
$("#param_tbody").on("click", ".remove_param", function () {
    $(this).parent().parent().remove();
});


$("#excel_json_auto_switch").click(function () {

    var params = {
        csrfmiddlewaretoken: get_token(),
        sample_data: $("#sample_data").val()
    };

    var res_data = send_excel_json_auto_switch(params);
    if(res_data.ret){
        pop_success(res_data.msg);
        $("#sample_data").val(res_data.sample_data)
    }
});

// 点击转换成json格式
$("#switch_json").click(function () {
    var res_data = send_switch_json($('#req_form').serialize());
    if (res_data.ret) {
        $("#params").val(json_stringify(res_data.data));
        var msg = "转换成功！";
        if (res_data.warning){
            msg += "\n警告信息：\n" + res_data.warning;
        }
        pop_success(msg)
    }
});

// 点击转换成键值对格式
$("#switch_kv").click(function () {

    var json_params = $("#params").val();
    if (json_params) {
        var params = {
            json_params: json_params,
            csrfmiddlewaretoken: get_token()
        };
        var res_data = send_switch_kv(params);
        if (res_data.ret) {
            $("#param_tbody .key").remove();
            var d = res_data.data;

            for (key in d) {
                value = d[key];
                if (typeof value == "object") {
                    value = JSON.stringify(d[key]);
                }
                set_param_tr(key, value); //json对象的key,value
            }
        }
    }

});

// 新建case：清空页面所有值
$("#newCase").click(function () {
    Modal.confirm(
        {
            msg: "确认初始化用例部分的页面数据?(不做增删该操作)"
        }).on(function (e) {
        // 这里是异步的，有什么操作只能写这里
        if (e) {
            clear_case();
            pop_success("已清空用例数据。")
        }
    });

});
// 删除case
$("#deleteCase").click(function () {
    Modal.confirm(
        {
            msg: "确定删除？？"
        }).on(function (e) {
        // 这里是异步的，有什么操作只能写这里
        if (e) {
            deleteCase();
        }
    });

});
// 更新case
$("#updateCase").click(function () {
    Modal.confirm(
        {
            msg: "确定更新？？"
        }).on(function (e) {
        // 这里是异步的，有什么操作只能写这里
        if (e) {
            updateCase();
        }
    });

});
// 保存case
$("#saveCase").click(function () {
    saveCase();
});

var deleteCase = function () {
    var case_id = get_case_id();
    if (!case_id) {
        pop_danger("没有选择用例！")
    }
    else {
        var parmas = {
            token: get_token(),
            id: case_id
        };
        var res_data = send_delete_case(parmas);
        if (res_data.ret) {

            pop_success("删除成功！");

            var next_case_id_ = next_case_id();
            if(!next_case_id_){
                next_case_id_ = last_case_id();
            }

            clear_case();

            if(next_case_id_){
                get_case_list(next_case_id_);
            }
        }
    }
};

var saveCase = function () {
    var api_id = $("#api_id").val();
    if (!api_id) {
        pop_danger("没有选择接口！")
    }
    else {
        var res_data = send_save_case(get_req_form_data());
        if (res_data.ret) {
            pop_success("新增成功！\r\n" + res_data.warning);
            get_case_list(res_data.id);
        }
    }
};

var updateCase = function () {
    var case_id = get_case_id();
    if (!case_id) {
        pop_danger("没有选择用例！")
    }
    else {
        var res_data = send_update_case(get_req_form_data());
        if (res_data.ret) {
            pop_success("更新成功！\r\n" + res_data.warning);
            get_case_list(case_id);
        }
    }
};

// var selectNode_for_caseid = function (case_id) {
//     node = $("span[class='case'][value='" + case_id + "']").parent("li");
//     nodeId = node.attr("data-nodeid");
//     $('#treeview').treeview('selectNode', [parseInt(nodeId), { silent:true}]);
// };
// var get_lastnode_caseid = function (case_id) {
//     node = $("span[class='case'][value='" + case_id + "']").parent("li").prev();
//     last_case_id = node.find(".case").attr("value");
//     return last_case_id
// };
// var get_nextnode_caseid = function (case_id) {
//     node = $("span[class='case'][value='" + case_id + "']").parent("li").next();
//     next_case_id = node.find(".case").attr("value");
//     return next_case_id
// };

// 设置用力列表数据
var set_case_list = function (case_data) {
    $("#case_select").html('');
    for (c in case_data) {
        set_case_option(case_data[c].id, case_data[c].title);
    }

};
var set_case_option = function (id, title) {
    var option_html = '<option value="' + id + '">' + +id+" -- "+title + '</option>';
    $("#case_select").append(option_html)
};

// 选择用例，加载对应数据
$("#case_select").change(function () {
    var case_id = $(this).val();
    if (case_id) {
        get_case_data(case_id);
    }
});

var set_case_option_bgcolor = function (case_id) {
    var this_case_option = $("#case_select option[value='" + case_id + "']");
    this_case_option.css({"background-color": "aquamarine"});
    this_case_option.siblings().css({"background-color": ""});

    var all_options = document.getElementById("case_select").options;
    for (i=0; i<all_options.length; i++){
        if (all_options[i].value == case_id)  // 根据option标签的ID来进行判断  测试的代码这里是两个等号
        {
            all_options[i].selected = true;
        }

    }
};


var next_case_id = function () {
    var case_id = $("#case_select").find("option:selected").next().val();
    return case_id
};
var last_case_id = function () {
    var case_id = $("#case_select").find("option:selected").prev().val();
    return case_id
};

$("#lastCase").click(function () {
    last_case();
});
var last_case = function () {
    var case_id = last_case_id();
    if(case_id){
        get_case_data(case_id);
    }
    else{
        pop_danger("没有上一个了。");
    }
};

$("#nextCase").click(function () {
    next_case();
});
var next_case = function () {
    var case_id =  next_case_id();
    if(case_id){
        get_case_data(case_id);
    }
    else{
        pop_danger("没有下一个了。");
    }

};

// F12_p_to_json
$("#F12_p_to_json").click(function () {

    var p = $("#params").val();

    if (p){
        var params = {
            params: params,
            csrfmiddlewaretoken: get_token()
        };
        var res_data = send_F12_p_to_json(params);
        if (res_data.ret) {
            $("#params").val(res_data.data);
            pop_success("转换成功！")

        }
        // var url = '/api/F12_p_to_json';
        // //采用POST方式调用服务
        // $.post(url, params, function (res_data) {
        //     if (res_data.ret) {
        //         $("#params").val(res_data.data);
        //         pop_success("转换成功！")
        //
        //     }
        //     else {
        //         pop_danger("转换失败，错误信息：\n" + res_data.erro)
        //     }
        // });
    }
});


// header名称部分

// haeders参数解释处理
$("#h_info_show").click(function () {
    $("#h_info_show").css({'display': 'none'});
    $("#h_info_close").css({'display': 'inherit'});
    $('#header_info').css({'display': 'inherit'});
});
$("#h_info_close").click(function () {
    $("#h_info_close").css({'display': 'none'});
    $("#h_info_show").css({'display': 'inherit'});
    $('#header_info').css({'display': 'none'});
});

// 设置header_tr并添加
var set_header_tr = function (k, v) {
    var tr = '<tr class="head"><td width="40%"><input name="header_key" class="form-control k" type="text" maxlength="100" value="' + k + '" placeholder="参数名称"></td><td width="50%"><input name="header_value" class="form-control v" type="text" maxlength="5000" placeholder="参数数值" value="' + v + '"></td><td width="10%"><button type="button" class="btn btn-info remove remove_header">删除</button></td></tr>';
    $("#header_mark").before(tr);
};

//	    添加headers
$("#addHeadParamenter").click(function () {
    // $("#header_mark").before(header_tr)
    set_header_tr('', '')
});
$("#addContentType_json").click(function () {
    // $("#header_mark").before(header_tr)
    set_header_tr('Content-Type', 'application/json')
});

//	    删除header参数
$("#header_tbody").on("click", ".remove_header", function () {
    $(this).parent().parent().remove()
});


// 添加当期时间戳
$("#add_sign").click(function () {

    var cookies = $("#cookies").val();
    var params = {
        cookies: cookies,
        csrfmiddlewaretoken: get_token()
    };

    var res_data = send_add_sign(params);
    if (res_data.ret) {
        $("#cookies").val(res_data.data);
        pop_success("转换成功！")

    }

    // var url = '/api/add_sign';
    // //采用POST方式调用服务
    // $.post(url, params, function (res_data) {
    //     if (res_data.ret) {
    //         $("#cookies").val(res_data.data);
    //         pop_success("转换成功！")
    //
    //     }
    //     else {
    //         pop_danger("转换失败，错误信息：\n" + res_data.erro)
    //     }
    // });

});

// 获取用例数据
var get_case_data = function (case_id) {
    var params = {
        id: case_id
    };
    var res_data = send_get_case_data(params);
    if (res_data.ret) {

        // 加载新case先清空case
        clear_case();
        // 置入case数据
        set_case_data(res_data.data);
    }
    set_case_option_bgcolor(case_id);
};

// 设置用例数据
var set_case_data = function (case_data) {
    $("#case_id").val(case_data.id);
    $("#case_title").val(case_data.title);
    $("#case_desc").val(case_data.desc);
    $("#url").val(case_data.url);

    $("#latest_update_user").html(case_data.latest_update_user);
    $("#latest_update_user").attr("title", case_data.latest_update_user_id);
    $("#u_date").html(case_data.u_date);

    if(case_data.data){
        $("#params").val(json_stringify(case_data.data));
    }
    if(case_data.sample_data){
        $("#sample_data").val(json_stringify(case_data.sample_data));
    }
    if(case_data.cookies){
        $("#cookies").val(json_stringify(case_data.cookies));
    }
    set_prefix_data(case_data.prefix);
    set_rsgv_data(case_data.rsgv);
    set_rsgh_data(case_data.rsgh);
    // set_rsgc_data(case_data.rsgc);
    set_asserts_data(case_data.asserts);

    // var case_status = false;
    // if (case_data.status == "1") {
    //    case_status = true
    // }
    //  $("#case_status").prop("checked", case_status);
     $("#case_status").prop("checked", case_data.status);
     $("#set_global_cookies").prop("checked", case_data.set_global_cookies);
     $("#clear_global_cookies").prop("checked", case_data.clear_global_cookies);

    var h = case_data.headers;// [{k:v},{k:v}]
    if (h) {
        for (key in h) {
            set_header_tr(key, h[key]); //json对象的key,value
        }
    }
    // 没有header就添加一个空的header
    // else{
    //     set_header_tr("Content-Type", "application/json");
    //     // $("#header_mark").before(header_tr);
    // }

    var p = case_data.params;// [{k:v},{k:v}]
    if (p) {
        for (key in p) {
            set_param_tr(key, p[key]); //json对象的key,value
        }
    }
};

var set_asserts_data = function (asserts) {
    // [{asserts:[{},{}]},{}]
    // console.log(asserts)
    var assert_ret;
    if (asserts) {
        for (a in asserts) {
            if (asserts[a].assert_ret) {
                assert_ret = 1
            }
            else if (asserts[a].assert_ret == undefined) {
                assert_ret = 3
            }
            else {
                assert_ret = 2
            }
            add_verify_tr(asserts[a].assert_status, asserts[a].assert_key, asserts[a].assert_method,
                asserts[a].assert_expect_value, assert_ret,
                asserts[a].assert_real_value, asserts[a].assert_erro);
        }
    }
};

var set_prefix_data = function (data) {
    // [{prefix:[{},{}]},{}]
    if (data) {
        for (i in data) {
            add_prefix_tr(
                data[i].prefix_status,
                data[i].prefix_case_id,
                data[i].prefix_set_var_name,
                data[i].prefix_key,
                data[i].prefix_real_value,
                data[i].prefix_res_body,
                data[i].prefix_erro
            );
        }
    }
};

var set_rsgv_data = function (data) {
    // [{rsgv:[{},{}]},{}]
    if (data) {
        for (i in data) {
            add_rsgv_tr(data[i].rsgv_status, data[i].rsgv_name, data[i].rsgv_set_method,
                data[i].rsgv_key, data[i].rsgv_real_value, data[i].rsgv_ret, data[i].rsgv_erro_msg);
        }
    }
};
var set_rsgh_data = function (data) {
    // [{rsgh:[{},{}]},{}]
    if (data) {
        for (i in data) {
            add_rsgh_tr(data[i].rsgh_status, data[i].rsgh_name, data[i].rsgh_set_method,
                data[i].rsgh_key, data[i].rsgh_real_value, data[i].rsgh_ret, data[i].rsgh_erro_msg);
        }
    }
};
var set_rsgc_data = function (data) {
    // [{rsgc:[{},{}]},{}]
    if (data) {
        for (i in data) {
            add_rsgc_tr(data[i].rsgc_status, data[i].rsgc_name,
                data[i].rsgc_key,data[i].rsgc_real_value);
        }
    }
};

// 获取当前case_id
var get_case_id = function () {
    return $("#case_id").val()
};

// 设置当前case_id
var set_case_id = function (id) {
    $("#case_id").val(id)
};


// 只清空case部分
var clear_case = function () {
    $("#case_title").val('');
    $("#case_desc").val('');
    $("#url").val("");
    $("#res_time").html('');
    $("#status_code").html('');
    $("#res_erro").html('');
    $("#case_status").prop("checked",true);

    $("#latest_update_user").html("");
    $("#latest_update_user").attr("title", "");
    $("#u_date").html("");

    $("#param_tbody .key").remove();
    $("#header_tbody .head").remove();
    $("#prefix_tbody .key").remove();
    $("#rsgv_tbody .key").remove();
    $("#rsgh_tbody .key").remove();
    // $("#rsgc_tbody .key").remove();
    $("#set_global_cookies").prop("checked",false);
    $("#clear_global_cookies").prop("checked",false);
    $("#verify_tbody .key").remove();
    $("#params").val('');
    $("#sample_data").val('');
    $("#cookies").val('');
    $("#real_data").val('');
    $("#res_body").val('');
    $("#res_headers").val('');
    $("#res_cookies").val('');

    $("#case_id").val("")
};


var api_info_html = function () {
    /*
    <div id="api_info">
        <ol class="breadcrumb">
            <li>
                <a id="project_href" style="color: #337ab7"><span id="project_title" class="line25"></span></a>
            </li>
            <li>
                <span id="group_title" class="line25"></span>
            </li>
            <li>
                <span id="api_method" class="label label-success line25"></span>
                <span id="api_titel" class="line25"></span>
            </li>
        </ol>
    </div>
     */
};


var set_api_info = function (res_data) {

    $("title").html("接口:" + res_data.api_data.title);

    var tr_thml = $(api_info_html.getMultiLine());

    tr_thml.find("#project_href").attr("href", "/html/api/api_dir?index_flag=1&project_id="+res_data.project_data.id);
    tr_thml.find("#project_title").html(res_data.project_data.title);
    tr_thml.find("#group_title").html(res_data.group_data.title);
    tr_thml.find("#api_titel").html(res_data.api_data.title);
    tr_thml.find("#api_method").html(res_data.api_data.method);
    tr_thml.find("#api_id").val(res_data.api_data.id);
    $("#api_id").val(res_data.api_data.id);

    var tr = tr_thml.prop("outerHTML");
    set_header_middle(tr)
};

var get_case_list = function (next_case_id, first) {
    first = first || false;

    var params = {
        api_id: getUrlQueryString("api_id"),
        case_id: next_case_id
    };
    var res_data = send_get_case_list(params);

    if(res_data.ret){
        set_api_info(res_data);
        set_case_list(res_data.case_list);

        if(first){
            set_global_env(res_data.project_data.id);
            // set_global_host();
            // set_global_variable();
            // set_global_header();
            // set_global_cookie();
            // set_default_global_config(res_data.project_data);
        }
        if (next_case_id){
            get_case_data(next_case_id);
        }
        else{
            if(res_data.case_list.length > 0){
                next_case_id = next_case_id || res_data.case_list[0].id;
                get_case_data(next_case_id);
            }
        }

    }
};

var set_default_global_config = function (project_data) {

    // $("#global_host_select").find("option[value='" + project_data.global_host + "']").attr("selected", "selected");
    // $("#global_variable_select").find("option[value='" + project_data.global_variable + "']").attr("selected", "selected");
    // $("#global_header_select").find("option[value='" + project_data.global_header + "']").attr("selected", "selected");
    // $("#global_cookie_select").find("option[value='" + project_data.global_cookie + "']").attr("selected", "selected");

    $("#global_host_select").val(project_data.global_host);
    $("#global_variable_select").val(project_data.global_variable);
    $("#global_header_select").val(project_data.global_header);
    $("#global_cookie_select").val(project_data.global_cookie);
};


get_user_info();

var case_id = getUrlQueryString("case_id");
get_case_list(case_id, true);


