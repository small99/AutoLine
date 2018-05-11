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

function show_case_win(win_id, fm_id, method){
    var button = {"create": "创建", "edit": "更新", "delete": "删除"};
    var selected = $('#project_tree').tree("getSelected");
    if(method == "create"){
        $('#{0}'.lym_format(win_id)).window({"title": "创建用例集"});
        $('#{0} input#suite_id'.lym_format(fm_id)).val(selected.attributes["id"]);

    }
    else if(method == "edit" || method == "delete"){
        $('#{0}'.lym_format(win_id)).window({"title": "管理用例集"});
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

function manage_case(win_id, fm_id){
    $('#{0}'.lym_format(fm_id)).form('submit',{
        url: "/api/v1/case/",
        type: "post",
        success:function(data){
            var obj = JSON.parse(data);
            if(obj.status == "success"){
                close_win('{0}'.lym_format(win_id));
                var root = $('#project_tree').tree("getRoot");
                load_project_tree(root.attributes.id);
            }
            show_msg("提示", obj.msg);
        }
    });
}


function manage_frame_case(win_id, fm_id){
    $('#{0}'.lym_format(fm_id)).form('submit',{
        url: "/api/v1/case/",
        type: "post",
        success:function(data){
            var obj = JSON.parse(data);
            if(obj.status == "success"){
                close_win('{0}'.lym_format(win_id));
                var root = parent.$('#project_tree').tree("getRoot");
                parent.load_project_tree(root.attributes.id);
                $("#case_list").datagrid('reload');
            }
            show_msg("提示", obj.msg);
        }
    });
}

function manage_case_table(win_id, fm_id, method){
    var button = {"create": "创建", "edit": "更新", "delete": "删除"};

    if(method == "create"){
        $('#{0}'.lym_format(win_id)).window({"title": "创建用例"});

    }
    else if(method == "edit" || method == "delete"){
        var row = $('#case_list').datagrid('getSelected');
        if(row){
            $('#{0}'.lym_format(win_id)).window({"title": "管理用例"});
            $('#{0} input#id'.lym_format(fm_id)).val(row["id"]);
            $('#{0} input#project_id'.lym_format(fm_id)).val(row["project_id"]);
            $('#{0} input#name'.lym_format(fm_id)).textbox('setValue', row["名称"]);
            $('#{0} input#desc'.lym_format(fm_id)).textbox('setValue', row["描述"]);
        }
        else{
        show_msg("提示", "请选择要管理的用例");
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