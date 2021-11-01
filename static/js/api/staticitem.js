
var charts_time_out = 3000;
var charts_handle = function (option, myChart, app) {
    var dataLen = option.series[0].data.length;
    // 取消之前高亮的图形
    myChart.dispatchAction({
        type: 'downplay',
        seriesIndex: 0,
        dataIndex: app.currentIndex
    });
    app.currentIndex = (app.currentIndex + 1) % dataLen;
    // 高亮当前图形
    myChart.dispatchAction({
        type: 'highlight',
        seriesIndex: 0,
        dataIndex: app.currentIndex
    });
    // 显示 tooltip
    myChart.dispatchAction({
        type: 'showTip',
        seriesIndex: 0,
        dataIndex: app.currentIndex
    });
}
var staticitem_project = function (){
    // $.ajax({
    //     url: url,
    //     type: method,
    //     cache: false, //true 如果当前请求有缓存的话，直接使用缓存。如果该属性设置为 false，则每次都会向服务器请求
    //     dataType: "json", //预期服务器返回的数据类型
    //     // processData: false, // 告诉jQuery不要去处理发送的数据
    //     // contentType: false, // 告诉jQuery不要去设置Content-Type请求头
    //     async: async,
    //     data: params,
    //     beforeSend: function () {
    //         // pop_success("正在识别，请稍等...", 200);
    //     },
    //     success: function (response_data) { // 状态码为200 即为success
    //         if (pop){
    //             if(!response_data.ret){
    //                 pop_danger(response_data.msg)
    //             }
    //         }
    //         res_data = response_data;
    //         // defer.resolve(response_data)
    //     },
    //     error: function (response_data) { // 状态码非200 为error
    //         if (pop){
    //             response_pop_msg(response_data)
    //         }
    //         res_data = response_data.responseJSON;
    //         // defer.resolve(response_data)
    //     }
    // });
    // var res_data = send_staticitem_project()
    var res_data = "";
    $.ajax({
        url: "/api/staticitem_project",
        type: 'GET',
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
    if(res_data.ret){

        var dom = document.getElementById("container1");
        var myChart = echarts.init(dom);
        var option;

        option = {
            tooltip: {
                trigger: 'axis',
                axisPointer: {            // 坐标轴指示器，坐标轴触发有效
                    type: 'shadow'        // 默认为直线，可选为：'line' | 'shadow'
                }
            },
            title: {
                text: '项目分组/接口/用例统计',
                subtext: '总计 {0} 条用例'.format(res_data.all_count),
                left: 'center',
                marginBottom: "20px"
            },
            legend: {
                data: ['分组数量', '接口数量', '用例数量'],
                top: "10%"
            },
            toolbox: {
                show: true,
                orient: 'vertical',
                left: 'right',
                top: 'center',
                bottom: '0%',
                feature: {
                    mark: {show: true},
                    dataView: {show: true, readOnly: false},
                    magicType: {show: true, type: ['line', 'bar', 'stack', 'tiled']},
                    restore: {show: true},
                    saveAsImage: {show: true}
                }
            },
            grid: {
                top: '20%',
                left: '0',
                right: '5%',
                containLabel: true
            },
            xAxis: [
                {
                    type: 'category',
                    axisTick: {show: false},
                    data: res_data.project_title_list
                }
            ],
            yAxis: [
                {
                    type: 'value'
                }
            ],
            series: [
                {
                    name: '分组数量',
                    type: 'bar',
                    barGap: 0,
                    emphasis: {
                        focus: 'series'
                    },
                    itemStyle: {
                        normal: {
                            label: {
                                show: true, //开启显示
                                position: 'top', //在上方显示
                                textStyle: { //数值样式
                                    color: 'black',
                                    fontSize: 12
                                }
                            },
                            color: "#fc8452"
                        }
                    },
                    data: res_data.group_count_list
                },
                {
                    name: '接口数量',
                    type: 'bar',
                    emphasis: {
                        focus: 'series'
                    },
                    itemStyle: {
                        normal: {
                            label: {
                                show: true, //开启显示
                                position: 'top', //在上方显示
                                textStyle: { //数值样式
                                    color: 'black',
                                    fontSize: 12
                                }
                            },
                            color: "#91cc75"
                        }
                    },
                    data: res_data.api_count_list
                },
                {
                    name: '用例数量',
                    type: 'bar',
                    emphasis: {
                        focus: 'series'
                    },
                    itemStyle: {
                        normal: {
                            label: {
                                show: true, //开启显示
                                position: 'top', //在上方显示
                                textStyle: { //数值样式
                                    color: 'black',
                                    fontSize: 12
                                }
                            },
                            color: "#73c0de"
                        }
                    },
                    data: res_data.case_count_list
                }
            ]
        };
        var app = {};
        app.currentIndex = -1;

        setInterval(function () {
            var dataLen = option.series[0].data.length;
            // 取消之前高亮的图形
            myChart.dispatchAction({
                type: 'downplay',
                seriesIndex: 0,
                dataIndex: app.currentIndex
            });
            app.currentIndex = (app.currentIndex + 1) % dataLen;
            // 高亮当前图形
            myChart.dispatchAction({
                type: 'highlight',
                seriesIndex: 0,
                dataIndex: app.currentIndex
            });
            // 显示 tooltip
            myChart.dispatchAction({
                type: 'showTip',
                seriesIndex: 0,
                dataIndex: app.currentIndex
            });
        }, charts_time_out);
        if (option && typeof option === 'object') {
            myChart.setOption(option);
        }
    }
}


var staticitem_task = function (){
    // var res_data = send_staticitem_task();
    var res_data = "";
    $.ajax({
        url: "/api/staticitem_task",
        type: 'GET',
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
    if (res_data.ret){
        var dom = document.getElementById("container2");
        var myChart = echarts.init(dom);
        var option;

        option = {
            title: {
                text: '测试任务分布',
                subtext: '总计 {0} 个任务，共含{1}个用例'.format(res_data.task_count, res_data.case_count_for_task),
                left: 'center'
            },
            tooltip: {
                trigger: 'item',
            },
            legend: {
                orient: 'vertical',
                top: '5%',
                bottom: '0%',
                left: 'right'
            },
            series: [
                {
                    type: 'pie',
                    radius: ['40%', '60%'],
                    top: '10%',
                    avoidLabelOverlap: true,
                    label: {
                        show: true,
                        position: 'left',
                        textStyle: { //数值样式
                            color: 'black',
                            fontSize: 12
                        }
                    },
                    labelLine: {
                        show: true
                    },
                    data: res_data.data,
                    itemStyle: {
                        emphasis: {
                            shadowBlur: 1,
                            shadowOffsetX: 0,
                            shadowColor: '#fff',
                        },
                        normal: {
                            label: {
                                show: true,
                                formatter: '{b} - {c}',
                                position: 'outer',
                                color: 'rgb(131, 140, 163)',
                                fontSize: 16
                            },
                            labelLine: {
                                show: true,
                            }
                        },
                    }
                }
            ]
        };
        var app = {};
        app.currentIndex = -1;

        setInterval(function () {
            var dataLen = option.series[0].data.length;
            // 取消之前高亮的图形
            myChart.dispatchAction({
                type: 'downplay',
                seriesIndex: 0,
                dataIndex: app.currentIndex
            });
            app.currentIndex = (app.currentIndex + 1) % dataLen;
            // 高亮当前图形
            myChart.dispatchAction({
                type: 'highlight',
                seriesIndex: 0,
                dataIndex: app.currentIndex
            });
            // 显示 tooltip
            myChart.dispatchAction({
                type: 'showTip',
                seriesIndex: 0,
                dataIndex: app.currentIndex
            });
        }, charts_time_out);
        if (option && typeof option === 'object') {
            myChart.setOption(option);
        }
    }
}


var staticitem_recent = function (){
    // var params = {
    //     project_id: $("#choose_project").val()
    // };
    // console.log(111, params)
    // var res_data = send_staticitem_recent(params)
    var res_data = "";

    $.ajax({
        url: "/api/staticitem_recent?project_id=" + $("#choose_project").val(),
        type: 'GET',
        // params: params,
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
    if(res_data.ret){
        $("#container3").remove();
        $("#c3").append('<div id="container3" class="container"></div>');
        var chartDom = document.getElementById('container3');
        var myChart = echarts.init(chartDom);
        var option;

        option = {
            tooltip: {
                trigger: 'axis',
                axisPointer: {            // 坐标轴指示器，坐标轴触发有效
                    type: 'shadow'        // 默认为直线，可选为：'line' | 'shadow'
                }
            },
            legend: {
                data: res_data.titles,
                left: 'right',
                top: 'center',
                orient: 'vertical'
            },
            grid: {
                left: '5%',
                right: '20%',
                top: '20%',
                bottom: "0",
                containLabel: true
            },
            toolbox: {
                show: true,
                orient: 'vertical',
                left: 'left',
                top: 'center',
                right: '0%',
                feature: {
                    mark: {show: true},
                    dataView: {show: true, readOnly: false},
                    magicType: {show: true, type: ['line', 'bar', 'stack', 'tiled']},
                    restore: {show: true},
                    saveAsImage: {show: true}
                }
            },
            xAxis: [
                {
                    type: 'category',
                    data: res_data.days
                }
            ],
            yAxis: [
                {
                    type: 'value'
                }
            ],
            series: res_data.series
        };
        var app = {};
        app.currentIndex = -1;

        setInterval(function () {
            var dataLen = option.series[0].data.length;
            // 取消之前高亮的图形
            myChart.dispatchAction({
                type: 'downplay',
                seriesIndex: 0,
                dataIndex: app.currentIndex
            });
            app.currentIndex = (app.currentIndex + 1) % dataLen;
            // 高亮当前图形
            myChart.dispatchAction({
                type: 'highlight',
                seriesIndex: 0,
                dataIndex: app.currentIndex
            });
            // 显示 tooltip
            myChart.dispatchAction({
                type: 'showTip',
                seriesIndex: 0,
                dataIndex: app.currentIndex
            });
        }, charts_time_out);
        if (option && typeof option === 'object') {
            myChart.setOption(option);
        }
    }
}


var staticitem_user = function (){
    // var res_data = send_staticitem_user();
    var res_data = "";
    $.ajax({
        url: "/api/staticitem_user",
        type: 'GET',
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
    if (res_data.ret){
        var dom = document.getElementById("container4");
        var myChart = echarts.init(dom);
        var option;

        option = {
            title: {
                text: '近七周用户新增用例统计',
                left: 'center'
            },
            tooltip: {
                trigger: 'axis',
                axisPointer: {            // 坐标轴指示器，坐标轴触发有效
                    type: 'shadow'        // 默认为直线，可选为：'line' | 'shadow'
                }
            },
            legend: {
                data: res_data.users,
                left: 'left',
                top: 'center',
                orient: 'vertical'
            },
            grid: {
                left: '15%',
                right: '5%',
                top: '10%',
                bottom: "0",
                containLabel: true
            },
            toolbox: {
                show: true,
                orient: 'vertical',
                left: 'right',
                top: 'center',
                feature: {
                    mark: {show: true},
                    dataView: {show: true, readOnly: false},
                    magicType: {show: true, type: ['line', 'bar', 'stack', 'tiled']},
                    restore: {show: true},
                    saveAsImage: {show: true}
                }
            },
            xAxis: {
                type: 'category',
                boundaryGap: false,
                data: res_data.days
            },
            yAxis: {
                type: 'value'
            },
            series: res_data.series
        };

        var app = {};
        app.currentIndex = -1;

        setInterval(function () {
            var dataLen = option.series[0].data.length;
            // 取消之前高亮的图形
            myChart.dispatchAction({
                type: 'downplay',
                seriesIndex: 0,
                dataIndex: app.currentIndex
            });
            app.currentIndex = (app.currentIndex + 1) % dataLen;
            // 高亮当前图形
            myChart.dispatchAction({
                type: 'highlight',
                seriesIndex: 0,
                dataIndex: app.currentIndex
            });
            // 显示 tooltip
            myChart.dispatchAction({
                type: 'showTip',
                seriesIndex: 0,
                dataIndex: app.currentIndex
            });
        }, charts_time_out);

        if (option && typeof option === 'object') {
            myChart.setOption(option);
        }
    }
}


var staticitem_user2 = function (){
    // var res_data = send_staticitem_user2();
    var res_data = "";
    $.ajax({
        url: "/api/staticitem_user2",
        type: 'GET',
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
    if (res_data.ret){
        var dom = document.getElementById("container5");
        var myChart = echarts.init(dom);
        var option;

        option = {
            title: {
                text: '用例新增统计（按最后更新算）',
                left: 'center'
            },
            tooltip: {
                trigger: 'item',
            },
            legend: {
                orient: 'vertical',
                top: '5%',
                bottom: '0%',
                left: 'right'
            },
            series: [
                {
                    type: 'pie',
                    radius: ['40%', '60%'],
                    top: '10%',
                    avoidLabelOverlap: true,
                    label: {
                        show: true,
                        position: 'left',
                        textStyle: { //数值样式
                            color: 'black',
                            fontSize: 12
                        }
                    },
                    labelLine: {
                        show: true
                    },
                    data: res_data.series,
                    itemStyle: {
                        emphasis: {
                            shadowBlur: 1,
                            shadowOffsetX: 0,
                            shadowColor: '#fff',
                        },
                        normal: {
                            label: {
                                show: true,
                                formatter: '{b} - {c}',
                                position: 'outer',
                                color: 'rgb(131, 140, 163)',
                                fontSize: 16
                            },
                            labelLine: {
                                show: true,
                            }
                        },
                    }
                }
            ]
        };

        var app = {};
        app.currentIndex = -1;

        setInterval(function () {
            var dataLen = option.series[0].data.length;
            // 取消之前高亮的图形
            myChart.dispatchAction({
                type: 'downplay',
                seriesIndex: 0,
                dataIndex: app.currentIndex
            });
            app.currentIndex = (app.currentIndex + 1) % dataLen;
            // 高亮当前图形
            myChart.dispatchAction({
                type: 'highlight',
                seriesIndex: 0,
                dataIndex: app.currentIndex
            });
            // 显示 tooltip
            myChart.dispatchAction({
                type: 'showTip',
                seriesIndex: 0,
                dataIndex: app.currentIndex
            });
        }, charts_time_out);

        if (option && typeof option === 'object') {
            myChart.setOption(option);
        }
    }
}


var get_all_project = function () {
    var res_data = send_get_all_project();

    if(res_data.ret){
        var data = res_data.data;
        var option_text = '';
        for(i in data){
            option_text += '<option value="{0}">{1}</option>'.format(data[i].id, data[i].title);
        }
        var default_option = '<option value="">全部项目</option>';
        $("#choose_project").html("").append(default_option+option_text);
        staticitem_recent();

    }
};

set_header_middle("系统看板")

// get_user_info();
get_all_project()
staticitem_project();
staticitem_task();
staticitem_user();
staticitem_user2();
$("#choose_project").change(function () {
    staticitem_recent();
})


