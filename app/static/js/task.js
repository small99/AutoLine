function showImg(value, row, index){
    var status = {
        "pass": "icon-success",
        "fail": "icon-fail",
        "running": "icon-run"
    };

    return '<img width="17px" height="17px" border="0" src="{0}"/>'.lym_format(row.url) ;
}

function view_detail_report(value, row, index){
    if(row.status == "running"){
        return;
    }

    return "<a href=\"#\" class=\"easyui-linkbutton\" data-options=\"iconCls:'icon-product'\" onclick=\"parent.addReportTab({0}, {1});\">查看报告</a>".lym_format(row.project_id, row.build_no);
}


function view_task(value, row, index){
    return "<a href=\"#\" class=\"easyui-linkbutton\" data-options=\"iconCls:'icon-task'\" onclick=\"parent.addTaskTab('查看任务', '/task/{0}', 'icon-task');\">查看任务</a>".lym_format(row.id);
}

function manage_task(value, row, index){
    return "<a href=\"#\" class=\"easyui-linkbutton\" data-options=\"iconCls:'icon-task'\" onclick=\"\">查看任务</a>".lym_format(row.id);
}