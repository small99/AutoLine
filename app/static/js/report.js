function show_status_style(value, row, index){
    if(value == "pass"){
        return '<font color="green">{0}</font>'.lym_format(value);
    }
    else{
        return '<font color="red">{0}</font>'.lym_format(value);
    }
}


function show_log_style(value, row, index){

    if(value != undefined){
        if(row.image != ""){
            return "{0}<a href=\"#\" class=\"easyui-linkbutton\" onclick=\"parent.addViewImageTab({1}, {2}, '{3}');\">查看截图</a>".lym_format(row.msg, row.project_id, row.build_no, row.image);
        }
        else{
            return value;
        }
    }

    return;
}