// 自定义的方法

// 将函数里中注释转换成多行字符串
Function.prototype.getMultiLine = function () {
    var lines = new String(this);
    lines = lines.substring(lines.indexOf("/*") + 3, lines.lastIndexOf("*/"));
    return lines;
};

// 将js对象json格式化输出
var json_stringify = function (info) {
    return JSON.stringify(info, null, 4)
};

// 获取url参数，不可以带井号
function getUrlQueryString(name) {
    const reg = new RegExp("(^|&)" + name + "=([^&]*)(&|$)", "i");
    const urlObj = window.location;
    var r = urlObj.href.indexOf('#') > -1 ? urlObj.hash.split("?")[1].match(reg) : urlObj.search.substr(1).match(reg);
    if (r != null) return unescape(r[2]);
    return null;
}

// 提示框
window.Modal = function () {
    var reg = new RegExp("\\[([^\\[\\]]*?)\\]", 'igm');
    var alr = $("#ycf-alert");
    var ahtml = alr.html();

    //关闭时恢复 modal html 原样，供下次调用时 replace 用
    //var _init = function () {
    //    alr.on("hidden.bs.modal", function (e) {
    //        $(this).html(ahtml);
    //    });
    //}();

    /* html 复原不在 _init() 里面做了，重复调用时会有问题，直接在 _alert/_confirm 里面做 */


    var _alert = function (options) {
        alr.html(ahtml);    // 复原
        alr.find('.ok').removeClass('btn-success').addClass('btn-primary');
        alr.find('.cancel').hide();
        _dialog(options);

        return {
            on: function (callback) {
                if (callback && callback instanceof Function) {
                    alr.find('.ok').click(function () {
                        callback(true)
                    });
                }
            }
        };
    };

    var _confirm = function (options) {
        alr.html(ahtml); // 复原
        alr.find('.ok').removeClass('btn-primary').addClass('btn-success');
        alr.find('.cancel').show();
        _dialog(options);
        $('.modal-backdrop').css({'opacity': "0.5"});
        return {
            on: function (callback) {
                if (callback && callback instanceof Function) {
                    alr.find('.ok').click(function () {
                        callback(true)
                    });
                    alr.find('.cancel').click(function () {
                        callback(false)
                    });
                }
            }
        };
    };

    var _dialog = function (options) {
        var ops = {
            msg: "提示内容",
            title: "操作提示",
            btnok: "确定",
            btncl: "取消"
        };

        $.extend(ops, options);

        var html = alr.html().replace(reg, function (node, key) {
            return {
                Title: ops.title,
                Message: ops.msg,
                BtnOk: ops.btnok,
                BtnCancel: ops.btncl
            }[key];
        });

        alr.html(html);
        alr.modal({
            width: 500,
            backdrop: 'static'
        });
    };

    return {
        alert: _alert,
        confirm: _confirm
    }

}();

// 格式化字符串
String.prototype.format = function (args) {
    var result = this;
    if (arguments.length > 0) {
        if (arguments.length == 1 && typeof (args) == "object") {
            for (var key in args) {
                if (args[key] != undefined) {
                    var reg = new RegExp("({" + key + "})", "g");
                    result = result.replace(reg, args[key]);
                }
                else {
                    args[key] = "";
                    var reg = new RegExp("({)" + key + "(})", "g");
                    result = result.replace(reg, args[key]);
                }
            }
        }
        else {
            for (var i = 0; i < arguments.length; i++) {
                if (arguments[i] != undefined) {
                    //var reg = new RegExp("({[" + i + "]})", "g");//这个在索引大于9时会有问题，谢谢何以笙箫的指出
                    var reg = new RegExp("({)" + i + "(})", "g");
                    result = result.replace(reg, arguments[i]);
                }
                else {
                    arguments[i] = "";
                    var reg = new RegExp("({)" + i + "(})", "g");
                    result = result.replace(reg, arguments[i]);
                }
            }
        }
    }
    return result;
};

// 弹出提示框的部分 需要一个#pop div容器
var pop_text1 = '<div class="alert alert-';
var pop_text2 = ' alert-dismissible" role="alert">' +
    '<button type="button" class="close" data-dismiss="alert" ' +
    'aria-label="Close"><span aria-hidden="true">&times;</span>' +
    '</button><span id="pop_text">';
var pop_text3 = '</span></div>';

var t1; // 定时器用

var pop_danger = function (text, time) {
    time = arguments[1] ? arguments[1] : 6;
    //先清除之前的定时器,在重新增加定时器
    pop("danger", text, time)
};

var pop_success = function (text, time) {
    time = arguments[1] ? arguments[1] : 6;
    pop("success", text, time)
};


var pop = function (type, text, time) {
    html = pop_text1 + type + pop_text2 + text + pop_text3;
    $("#pop").html(html);
    timer(time)
};

var timer = function (time) {
    time = arguments[0] ? arguments[0] : 8;//设置第一个参数的默认值为1
    //先清除之前的定时器,在重新增加定时器
    window.clearTimeout(t1);
    t1 = window.setTimeout(refreshCount, 1000 * time);
    function refreshCount() {
        $("#pop").empty();
    }
};

var open_zhe = function () {
    $("#zhe").css({"opacity": "0.5"});
    $("#zhe").show();
};

var close_zhe = function () {
    $("#zhe").css({"opacity": "0"});
    $("#zhe").hide();
};

$(".close_pop_panel").click(function () {
    close_pop_panel()
});

var close_pop_panel = function () {
   $(".pop_panel").hide();
    close_zhe();
};
$("#zhe").click(function () {
    $(".pop_panel").hide();
    close_zhe();
});

// 获取token
var get_token = function () {
    return $('input[name="csrfmiddlewaretoken"]').val();
};



// 生成随机数
var random = (function(){
	var high = 1, low = 1 ^ 0x49616E42;
	var shuffle = function(seed){
		high = seed;
		low = seed ^ 0x49616E42;
	}

	return function(){
    	var a = new Date()-0
     	shuffle(a);
    	high = (high << 16) + (high >> 16);
    	high += low;
   		low += high;
     	return high;
 	}
})();


//
// var send_req = function (method, url, params, pop=true) {
//
//     var res_data = "";
//
//     if (method == "get"){
//         console.log(1, url)
//         $.get(url, params, function (response_data) {
//             if (pop){
//                 if(!response_data.ret){
//                     pop_danger(response_data.msg)
//                 }
//             }
//             res_data = response_data;
//             console.log(2, res_data)
//         }).fail(function (response_data) {
//             if (pop){
//                 response_pop_msg(response_data)
//             }
//             res_data = response_data;
//         });
//     }
//
//     else if(method == "post"){
//         $.post(url, params, function (response_data) {
//             if (pop){
//                 if(!response_data.ret){
//                     pop_danger(response_data.msg)
//                 }
//             }
//             res_data = response_data;
//         }).fail(function (response_data) {
//             if (pop){
//                 response_pop_msg(response_data)
//             }
//             res_data = response_data;
//         });
//     }
//     console.log(3, res_data)
//     return res_data
// };

// 获取url路径 举例：http//www.liangshunet.com/pub/item.aspx?t=osw7 ==> /pub/item.aspx
function GetUrlRelativePath(){
    var url = document.location.toString();
    var arrUrl = url.split("//");

    var start = arrUrl[1].indexOf("/");
    var relUrl = arrUrl[1].substring(start);//stop省略，截取从start开始到结尾的所有字符

    if(relUrl.indexOf("?") != -1){
        relUrl = relUrl.split("?")[0];
    }

    return relUrl.split("#")[0];
}

// url地址添加参数 xxx?t=osw7 ==> ?t=osw7&a=1
// function add_url_params(url,arg,arg_val){
function add_url_params(key, val, url){
    url = url || window.location.href
    url = url.split("#")[0]    // 不要 #号老报错

    var pattern=key+'=([^&]*)';
    var replaceText=key+'='+val;
    if(url.match(pattern)){
        var tmp='/('+ key+'=)([^&]*)/gi';
        tmp=url.replace(eval(tmp),replaceText);
        return tmp;
    }else{
        if(url.match('[\?]')){
            return url+'&'+replaceText;
        }else{
            return url+'?'+replaceText;
        }
    }
}


var set_header_middle = function (str){
    top.window.document.getElementById('header_middle').innerHTML = str;
}

var set_height_auto = function (ele_id, h){
    // tree_h = window.screen.height; //最大页面高度（不正确
    // h1 = document.documentElement.clientHeight;
    // h2 = window.innerHeight; // 当前页面高度
    console.log(window.innerHeight)
    document.getElementById(ele_id).style.maxHeight= window.innerHeight - h + 'px';
}

var response_pop_msg = function (response_data) {
    if(!response_data.responseJSON.ret){
        // var res_data = response_data.responseJSON;  // 这个值不知道是json还是对象
        pop_danger(response_data.responseJSON.msg);
    }
    else {
        pop_danger("请求异常！");
    }
};

var send_req_file = function (method, url, params, pop) {
    params = params || "";
    pop = params || true;

    var res_data = "";
    $.ajax({
        url: url,
        type: 'POST',
        data: params,
        // 告诉jQuery不要去处理发送的数据
        processData: false,
        // 告诉jQuery不要去设置Content-Type请求头
        contentType: false,
        async: false,
        beforeSend: function () {
            // pop_success("正在进行，请稍候...", 99);
        },
        success: function (response_data) {
            if (pop){
                if(!response_data.ret){
                    pop_danger(response_data.msg)
                }
            }
            res_data = response_data;
        },
        error: function (response_data) {
            if (pop){
                response_pop_msg(response_data)
            }
            res_data = response_data.responseJSON;
        }
    });
    return res_data
};

var send_req = function (method, url, params, pop=true, async=false) {

    var res_data = "";
    // var defer = $.Deferred();    # defer 可以解决请求时间过长,页面卡住的问题
    $.ajax({
        url: url,
        type: method,
        cache: false, //true 如果当前请求有缓存的话，直接使用缓存。如果该属性设置为 false，则每次都会向服务器请求
        dataType: "json", //预期服务器返回的数据类型
        // processData: false, // 告诉jQuery不要去处理发送的数据
        // contentType: false, // 告诉jQuery不要去设置Content-Type请求头
        async: async,
        data: params,
        beforeSend: function () {
            // pop_success("正在识别，请稍等...", 200);
        },
        success: function (response_data) { // 状态码为200 即为success
            if (pop){
                if(!response_data.ret){
                    pop_danger(response_data.msg)
                }
            }
            res_data = response_data;
            // defer.resolve(response_data)
        },
        error: function (response_data) { // 状态码非200 为error
            if (pop){
                response_pop_msg(response_data)
            }
            res_data = response_data.responseJSON;
            // defer.resolve(response_data)
        }
    });
    return res_data;
    // return defer.promise();
};

// $.when(send_get_all_project()).done(function(data){
//     alert(data);
// });

// 登陆相关
var send_login_verify = function (params) {
    return send_req("post", "/login_verify", params)};

// 自测用的接口
var send_test = function (params) {return send_req("get", "/api/test_self", params)};

// 项目部分
var send_get_all_project = function (params) {return send_req("get", "/api/get_all_project", params)};
var send_add_project = function (params) {return send_req("post", "/api/add_project", params)};
var send_delete_project = function (params) {return send_req("post", "/api/delete_project", params)};
var send_update_project = function (params) {return send_req("post", "/api/update_project", params)};

// 分组部分
var send_get_all_group = function (params) {return send_req("get", "/api/get_all_group", params)};
var send_add_group= function (params) {return send_req("post", "/api/add_group", params)};
var send_delete_group = function (params) {return send_req("post", "/api/delete_group", params)};
var send_update_group = function (params) {return send_req("post", "/api/update_group", params)};

// 接口部分部分
var send_get_api_list = function (params) {return send_req("get", "/api/get_api_list", params)};   // 根据接口列表
var send_add_api = function (params) {return send_req("post", "/api/add_api", params)};
var send_delete_api = function (params) {return send_req("post", "/api/delete_api", params)};
var send_update_api = function (params) {return send_req("post", "/api/update_api", params)};

// 用例部分
var send_get_case_data = function (params) {return send_req("get", "/api/get_case_data", params)};   // 获取某个case的数据
var send_get_case_list = function (params) {return send_req("get", "/api/get_case_list", params)};   // 获取case列表
var send_save_case = function (params) {return send_req("post", "/api/save_case", params)};
var send_delete_case = function (params) {return send_req("get", "/api/delete_case", params)};
var send_update_case = function (params) {return send_req("post", "/api/update_case", params)};

// 全局配置
var send_get_global_env = function (params) {return send_req("get", "/api/get_global_env", params)};
// var send_get_global_env_tag = function (params) {return send_req("get", "/api/get_global_env_tag", params)};
var send_get_global_host = function (params) {return send_req("get", "/api/get_global_host", params)};
var send_get_global_variable = function (params) {return send_req("get", "/api/get_global_variable", params)};
var send_get_global_header = function (params) {return send_req("get", "/api/get_global_header", params)};
var send_get_global_cookie = function (params) {return send_req("get", "/api/get_global_cookie", params)};

//接口报告相关接口
var send_get_workwx_user_group = function () {return send_req("get", "/api/get_workwx_user_group")};
var send_get_workwx_group_chat = function () {return send_req("get", "/api/get_workwx_group_chat")};
var send_get_email_user_group = function () {return send_req("get", "/api/get_email_user_group")};

// 页面接口请求
var send_send_req = function (params) {return send_req("post", "/api/send_req", params)};

// 其他功能部分
var send_switch_json = function (params) {return send_req("post", "/api/switch_json", params)};     // kv格式转换成json格式
var send_switch_kv = function (params) {return send_req("post", "/api/switch_kv", params)};     // json格式转换成kv格式
var send_F12_p_to_json = function (params) {return send_req("post", "/api/F12_p_to_json", params)};     // F12的请求参数转换json
var send_excel_json_auto_switch = function (params) {return send_req("post", "/api/excel_json_auto_switch", params)};   // excel格式和json格式智能转换
var send_add_sign = function (params) {return send_req("post", "/api/add_sign", params)};        // 添加当前时间戳

// 测试任务
var send_get_test_task_detail = function (params) {return send_req("get", "/api/get_test_task_detail", params)};
var send_get_test_task_list = function (params) {return send_req("get", "/api/get_test_task_list", params)};

var send_add_test_task = function (params) {return send_req("post", "/api/add_test_task", params)};
var send_update_test_task = function (params) {return send_req("post", "/api/update_test_task", params)};
var send_delete_test_task = function (params) {return send_req("post", "/api/delete_test_task", params)};
var send_execute_task_now = function (params) {return send_req("get", "/api/execute_task_now", params)};

// 定时任务
var send_start_cron_program = function (params) {return send_req("get", "/api/start_cron_program", params)};
var send_pause_cron_program = function (params) {return send_req("get", "/api/pause_cron_program", params)};
var send_resume_cron_program = function (params) {return send_req("get", "/api/resume_cron_program", params)};
var send_stop_cron_program = function (params) {return send_req("get", "/api/stop_cron_program", params)};
var send_start_cron_task = function (params) {return send_req("get", "/api/start_cron_task", params)};
var send_stop_cron_task = function (params) {return send_req("get", "/api/stop_cron_task", params)};


// 测试任务组 send_get_task_detail
var send_get_task_group_list = function (params) {return send_req("get", "/api/get_task_group_list", params)};
var send_get_task_group_detail = function (params) {return send_req("get", "/api/get_task_group_detail", params)};
var send_add_task_group = function (params) {return send_req("post", "/api/add_task_group", params)};
var send_update_task_group = function (params) {return send_req("post", "/api/update_task_group", params)};
var send_delete_task_group = function (params) {return send_req("post", "/api/delete_task_group", params)};
var send_execute_task_group_now = function (params) {return send_req("get", "/api/execute_task_group_now", params)};
var send_start_cron_task_group = function (params) {return send_req("get", "/api/start_cron_task_group", params)};
var send_stop_cron_task_group = function (params) {return send_req("get", "/api/stop_cron_task_group", params)};


// 获取指定任务或所有任务的下次执行时间
var send_get_cron_info = function (params) {return send_req("get", "/api/get_cron_info", params, false)};

// 测试报告列表数据
var send_get_report_list = function (params) {return send_req("get", "/api/get_report_list", params)};

// 测试报告页面
var send_get_report_data = function (params) {return send_req("get", "/api/get_report_data", params)};
var send_get_case_detail = function (params) {return send_req("get", "/api/get_case_detail", params)};
// 获取全部报告数据
var send_get_all_report = function (params) {return send_req("get", "/api/get_all_report", params)};


var send_upload_case = function (params) {return send_req_file("post", "/api/upload_case", params)};     // 上传用例
// 下载接口用例数据 dl_api_case_data:数据处理判断，结果为ｔｒｕｅ通过触发ａ标签直接请求文件
var send_dl_api = function (params) {return send_req("get", "/api/dl_api", params)};
var send_download = function (params) {return send_req("get", "/api/download", params)};   // 下载文件
var send_download_group = function (params) {return send_req("get", "/api/download_group", params)};

// 统计
var send_staticitem_project = function (params) {return send_req("get", "/api/staticitem_project")};
var send_staticitem_task = function (params) {return send_req("get", "/api/staticitem_task")};
var send_staticitem_recent = function (params) {return send_req("get", "/api/staticitem_recent", params)};
var send_staticitem_user = function (params) {return send_req("get", "/api/staticitem_user")};
var send_staticitem_user2 = function (params) {return send_req("get", "/api/staticitem_user2")};

// 报表自动化对比
var send_get_report_form_list = function (params) {return send_req("get", "/api/get_report_form_list", params)};
var send_get_rf_result_list = function (params) {return send_req("get", "/api/get_rf_result_list", params)};
var send_get_rf_result_detail = function (params) {return send_req("get", "/api/get_rf_result_detail", params)};

var get_user_info = function () {}

