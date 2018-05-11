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
        if(value.indexOf("<a") != -1){
            console.log(row);
            return "<a href=\"#\" class=\"easyui-linkbutton\" onclick=\"parent.addViewImageTab({0}, {1}, '{2}');\">查看截图</a>".lym_format(row.project_id, row.build_no, row.image);
        }
        else{
            return value;
        }
    }

    return;
}