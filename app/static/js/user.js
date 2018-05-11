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

function init_role_list(){
    $.ajax({
        type : 'get',
        url : '/api/v1/role/',
        success : function(data, textStatus, request) {
            $('#create_user_fm select#role_id').combobox("loadData", data["rows"]);
            $('#edit_user_fm select#role_id').combobox("loadData", data["rows"]);
            $('#del_user_fm select#role_id').combobox("loadData", data["rows"]);
        }
    });

}

function manage_user(win_id, fm_id){
    $('#{0}'.lym_format(fm_id)).form('submit',{
        url: "/api/v1/user/",
        type: "post",
        success:function(data){
            var obj = JSON.parse(data);
            if(obj.status == "success"){
                $("#user_list").datagrid('reload');

                close_win('{0}'.lym_format(win_id));
            }
            show_msg("提示", obj.msg);
        }
    });
}

function edit_user(){
    var row = $('#user_list').datagrid('getSelected');
    if (row){
        $("#edit_user_fm input[name='id']").val(row["id"]);
        $("#edit_user_fm select#role_id").combobox('select', row["role_id"]);
        $("#edit_user_fm input#username").textbox('setValue', row["用户名"]);
        $("#edit_user_fm input#email").textbox('setValue', row["email"]);
        open_win('edit_user_win');
    }
    else{
        show_msg("提示", "请选择要编辑的用户");
    }
}

function delete_user(){
    var row = $('#user_list').datagrid('getSelected');
    if (row){
        $("#del_user_fm input[name='id']").val(row["id"]);
        $("#del_user_fm select#role_id").combobox('select', row["role_id"]);
        $("#del_user_fm input#username").textbox('setValue', row["用户名"]);
        $("#del_user_fm input#email").textbox('setValue', row["email"]);
        open_win('del_user_win');
    }
    else{
        show_msg("提示", "请选择要删除的用户");
    }
}