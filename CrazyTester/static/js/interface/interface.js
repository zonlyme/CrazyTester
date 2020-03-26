$(function () {

    // 自定义的方法

    // 将函数里中注释转换成多行字符串
    Function.prototype.getMultiLine = function () {
        var lines = new String(this);
        lines = lines.substring(lines.indexOf("/*") + 3, lines.lastIndexOf("*/"));
        return lines;
    };


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

    // alert是确认框，confirm是提示框，有取消和确认，都是异步的
    // Modal.alert(
    //     {
    //         msg: '123123',
    //         title: '标题',
    //         btnok: '确定',
    //         btncl: '取消'
    //     });

    // 如需增加回调函数，后面直接加 .on( function(e){} );
    // 点击“确定” e: true
    // 点击“取消” e: false

    // Modal.confirm(
    //     {
    //         msg: "123123？"
    //     })
    //     .on(function (e) {
    //         // 这里是异步的，有什么操作只能写这里
    // });


    // 头部导航栏

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

    // 显示 上传用例面板
    $("#upload_case").click(function () {
        $('#upload_case_panel').css({'display': 'inherit'});
        open_zhe();
    });

    // 关闭上传用例面板
    $(".colse_panel_pop").click(function () {
        $('.panel_pop').css({'display': 'none'});
        close_zhe();
    });

    var open_zhe = function () {
        $("#zhe").css({"opacity": "0.5"});
        $("#zhe").css({"display": "inherit"});
    };
    var close_zhe = function () {
        $("#zhe").css({"opacity": "0"});
        $("#zhe").css({"display": "none"});
    };
    // 提交用例模板
    $("#submit_upload_case").click(function () {
        var formData = new FormData();
        var case_file = document.getElementById('case_file').files[0];
        formData.append("csrfmiddlewaretoken", get_token());
        formData.append("case_file", case_file);
        url = '/interface/upload_case';
        //采用POST方式调用服务
        $.ajax({
            url: url,
            type: 'POST',
            data: formData,
            // 告诉jQuery不要去处理发送的数据
            processData: false,
            // 告诉jQuery不要去设置Content-Type请求头
            contentType: false,
            beforeSend: function () {
                pop_success("正在进行，请稍候...", 99);
            },
            success: function (data) {
                pop_success(data);
                $('#upload_case_panel').css({'display': 'none'});
                close_zhe();
                get_all_node();
                get_nav();
            },
            error: function (responseStr) {
                pop_danger("请求失败");
                close_zhe();
            }
        });
    });

    // 批量识别全国二维码部分
    $("#license_recognit").click(function () {
        csrfmiddlewaretoken = get_token();
        var formData = new FormData();
        formData.append("csrfmiddlewaretoken", csrfmiddlewaretoken);
        url = '/interface/license_recognit';
        //采用POST方式调用服务
        $.ajax({
            url: url,
            type: 'GET',
            data: formData,
            // 告诉jQuery不要去处理发送的数据
            processData: false,
            // 告诉jQuery不要去设置Content-Type请求头
            contentType: false,
            beforeSend: function () {
                pop_success("正在识别，请稍等...", 99);
            },
            success: function (data) {
                $("#pop").empty();
                alert(data);
                // pop_success(data);
            },
            error: function (responseStr) {
                pop_danger("请求失败");
            }
        });
    });

    $("#show_env_info").click(function () {
        if ($("#env_info_div").css("display") == "none") {
            $("#env_info_div").css({'display': 'inherit'});
            open_zhe();
        }
        else {
            $("#env_info_div").css({'display': 'none'});
            close_zhe();
        }
    });


    // 左侧导航栏
    $("#newFodler").click(function () {
        if (nodeOperate1()) {
            nodeOperate("newFodler", "");
        }

    });
    $("#editeFodler").click(function () {
        if (nodeOperate1()) {
            nodeOperate3("editeFodler")
        }
    });
    $("#deleteFodler").click(function () {
        nodeOperate3("deleteFodler")
    });

    var open_panel_pop = function (statement, opeart) {
        $("#statement_operat").val(statement);
        $("#opeart").val(opeart);
        $('#confirmation_box').css({'display': 'inherit'});
        open_zhe();
    };
    var close_panel_pop = function (statement, opeart) {
        $("#statement_operat").val('');
        $("#opeart").val('');
        $('#confirmation_box').css({'display': 'none'});
        close_zhe();
    };


    // 验证input框里有没有内容
    var nodeOperate1 = function () {
        fname = $("#newFodlerName").val();
        if (fname) {
            return true
        }
        else {
            pop_danger("请输入文件名字！");
            return false
        }
    };

    // 是否选择了节点.
    var nodeOperate3 = function (operate) {
        li = $("#treeview").treeview('getSelected')[0];
        if (li) {
            html = $(li.text);
            if (html.hasClass("fodler")) {
                // 选中li的id
                li_id = li.nodeId;
                node_id = $(li.text).attr("value");
                if (operate == "editeFodler") {
                    msg = "确认更新？";
                }
                else if (operate == "deleteFodler") {
                    msg = "删除后不可挽回！！\n确定删除？？";
                }
                Modal.confirm(
                    {
                        msg: msg
                    }).on(function (e) {
                    // 这里是异步的，有什么操作只能写这里
                    if (e) {
                        nodeOperate(operate, node_id);
                    }
                });
            }
            else {
                pop_danger("请中择第一层节点!！")
            }
        } else {
            pop_danger("请选中第一层节点!！")
        }
    };

    var nodeOperate = function (operate, node_id) {

        token = get_token();
        fname = $("#newFodlerName").val();
        // 当前选中的节点作为父节点
        fromData = {
            operate: operate,
            fname: fname,
            csrfmiddlewaretoken: token,
            pNodeId: node_id
        };
        url = '/interface/nodeOperate';
        $.post(url, fromData, function (data) {

            jsondata = $.parseJSON(data);
            if (jsondata.ret) {
                if (operate == "newFodler") {
                    // singleNode = [{text: "<span class='fodler' value='"+jsondata.id+"'>"+fname+"</span>"}];
                    // $("#treeview").treeview("addNode", [{node:singleNode}]);
                    // 因为不能添加跟节点,所以直接重新加载nav部分
                    get_nav();
                    get_all_node();
                    pop_success("新增成功！");
                }
                else if (operate == "editeFodler") {
                    singleNode = {text: "<span class='fodler' value='" + node_id + "'>" + fname + "</span>"};
                    $("#treeview").treeview("editNode", [li_id, singleNode]);
                    pop_success("更新成功！");
                }
                else if (operate == "deleteFodler") {
                    $("#treeview").treeview("deleteNode", li_id);
                    pop_success("删除成功！");
                }
            }
            else {
                pop_danger("出现错误！" + jsondata.erro_msg)
            }
        })
    };

    // 载入导航栏数据
    var get_nav = function () {
        $.get('/interface/get_nav', function (nav_data) {
            $('#treeview').treeview({
                // enableLinks:true,
                // tree节点的字体颜色
                color: "#428bca",
                // tree节点左侧的展开图标，折叠的图标，节点的图标
                //	expandIcon: "glyphicon glyphicon-stop",
                //	collapseIcon: "glyphicon glyphicon-unchecked",
                //	nodeIcon: "glyphicon glyphicon-user",
                // 是否显示标签
                showTags: true,
                // tree中的数据
                data: nav_data,
                // 这里设置tree的展开层级l
                levels: 1,
                // tree 的节点背景颜色
                //  backColor:'aqua',
                onNodeSelected: function (event, data) {
                    html = $(data.text);
                    if (html.hasClass("api")) {
                        api_id = html.attr("value");
                        if (api_id) {
                            // nodeId = $("#treeview").treeview('getSelected')[0].nodeId;
                            getApiData(api_id);
                            set_c_api_id(api_id)

                        }
                    }
                }
            });
        });
    };


    // api部分
    var get_env = function () {
        $.get('/interface/get_env', function (data) {
            jsondata = $.parseJSON(data);
            option_text = '';
            for (i in jsondata) {
                option_text += '<option value="' + jsondata[i].id + '">' + jsondata[i].title;
                     // + ":" + jsondata[i].host + '</option>';
            }
            $("#env_info").html(option_text);
            $("#env_info").find("option[value='2']").attr("selected", "selected");
            $("#env_info2").html(option_text);
            $("#env_info2").find("option[value='2']").attr("selected", "selected");
            set_env_info_detail(jsondata)
        });
    };

    $(".colse_env_info_div").click(function () {
        $("#env_info_div").css({'display': 'none'});
        close_zhe();
    });

    var env_info_detail_html = function () {
        /*
         <div style="border: 2px solid #adefd3;" id="env_box">
            <table class="table table-bordered table-striped">
                <thead>
                    <tr>
                        <th colspan="3" class="th_color2">
                            标题:&nbsp;&nbsp;<span class="env_title"></span></th>
                    </tr>
                    <tr>
                        <th colspan="3" class="th_color2">
                            域名:&nbsp;&nbsp;<span class="env_host"></span></th>
                    </tr>
                    <tr>
                        <th class="th_color"><strong>参数名称</strong></th>
                        <th class="th_color"><strong>参数值</strong></th>
                        <th class="th_color"><strong>参数描述</strong></th>
                    </tr>
                </thead>
                <tbody>
                </tbody>
            </table>
        </div>
         */
    };

    var set_env_info_detail = function (env_data) {
        for (i in env_data) {
            env = env_data[i];  // 获取每一个环境信息
            env_html = $(env_info_detail_html.getMultiLine());
            env_html.find(".env_title").html(env.title);
            env_html.find(".env_host").html(env.host);
            if (env.params){
                params = $.parseJSON(env.params);   // 获取环境中参数信息
                for (j in params) {
                    param = params[j];              // 　获取环境参数中的每一个参数
                    tr = '<tr><td>' + param.key +
                        '</td><td>' +param.value +
                        '</td><td>' +param.description +
                        '</td></tr>';
                    env_html.find("tbody").append(tr);
                }
            }

            env_html = env_html.prop("outerHTML");
            $("#env_info_table").append(env_html);
            // div_boder_end = '<hr style="background-color:#2f3238;height: 2px;">';
            // $("#env_info_table").append(div_boder_end);
            div_boder_end = '<br><br>';
            $("#env_info_table").append(div_boder_end);
        }
    };

    $("#batch_test_button").click(function () {
        $("#batch_test_pop").css({'display': 'inherit'});
        open_zhe();
    });
    $(".close_batch_test_pop").click(function () {
        $("#batch_test_pop").css({'display': 'none'});
        close_zhe()
    });
    $("#submit_batch_test").click(function () {
        token = get_token();
        from_data = {
            csrfmiddlewaretoken: token,
            env_id: $("#env_info2").val(),
            apis: $("#batch_apis").val(),
            receivers: $("#batch_email").val(),
            alias: $("#batch_title").val()
        };
        url = '/interface/batch_test';
        //采用POST方式调用服务
        pop_success("正在发送请求,请稍等...", 20);
        $.get(url, from_data, function (data) {
            pop_success("请求完毕请查看结果.", 5);
            $("#batch_test_res_body").val(data);
            data = $.parseJSON(data);
            if(data.report_url){
                text = '<a href="'+data.report_url+'" target="_blank">查看测试报告</a>';
                $("#show_test_report").html(text);
                $("#show_test_report").css({"display":"inline-block"});
            }

        });
    });

    // 删除api
    $("#deleteAPI").click(function () {
        api_id = get_c_api_id();
        if (api_id == "") {
            pop_danger("当前没有选择接口！")
        }
        else {
            Modal.confirm(
                {
                    msg: "删除后不可挽回！！\n确定删除？？"
                }).on(function (e) {
                // 这里是异步的，有什么操作只能写这里
                if (e) {
                    $.get('/interface/deleteAPI/' + api_id, function (data) {
                        jsondata = $.parseJSON(data);
                        if (jsondata.ret) {
                            pop_success("删除成功！");
                            cNodeId = get_cNodeId(api_id);
                            $("#treeview").treeview("deleteNode", cNodeId);
                            clear_page();
                        }
                        else {
                            pop_danger("删除失败：" + jsondata.erro_msg)
                        }
                    });
                }
            });
        }
    });

    $("#saveAPI").click(function () {
        node_id = $("#choose_node").val();
        if (node_id == "") {
            pop_danger("请选择正确节点位置！")
        }
        else {
            data = sendForm("/interface/saveAPI/" + node_id);
            title = $("#api_title").val();
            data_hander2(data, title, node_id);
        }
    });

    // 更新api
    $("#updateAPI").click(function () {
        id = get_c_api_id();
        if (id == "") {
            pop_danger("没有选择接口!")
        }
        else {
            Modal.confirm(
                {
                    msg: "确定更新？"
                }).on(function (e) {
                // 这里是异步的，有什么操作只能写这里
                if (e) {
                    data = sendForm("/interface/updateAPI");
                    title = $("#api_title").val();
                    data_hander1(data, title);
                }
            });

        }
    });

    // 处理更新
    var data_hander1 = function (data, title) {
        // 返回的数据逻辑：
        //     有错误ret为Flase，并会有erro信息
        //     没错误ret为True，并会有warning信息，warning可能为空
        jsondata = $.parseJSON(data);
        if (jsondata.ret) {
            api_id = get_c_api_id();
            cNodeId = get_cNodeId(api_id);
            title = api_id + " -- " + title;
            singleNode = {text: "<span class='api' value='" + api_id + "'>" + title + "</span>"};
            $("#treeview").treeview("editNode", [cNodeId, singleNode]);
            pop_success("更新成功！")
        }
        else {
            pop_danger("更新失败，错误信息：\n" + jsondata.erro);
        }
    };
    // 处理保存
    var data_hander2 = function (data, title, parent_node) {
        // 返回的数据逻辑：
        //     有错误ret为Flase，并会有erro信息
        //     没错误ret为True，并会有warning信息，warning可能为空
        jsondata = $.parseJSON(data);
        if (jsondata.ret) {

            pNodeId = get_cNodeId2(parent_node);
            title = jsondata.id + " -- " + title;
            singleNode = [{text: "<span class='api' value='" + jsondata.id + "'>" + title + "</span>"}];
            $("#treeview").treeview("addNode", [pNodeId, {node: singleNode}]);
            set_c_api_id(jsondata.id);
            pop_success("保存成功！");

        }
        else {
            pop_danger("保存失败，错误信息：\n" + jsondata.erro)
        }
    };

    // 新建：清空页面所有值
    $("#newAPI").click(function () {
        Modal.confirm(
            {
                msg: "新建会清空页面数据!\n注意先保存或更新当前接口数据!!"
            }).on(function (e) {
            // 这里是异步的，有什么操作只能写这里
            if (e) {
                clear_page();
            }
        });

    });

    // 获取当前api所在的li的id 这个是查api的
    var get_cNodeId = function (api_id) {
        cNode = $("span[class='api'][value='" + api_id + "']");
        cNodeId = cNode.parent("li").attr("data-nodeid");
        cNodeId = parseInt(cNodeId);
        return cNodeId
    };
    // 获取当前api所在的li的id 这个是查节点的
    var get_cNodeId2 = function (api_id) {
        cNode = $("span[class='fodler'][value='" + api_id + "']");
        cNodeId = cNode.parent("li").attr("data-nodeid");
        cNodeId = parseInt(cNodeId);
        return cNodeId
    };
    // 获取一个节点的父级节点
    var get_pNodeId = function (nodeId) {
        pNodeId = $('#treeview').treeview('getParent', nodeId).nodeId;
        return pNodeId
    };

    var get_all_node = function () {
        // 获取首层节点
        $.get('/interface/get_all_node', function (data) {
            jsondata = $.parseJSON(data);
            $("#choose_node").empty().append('<option value="">请选择</option>');

            $.each(jsondata, function (index, item) {
                $("#choose_node").append("<option value='" + item.id + "'>" + item.name + "</option>")
            });
        });
    };

    // var createAndDownloadFile = function(fileName, content) {
    //     var aTag = document.createElement('a');
    //     var blob = new Blob([content]);
    //     aTag.download = fileName;
    //     aTag.href = URL.createObjectURL(blob);
    //     aTag.click();
    //     URL.revokeObjectURL(blob);
    // };

    // 下载接口下所有用例数据
    $("#dl_api_case_data").click(function () {

        api_id = get_c_api_id();
        if (api_id) {
            url = '/interface/dl_api_case_data?api_id=' + api_id;
            $.get(url, function (data) {
                json_data = $.parseJSON(data);
                if (json_data.ret) {
                    dl_api_case_data(json_data.file_path)
                }
                else {
                    pop_danger(json_data.erro_msg)
                }
            });
        }
        else {
            pop_danger("没有选择接口!")
        }
    });

    var dl_api_case_data = function (file_path) {
        $("#dl_api_case_data_a").attr("href", "./download/" + file_path);
        $("#dl_api_case_data_a span").trigger('click');
        // url = '/interface/dl_api_case_data2?file_name='+file_name;
        // // url = "/static/upload/case_file/" + file_name;
        // $.get(url, function(data) {
        //     // json_data = $.parseJSON(data);
        //     createAndDownloadFile(file_name, data);
        // })
    };


    // 用例部分

    // 发送请求的各个参数，获取请求结果
    $('#send_req').click(function () {
        pop_success("正在发送请求,请稍等...", 20);
        $.ajax({
            //几个参数需要注意一下
            type: "POST", //方法类型
            dataType: "json", //预期服务器返回的数据类型
            url: "/interface/send_req", //url
            data: $('#req_form').serialize(),
            success: function (data) {

                // 虽然返回的数据是json格式，但是到了这里并不是json格式，需要转换一下
                jsondata = $.parseJSON(data);
                if (!jsondata.res_ret) {
                    $('#res_body').val("");
                    $('#res_headers').val("");
                    $('#res_time').html("");
                    $('#status_code').html("");
                    $('#res_erro').html(jsondata.erro_msg);
                    pop_danger("失败了！错误信息:" + jsondata.erro_msg);
                    return;
                }
                if (!jsondata.res_body_is_json){
                    pop_success("响应成功！<br>但响应体不是josn格式,无法验证断言!");
                    $('#res_body').val(jsondata.res_body);
                    $("#prefix_tbody .key").remove();
                    $("#rsgv_tbody .key").remove();
                    $("#verify_tbody .key").remove();
                    if (jsondata.prefix){
                        set_prefix_data($.parseJSON(jsondata.prefix));// [{prefix:[{},{}]},{}]
                    }
                    if (jsondata.rsgv){
                        set_rsgv_data($.parseJSON(jsondata.rsgv));// [{rsgv:[{},{}]},{}]
                    }
                    set_asserts_data(jsondata.asserts);// [{asserts:[{},{}]},{}]
                    return;
                }

                msg = "响应成功！";
                if (jsondata.warning) {
                    msg += "<br>警告信息:" + jsondata.warning
                }
                if (!jsondata.asserts_flag){
                    msg += "<br><span style='color: red'>断言未全部通过!</span>"
                }
                pop_success(msg);

                $('#res_body').val(jsondata.res_body);
                $('#res_headers').val(jsondata.res_headers);
                $('#res_time').html(jsondata.time);
                $('#status_code').html(jsondata.status_code);
                $('#res_erro').html("");
                $("#prefix_tbody .key").remove();
                $("#rsgv_tbody .key").remove();
                $("#verify_tbody .key").remove();
                if (jsondata.prefix){
                    set_prefix_data($.parseJSON(jsondata.prefix));// [{prefix:[{},{}]},{}]
                }
                if (jsondata.rsgv){
                    set_rsgv_data($.parseJSON(jsondata.rsgv));// [{rsgv:[{},{}]},{}]
                }
                set_asserts_data(jsondata.asserts);// [{asserts:[{},{}]},{}]

            },
            error: function () {
                pop_danger("请求异常！");
            }
        });
    });

    // 前置操作tr数据
    var prefix_tr_raw = function () {
        /*
            <tr class="key">
                <td>
                    <input placeholder="1启用,0禁用" class="form-control"
                    id="prefix_status" name="prefix_status" value="" />
                </td>
                <td>
                    <input placeholder="填写用例id" class="form-control"
                    id="prefix_case_id" name="prefix_case_id" value="" />
                </td>
                <td>
                    <input placeholder="设置参数名称" class="form-control"
                    id="prefix_set_var_name" name="prefix_set_var_name"/>
                </td>
                <td>
                    <input placeholder="变量键" class="form-control"
                    id="prefix_key" name="prefix_key"/>
                </td>
                <td>
                    <input placeholder="实际值" class="form-control"
                    id="prefix_real_value" name="prefix_real_value"/>
                </td>
                <td>
                    <button type="button" class="btn btn-info remove remove_prefix">删除</button>
                </td>
            </tr>
         */
    };

    // 添加一条前置操作
    var add_prefix_tr = function (prefix_status, prefix_case_id, prefix_set_var_name, prefix_key, prefix_real_value) {
        // 设置默认参数
        prefix_status = prefix_status || 1;
        prefix_case_id = prefix_case_id || '';
        prefix_set_var_name = prefix_set_var_name || '';
        prefix_key = prefix_key || '';
        prefix_real_value = prefix_real_value || '';
        tr_thml = $(prefix_tr_raw.getMultiLine());
        tr_thml.find("#prefix_status").attr("value", prefix_status);
        tr_thml.find("#prefix_case_id").attr("value", prefix_case_id);
        tr_thml.find("#prefix_set_var_name").attr("value", prefix_set_var_name);
        tr_thml.find("#prefix_key").attr("value", prefix_key);
        tr_thml.find("#prefix_real_value").attr("value", prefix_real_value);
        // if (prefix_status == 1) {
        //     tr_thml.find("#prefix_status").attr("checked", "checked");
        // }
        // else{
        //     tr_thml.find("#prefix_status").removeAttr("checked");
        // }
        tr = tr_thml.prop("outerHTML");
        $("#prefix_mark").before(tr);
    };
    //	添加请求参数
    $(".add_prefix_tr").click(function () {
        add_prefix_tr();
    });
    //	删除前置操作
    $("#prefix_tbody").on("click", ".remove_prefix", function () {
        $(this).parent().parent().remove();
    });


    // <input type="checkbox" name="rsgv_status" value="1"
    // id="rsgv_status" checked="checked">启用
     // 响应设置全局变量
    var rsgv_tr_raw = function () {
        /*
            <tr class="key">
                <td>
                    <input placeholder="1启用,0禁用" class="form-control"
                    id="rsgv_status" name="rsgv_status" value="" /></td>
                </td>
                <td>
                    <input placeholder="变量名称" class="form-control"
                    id="rsgv_name" name="rsgv_name" value="" /></td>
                <td>
                    <input placeholder="变量键" class="form-control"
                    id="rsgv_key" name="rsgv_key"/></td>
                <td>
                    <input placeholder="实际值" class="form-control"
                    id="rsgv_real_value" name="rsgv_real_value"/></td>
                <td>
                    <button type="button" class="btn btn-info remove remove_rsgv">删除</button>
                </td>
            </tr>
         */
    };

    // 添加一条 响应设置全局变量 tr
    var add_rsgv_tr = function (rsgv_status, rsgv_name, rsgv_key, rsgv_real_value) {
        // 设置默认参数
        rsgv_status = rsgv_status || 1;
        rsgv_name = rsgv_name || '';
        rsgv_key = rsgv_key || '';
        rsgv_real_value = rsgv_real_value || '';
        tr_thml = $(rsgv_tr_raw.getMultiLine());
        tr_thml.find("#rsgv_status").attr("value", rsgv_status);
        tr_thml.find("#rsgv_name").attr("value", rsgv_name);
        tr_thml.find("#rsgv_key").attr("value", rsgv_key);
        tr_thml.find("#rsgv_real_value").attr("value", rsgv_real_value);
        // if (rsgv_status == 1) {
        //     tr_thml.find("#rsgv_status").attr("checked", "checked");
        // }
        // else{
        //     tr_thml.find("#rsgv_status").removeAttr("checked");
        // }

        tr = tr_thml.prop("outerHTML");
        $("#rsgv_mark").before(tr);
    };
    //	添加后置操作
    $(".add_rsgv_tr").click(function () {
        add_rsgv_tr();
    });
    //	删除后置操作
    $("#rsgv_tbody").on("click", ".remove_rsgv", function () {
        $(this).parent().parent().remove();
    });


    // 校验返回结果部分

    var verify_tr_raw = function () {
        /*
            <tr class="key">
                <td>
                    <input placeholder="1启用,0禁用" class="form-control"
                    id="verify_status" name="verify_status" value="" />
                </td>
                <td>
                    <input placeholder="断言键" class="verify_key form-control"
                    id="verify_key" name="verify_key" value="123" />
                </td>
                <td>
                    <input placeholder="期望的结果" class="verify_expect_ret form-control"
                    id="verify_expect_ret" name="verify_expect_ret"/></td>
                <td>
                    <select id="verify_method" name="verify_method"
                    class="verify_method form-control" title="">
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
                    </select>
                </td>

                <td>
                    <input placeholder="实际结果" class="verify_real_ret form-control"
                    id="verify_real_ret" name="verify_real_ret"/>
                </td>
                <td>
                    <input placeholder="断言结果" class="verify_ret form-control"
                    id="verify_ret" name="verify_ret"/>
                </td>
                <td>
                    <button type="button" class="btn btn-info remove remove_verify">删除</button>
                </td>
            </tr>
            */
    };

    // 设置verify并添加
    var add_verify_tr = function (verify_status, verify_key, verify_method, verify_expect_ret, verify_ret, assert_real_value, assert_erro) {
        // 设置默认参数
        verify_status = verify_status || "1";
        verify_key = verify_key || '';
        verify_method = verify_method || "1";
        verify_expect_ret = verify_expect_ret || '';
        verify_ret = verify_ret || 3;
        assert_real_value = assert_real_value || "";
        assert_erro = assert_erro || "";
        tr_thml = $(verify_tr_raw.getMultiLine());
        tr_thml.find("#verify_status").attr("value", verify_status);
        tr_thml.find("#verify_key").attr("value", verify_key);
        tr_thml.find("option[value=" + verify_method + "]").attr("selected", "selected");
        tr_thml.find("#verify_expect_ret").attr("value", verify_expect_ret);
        if (verify_ret == 1) {
            tr_thml.find("#verify_ret").css("border", "1px solid green");
            tr_thml.find("#verify_ret").attr("value", "True");
        }
        else if (verify_ret == 2) {
            tr_thml.find("#verify_ret").css({"border":"1px solid red","color":"red"});
            tr_thml.find("#verify_ret").attr("value", assert_erro);
        }
        else if (verify_ret == 3) {
            tr_thml.find("#verify_ret").attr("value", "");
        }
        tr_thml.find("#verify_real_ret").attr("value", assert_real_value);
        tr = tr_thml.prop("outerHTML");

        $("#verify_mark").before(tr);
    };

    //	添加请求参数
    $(".add_verify_tr").click(function () {
        add_verify_tr();
    });

    //	删除断言tr
    $("#verify_tbody").on("click", ".remove_verify", function () {
        $(this).parent().parent().remove();
    });


    // 参数名称部分

    // 添加空的param_tr
    var param_tr = '<tr class="key"><td><input name="param_key" class="form-control k" value="" type="text" maxlength="100" placeholder="参数名称"></td><td><input name="param_value" class="form-control v" type="text" maxlength="5000" style="width: 70%;float: left;" placeholder="参数数值"><button type="button" class="btn btn-info remove remove_param">删除参数</button></td></tr>';

    // 设置param_tr并添加
    var set_param_tr = function (k, v) {
        tr = '<tr class="key"><td><input name="param_key" class="form-control k" value="' + k + '" type="text" maxlength="100" placeholder="参数名称"></td><td><input name="param_value" class="form-control v" type="text" maxlength="5000" value=' + '\'' + v + '\'' + ' style="width: 70%;float: left;" placeholder="参数数值"><button type="button" class="btn btn-info remove remove_param">删除参数</button></td></tr>';
        $("#param_mark").before(tr);
    };

    //	添加请求参数
    $(".addParamenter").click(function () {
        $("#param_mark").before(param_tr)
    });

    //	删除请求参数
    $("#param_tbody").on("click", ".remove_param", function () {
        $(this).parent().parent().remove();
    });

    // 点击转换成json格式
    $("#switch_json").click(function () {
        url = '/interface/switch_json';
        //采用POST方式调用服务
        $.post(url, $('#req_form').serialize(), function (data) {
            jsondata = $.parseJSON(data);
            if (jsondata.ret) {
                $("#params").val(jsondata.data);
                if (jsondata.warning.length > 0) {
                    pop_success("转换成功！\n警告信息：\n" + jsondata.warning)
                }
            }
            else {
                pop_danger("转换失败，错误信息：\n" + jsondata.erro)
            }
        });
    });
    // 点击转换成键值对格式
    $("#switch_kv").click(function () {
        token = get_token();
        json_params = $("#params").val();
        // 如果json值不为空的话
        if (json_params) {
            from_data = {
                json_params: json_params,
                csrfmiddlewaretoken: token
            };
            url = '/interface/switch_kv';
            //采用POST方式调用服务
            $.post(url, from_data, function (data) {
                jsondata = $.parseJSON(data);
                if (jsondata.ret) {
                    $("#param_tbody .key").remove();
                    d = jsondata.data;

                    for (key in d) {
                        value = d[key];
                        if (typeof value == "object") {
                            value = JSON.stringify(d[key]);
                        }
                        set_param_tr(key, value); //json对象的key,value
                    }
                }
                else {
                    pop_danger("转换失败，错误信息：\n" + jsondata.erro)
                }
            });
        }

    });
    // 新建case：清空页面所有值
    $("#newCase").click(function () {
        Modal.confirm(
            {
                msg: "新建用例会清空当前数据！\n注意先保存或更新当前用例数据！！"
            }).on(function (e) {
            // 这里是异步的，有什么操作只能写这里
            if (e) {
                clear_case();
                clear_c_case_id();
                pop_success("已清空用例数据。")
            }
        });

    });
    // 删除case
    $("#deleteCase").click(function () {
        Modal.confirm(
            {
                msg: "删除后不可挽回！！\n确定删除？？"
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
        case_id = get_c_case_id();
        if (!case_id) {
            pop_danger("没有选择用例！")
        }
        else {
            from_data = {
                token: get_token(),
                case_id: case_id
            };
            url = "/interface/delete_case";
            $.post(url, from_data, function (data) {
                jsondata = $.parseJSON(data);
                if (jsondata.ret) {
                    clear_case();
                    caseId = case_id;
                    pop_success("删除成功！");
                    ret = last_case();
                    if(!ret){
                        next_case();
                    }
                    $("#case_select option[value='" + caseId + "']").remove();
                }
                else {
                    pop_danger("删除失败，错误信息：\n" + jsondata.erro_msg)
                }
            });
        }
    };

    var saveCase = function () {
        api_id = get_c_api_id();
        if (!api_id) {
            pop_danger("没有选择接口！")
        }
        else {
            url = "/interface/save_case";
            res_data = sendForm(url);
            jsondata = $.parseJSON(res_data);
            if (jsondata.ret) {
                set_case_option(jsondata.id, jsondata.title);   // 用例下拉列表新增用例option
                set_case_option_bgcolor(jsondata.id);           // 当前用例设置颜色
                $("#case_select").val(jsondata.id);
                set_c_case_id(jsondata.id);
                pop_success("保存成功！\r\n" + jsondata.warning)
            }
            else {
                pop_danger(jsondata.erro_msg)
            }
        }
    };

    var updateCase = function () {
        case_id = get_c_case_id();
        if (!case_id) {
            pop_danger("没有选择用例！")
        }
        else {
            url = "/interface/update_case";
            res_data = sendForm(url);
            jsondata = $.parseJSON(res_data);
            if (jsondata.ret) {
                pop_success("更新成功！\r\n" + jsondata.warning);
                $("#case_select option[value='" + case_id + "']").html($("#case_title").val());
            }
            else {
                pop_danger(jsondata.erro_msg)
            }
        }
    };

    $("#lastCase").click(function () {
        last_case();
    });
    var last_case = function () {
        case_id = $("#case_select").find("option:selected").prev().val();
        if(case_id){
            get_case_data(case_id);
            set_case_option_bgcolor(case_id);
            return true
        }
        else{
            pop_danger("没有上一个了。");
            return false
        }
    };
    $("#nextCase").click(function () {
        case_id = $("#case_select").find("option:selected").next().val();
        if(case_id){
            get_case_data(case_id);
            set_case_option_bgcolor(case_id);
        }
        else{pop_danger("没有下一个了。")}
    });
    var next_case = function () {
        case_id = $("#case_select").find("option:selected").next().val();
        if(case_id){
            get_case_data(case_id);
            set_case_option_bgcolor(case_id);
            return true
        }
        else{
            pop_danger("没有下一个了。");
            return false
        }

    };

    // F12_p_to_json
    $("#F12_p_to_json").click(function () {
        token = get_token();
        params = $("#params").val();
        from_data = {
            params: params,
            csrfmiddlewaretoken: token
        };
        url = '/interface/F12_p_to_json';
        //采用POST方式调用服务
        $.post(url, from_data, function (data) {
            jsondata = $.parseJSON(data);
            if (jsondata.ret) {
                $("#params").val(jsondata.data);
                pop_success("转换成功！")

            }
            else {
                pop_danger("转换失败，错误信息：\n" + jsondata.erro)
            }
        });
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

    // 添加空的header_tr
    var header_tr = '<tr class="head"><td><input name="header_key" class="form-control k" type="text" maxlength="100" placeholder="参数名称"></td><td><input name="header_value" class="form-control v" type="text" maxlength="5000" style="width: 70%;float: left;" placeholder="参数数值"><button type="button" class="btn btn-info remove remove_header">删除参数</button></td></tr>';

    // 设置header_tr并添加
    var set_header_tr = function (k, v) {
        tr = '<tr class="head"><td><input name="header_key" class="form-control k" type="text" maxlength="100" value=' + k + ' placeholder="参数名称"></td><td><input name="header_value" class="form-control v" type="text" maxlength="5000" style="width: 70%;float: left;" placeholder="参数数值" value="' + v + '"><button type="button" class="btn btn-info remove remove_header">删除参数</button></td></tr>';
        $("#header_mark").before(tr);
    };

    //	    添加headers
    $(".addHeadParamenter").click(function () {
        $("#header_mark").before(header_tr)
    });

    //	    删除header参数
    $("#header_tbody").on("click", ".remove_header", function () {
        $(this).parent().parent().remove()
    });


    // cookies部分

    // 添加当期时间戳
    $("#add_sign").click(function () {
        token = get_token();
        cookies = $("#cookies").val();
        from_data = {
            cookies: cookies,
            csrfmiddlewaretoken: token
        };
        url = '/interface/add_sign';
        //采用POST方式调用服务
        $.post(url, from_data, function (data) {
            jsondata = $.parseJSON(data);
            if (jsondata.ret) {
                $("#cookies").val(jsondata.data);
                pop_success("转换成功！")

            }
            else {
                pop_danger("转换失败，错误信息：\n" + jsondata.erro)
            }
        });

    });


    // 其他部分

    // 封装好的获取api数据的方法hu
    var getApiData = function (api_id) {
        // 获取接口数据
        $.get('/interface/get_api_data/' + api_id, function (r_data) {

            jsondata = $.parseJSON(r_data);
            // # 如果ret=false，代表有错误，打印错误信息
            if (jsondata.ret) {
                // 加载新接口先清空页面
                clear_page();

                set_api_data(jsondata.api_data);
                set_case_list(jsondata.case_data);

                if (jsondata.case_data.length > 0) {
                    get_case_data(jsondata.case_data[0]["id"]);
                    $("#case_select").val(jsondata.case_data[0]["id"]);

                }
                set_c_api_id(api_id)

            }
            else {
                pop_danger("错误：" + jsondata.erro)
            }
        });
    };

    // 设置接口数据
    var set_api_data = function (api_data) {
        $("#api_title").val(api_data.title);
        $("#api_desc").val(api_data.desc);
        $("#method").val(api_data.method);

    };

    // 设置用力列表数据
    var set_case_list = function (case_data) {
        for (c in case_data) {
            set_case_option(case_data[c].id, case_data[c].title);
        }
    };
    var set_case_option = function (id, title) {
        option_html = '<option value="' + id + '">' + title + '</option>';
        $("#case_select").append(option_html)
    };

    // 选择用例，加载对应数据
    $("#case_select").change(function () {
        case_id = $(this).val();
        if (case_id) {
            set_case_option_bgcolor(case_id);
            get_case_data(case_id);

        }
    });
    var set_case_option_bgcolor = function (case_id) {
        this_case_option = $("#case_select option[value='" + case_id + "']");
        this_case_option.css({"background-color": "aquamarine"});
        this_case_option.siblings().css({"background-color": ""});
    };

    // 设置用例数据
    var set_case_data = function (case_data) {
        $("#case_select").val(case_data.id);
        $("#case_title").val(case_data.title);
        $("#case_desc").val(case_data.desc);
        $("#url").val(case_data.url);
        $("#params").val(case_data.data);
        $("#cookies").val(case_data.cookies);
        $("#res_body").val(case_data.res_body);
        $("#res_headers").val(case_data.res_headers);
        $("#c_case_id").val(case_data.id);
        set_prefix_data(case_data.prefix);
        set_rsgv_data(case_data.rsgv);
        set_asserts_data(case_data.asserts);

        if (case_data.status == "1") {
            $("#case_status").prop("checked",true);
        }
        else{
            $("#case_status").prop("checked",false);
        }

        h = case_data.headers;// [{k:v},{k:v}]
        if (h) {
            for (key in h) {
                set_header_tr(key, h[key]); //json对象的key,value
            }
        }
        p = case_data.params;// [{k:v},{k:v}]
        if (p) {
            for (key in p) {
                set_param_tr(key, p[key]); //json对象的key,value
            }
        }
        // 没有header就添加一个空的header
        // else{
        //     $("#header_mark").before(header_tr);
        // }
    };

    var set_asserts_data = function (asserts) {
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
        if (data) {
            for (i in data) {
                add_prefix_tr(data[i].prefix_status, data[i].prefix_case_id,
                    data[i].prefix_set_var_name,
                    data[i].prefix_key, data[i].prefix_real_value);
            }
        }
    };

    var set_rsgv_data = function (data) {
        if (data) {
            for (i in data) {
                add_rsgv_tr(data[i].rsgv_status, data[i].rsgv_name,
                    data[i].rsgv_key,data[i].rsgv_real_value);
            }
        }
    };

    // 获取用例数据
    var get_case_data = function (case_id) {
        $.get('/interface/get_case_data/' + case_id, function (r_data) {
            jsondata = $.parseJSON(r_data);
            // # 如果ret=false，代表有错误，打印错误信息
            if (jsondata.ret) {
                // 加载新case先清空case
                clear_case();
                // 置入case数据
                set_case_data(jsondata.case_data);
            }
            else {
                pop_danger("错误：" + jsondata.erro)
            }
        });
    };

    // 获取当前api_id
    var get_c_api_id = function () {
        return $("#c_api_id").val()
    };
    // 清空当前api_id
    var clear_c_api_id = function () {
        $("#c_api_id").val("")
    };
    // 设置当前api_id
    var set_c_api_id = function (id) {
        $("#c_api_id").val(id)
    };

    // 获取当前case_id
    var get_c_case_id = function () {
        return $("#c_case_id").val()
    };
    // 清空当前case_id
    var clear_c_case_id = function () {
        $("#c_case_id").val("")
    };
    // 设置当前case_id
    var set_c_case_id = function (id) {
        $("#c_case_id").val(id)
    };


    // 清空页面
    var clear_page = function () {

        clear_api();
        // 清空case_select
        // $("#case_select").html("<option> 请选择用例 </option>");
        $("#case_select").html("");
        clear_case();
    };

    // 只清空api部分
    var clear_api = function () {
        // 清楚所有元素的值
        $("#api_title").val("");
        $("#api_desc").val("");
        $("#method").val("Post");

        clear_c_api_id();
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

        $("#param_tbody .key").remove();
        $("#header_tbody .head").remove();
        $("#prefix_tbody .key").remove();
        $("#rsgv_tbody .key").remove();
        $("#verify_tbody .key").remove();
        $("#params").val('');
        $("#cookies").val('');
        $("#res_body").val('');
        $("#res_headers").val('');
        // $('#API_status').html("新的API");
        // 删除了所有单个的param和header之后，在各添加一个

        clear_c_case_id();

    };

    // 接收一个url发送表单并返回响应数据
    var sendForm = function (url) {
        res_data = "";
        $.ajax({
            //几个参数需要注意一下
            type: "POST", //方法类型
            dataType: "json", //预期服务器返回的数据类型
            url: url,   //url
            async: false,
            data: $('#req_form').serialize(),
            success: function (data) {
                res_data = data;
                return res_data
            },
            error: function () {
                pop_danger("请求异常！");
            }
        });
        return res_data
    };

    // 获取token
    var get_token = function () {
        return $('input[name="csrfmiddlewaretoken"]').val();
    };

    // 弹出提示框的部分 需要一个#pop div容器
    var pop_text1 = '<div class="alert alert-';
    var pop_text2 = ' alert-dismissible" role="alert"><button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button><span id="pop_text">';
    var pop_text3 = '</span></div>';

    var t1; // 定时器用

    var pop_danger = function (text, time) {
        time = arguments[1] ? arguments[1] : 6;//设置第一个参数的默认值为1
//先清除之前的定时器,在重新增加定时器
        pop("danger", text, time)
    };

    var pop_success = function (text, time) {
        pop("success", text, time)
    };

    var pop = function (type, text, time) {
        html = pop_text1 + type + pop_text2 + text + pop_text3;
        $("#pop").html(html);
        setTimeout(time)
    };

    var setTimeout = function (time) {
        time = arguments[0] ? arguments[0] : 4;//设置第一个参数的默认值为1
        //先清除之前的定时器,在重新增加定时器
        window.clearTimeout(t1);
        t1 = window.setTimeout(refreshCount, 1000 * time);
        function refreshCount() {
            $("#pop").empty();
        }
    };


    // 载入页面时初始化部分

    // 进入页面之后，清空页面
    clear_page();
    // 获取所有节点
    get_nav();
    // 在保存节点部分获取所有节点
    get_all_node();

    get_env()


});
