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

function show_ui_step_win(win_id, fm_id, method){


    var button = {"create": "创建", "edit": "更新", "delete": "删除"};
    var selected = $('#project_tree').tree("getSelected");
    if(method == "create"){
        $('#{0}'.lym_format(win_id)).window({"title": "创建UI自动化测试步骤"});
        $('#{0} input#case_id'.lym_format(fm_id)).val(selected.attributes["id"]);

    }
    else if(method == "edit" || method == "delete"){
        $('#{0}'.lym_format(win_id)).window({"title": "管理UI自动化步骤"});
        $('#{0} input#id'.lym_format(fm_id)).val(selected.attributes["id"]);
        $('#{0} input#desc'.lym_format(fm_id)).textbox('setValue', selected.attributes["desc"]);
        $('#{0} input#keyword'.lym_format(fm_id)).combotree('setValue', selected.attributes["keyword"]);
        $('#{0} input#param_1'.lym_format(fm_id)).combotree('setValue', selected.attributes["param_1"]);
        $('#{0} input#param_2'.lym_format(fm_id)).combotree('setValue', selected.attributes["param_2"]);
        $('#{0} input#param_3'.lym_format(fm_id)).combotree('setValue', selected.attributes["param_3"]);
        $('#{0} input#param_4'.lym_format(fm_id)).combotree('setValue', selected.attributes["param_4"]);
    }
    else{
        show_msg("提示", "方法错误: ".lym_format(method));
        return;
    }
    $('#{0} input#method'.lym_format(fm_id)).val(method);
    $("#{0} a#manage_step".lym_format(fm_id)).linkbutton({'text': button[method]});


    open_win(win_id);
}

function manage_ui_step(win_id, fm_id){
    $.ajax({
        type : 'POST',
        url : '/api/v1/step/',
        data:  {
               "method": $('#{0} input#method'.lym_format(fm_id)).val(),
               "case_id": $('#{0} input#case_id'.lym_format(fm_id)).val(),
               "id": $('#{0} input#id'.lym_format(fm_id)).val(),
               "desc": $('#{0} input#desc'.lym_format(fm_id)).val(),
               "keyword": $('#{0} input#keyword'.lym_format(fm_id)).combotree('getText'),
               "param_1": $('#{0} input#param_1'.lym_format(fm_id)).combotree('getText'),
               "param_2": $('#{0} input#param_2'.lym_format(fm_id)).combotree('getText'),
               "param_3": $('#{0} input#param_3'.lym_format(fm_id)).combotree('getText'),
               "param_4": $('#{0} input#param_4'.lym_format(fm_id)).combotree('getText')
            },
        success : function(data, textStatus, request) {

            if(data.status == "success"){
                close_win('{0}'.lym_format(win_id));
                var root = $('#project_tree').tree("getRoot");
                load_project_tree(root.attributes.id);
            }
            show_msg("提示", data.msg);
        }
    });
}

function manage_ui_step_table(win_id, fm_id, method){


    var button = {"create": "创建", "edit": "更新", "delete": "删除"};
    if(method == "create"){
        $('#{0}'.lym_format(win_id)).window({"title": "创建UI自动化测试步骤"});
    }
    else if(method == "edit" || method == "delete"){
        var row = $('#ui_step_list').datagrid('getSelected');
        if(row){
            console.log(row);
            $('#{0}'.lym_format(win_id)).window({"title": "管理UI自动化步骤"});
            $('#{0} input#id'.lym_format(fm_id)).val(row["id"]);
            $('#{0} input#desc'.lym_format(fm_id)).textbox('setValue', row["备注"]);
            $('#{0} input#keyword'.lym_format(fm_id)).combotree('setValue', row["关键字"]);
            $('#{0} input#param_1'.lym_format(fm_id)).combotree('setValue', row["参数1"]);
            $('#{0} input#param_2'.lym_format(fm_id)).combotree('setValue', row["参数2"]);
            $('#{0} input#param_3'.lym_format(fm_id)).combotree('setValue', row["参数3"]);
            $('#{0} input#param_4'.lym_format(fm_id)).combotree('setValue', row["参数4"]);
        }
    }
    else{
        show_msg("提示", "方法错误: ".lym_format(method));
        return;
    }
    $('#{0} input#method'.lym_format(fm_id)).val(method);
    $("#{0} a#manage_step".lym_format(fm_id)).linkbutton({'text': button[method]});


    open_win(win_id);
}

function manage_frame_ui_step(win_id, fm_id){
    $.ajax({
        type : 'POST',
        url : '/api/v1/step/',
        data:  {
               "method": $('#{0} input#method'.lym_format(fm_id)).val(),
               "case_id": $('#{0} input#case_id'.lym_format(fm_id)).val(),
               "id": $('#{0} input#id'.lym_format(fm_id)).val(),
               "desc": $('#{0} input#desc'.lym_format(fm_id)).val(),
               "keyword": $('#{0} input#keyword'.lym_format(fm_id)).combotree('getText'),
               "param_1": $('#{0} input#param_1'.lym_format(fm_id)).combotree('getText'),
               "param_2": $('#{0} input#param_2'.lym_format(fm_id)).combotree('getText'),
               "param_3": $('#{0} input#param_3'.lym_format(fm_id)).combotree('getText'),
               "param_4": $('#{0} input#param_4'.lym_format(fm_id)).combotree('getText')
            },
        success : function(data, textStatus, request) {

            if(data.status == "success"){
                close_win('{0}'.lym_format(win_id));
                var root = parent.$('#project_tree').tree("getRoot");
                parent.load_project_tree(root.attributes.id);
                $("#ui_step_list").datagrid('reload');
            }
            show_msg("提示", data.msg);
        }
    });
}

function onShowFrameKeywordPanel(){
    var root = parent.$('#project_tree').tree("getRoot");
    var keyword=[];
    for(var i in G_SYS_KEYWORD_LIST){
        keyword.push(G_SYS_KEYWORD_LIST[i]);
    }
    if(root){
        $(this).combotree('reload', "/api/v1/keyword/?project_id={0}".lym_format(root.id));
    }
}