/*
 * autobeat.js
 *
 * 作者: 苦叶子
 *
 * 公众号: 开源优测
 *
 * Email: lymking@foxmail.com
 *
*/
function open_win(id){
    $('#{0}'.lym_format(id)).window('open');
}

function close_win(id){
    $('#{0}'.lym_format(id)).window('close');
}

function show_obj_win(win_id, fm_id, method){
    var button = {"create": "创建", "edit": "更新", "delete": "删除"};
    var selected = $('#project_tree').tree("getSelected");
    if(method == "create"){
        $('#{0}'.lym_format(win_id)).window({"title": "创建对象集"});
        $('#{0} input#project_id'.lym_format(fm_id)).val(selected.attributes["id"]);

    }
    else if(method == "edit" || method == "delete"){
        $('#{0}'.lym_format(win_id)).window({"title": "管理对象集"});
        $('#{0} input#id'.lym_format(fm_id)).val(selected.attributes["id"]);
        $('#{0} input#name'.lym_format(fm_id)).textbox('setValue', selected.attributes["name"]);
        $('#{0} input#desc'.lym_format(fm_id)).textbox('setValue', selected.attributes["desc"]);
    }
    else{
        show_msg("提示", "方法错误: ".lym_format(method));
        return;
    }
    $('#{0} input#method'.lym_format(fm_id)).val(method);
    $("#{0} a".lym_format(fm_id)).linkbutton({'text': button[method]});

    open_win(win_id);
}

function manage_object(win_id, fm_id){
    $('#{0}'.lym_format(fm_id)).form('submit',{
        url: "/api/v1/object/",
        type: "post",
        success:function(data){
            var obj = JSON.parse(data);
            if(obj.status == "success"){
                close_win('{0}'.lym_format(win_id));
                load_project_tree(obj.project_id);
            }
            show_msg("提示", obj.msg);
        }
    });
}


function manage_frame_object(win_id, fm_id){
    $('#{0}'.lym_format(fm_id)).form('submit',{
        url: "/api/v1/object/",
        type: "post",
        success:function(data){
            var obj = JSON.parse(data);
            if(obj.status == "success"){
                close_win('{0}'.lym_format(win_id));
                parent.load_project_tree(obj.project_id);
                $("#object_list").datagrid('reload');
            }
            show_msg("提示", obj.msg);
        }
    });
}

function manage_object_table(win_id, fm_id, method){
    var button = {"create": "创建", "edit": "更新", "delete": "删除"};

    if(method == "create"){
        $('#{0}'.lym_format(win_id)).window({"title": "创建对象集"});

    }
    else if(method == "edit" || method == "delete"){
        var row = $('#object_list').datagrid('getSelected');
        if(row){
            $('#{0}'.lym_format(win_id)).window({"title": "管理对象集"});
            $('#{0} input#id'.lym_format(fm_id)).val(row["id"]);
            $('#{0} input#project_id'.lym_format(fm_id)).val(row["project_id"]);
            $('#{0} input#name'.lym_format(fm_id)).textbox('setValue', row["名称"]);
            $('#{0} input#desc'.lym_format(fm_id)).textbox('setValue', row["描述"]);
        }
        else{
        show_msg("提示", "请选择要管理的对象集");
    }
    }
    else{
        show_msg("提示", "方法错误: ".lym_format(method));
        return;
    }
    $('#{0} input#method'.lym_format(fm_id)).val(method);
    $("#{0} a".lym_format(fm_id)).linkbutton({'text': button[method]});

    open_win(win_id);
}
