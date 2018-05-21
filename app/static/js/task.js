function showImg(value, row, index){
    var status = {
        "pass": "icon-success",
        "fail": "icon-fail",
        "running": "icon-run"
    };

    return '<img width="17px" height="17px" border="0" src="{0}"/>'.lym_format(row.url) ;
}

function view_detail_report(value, row, index){
    if(row.status == "running" || row.status=="exception"){
        return;
    }

    return "<a href=\"#\" class=\"easyui-linkbutton\" data-options=\"iconCls:'icon-product'\" onclick=\"parent.addReportTab({0}, {1});\">查看报告</a>".lym_format(row.project_id, row.build_no);
}

function view_run_log(value, row, index){
    if(row.status=="exception"){
        return;
    }
    return "<a href=\"#\" class=\"easyui-linkbutton\" data-options=\"iconCls:'icon-product'\" onclick=\"parent.addLogTab({0}, {1});\">查看日志</a>".lym_format(row.project_id, row.build_no);
}

function view_task(value, row, index){
    return "<a href=\"#\" class=\"easyui-linkbutton\" data-options=\"iconCls:'icon-task'\" onclick=\"parent.addTaskTab('查看任务', '/task/{0}', 'icon-task');\">查看任务</a>".lym_format(row.id);
}

function manage_task(value, row, index){
    var text = { "false": "启动", "true": "停止" };
    var url = "/api/v1/trigger/"
    var method = {"false": "start", "true": "stop"};
    return "<a href=\"#\" class=\"easyui-linkbutton\" onclick=\"manage_scheduler('{1}','{2}','{3}')\">{0}</a>".lym_format(text[row.enable], method[row.enable], url, row.id);
}

function manage_scheduler(method, url, id){
    $.ajax({
        type : 'POST',
        url : url,
        data:  {
               "method": method,
               "trigger_id": id
            },
        success : function(data, textStatus, request) {
            $("#task_list").datagrid('reload');
            show_msg("提示", data.msg);
            }
    });
}