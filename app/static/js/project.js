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

function init_product_list(){
    $.ajax({
        type : 'POST',
        url : '/api/v1/product/',
        data:  {
               "method": "query",
               "id": "-2"
            },
        success : function(data, textStatus, request) {
            $('#create_project_fm select#product_id').combobox("loadData", data["rows"]);
            $('#edit_project_fm select#product_id').combobox("loadData", data["rows"]);
            $('#del_project_fm select#product_id').combobox("loadData", data["rows"]);
        }
    });

}

function manage_project(win_id, fm_id){
    $('#{0}'.lym_format(fm_id)).form('submit',{
        url: "/api/v1/project/",
        type: "post",
        success:function(data){
            var obj = JSON.parse(data);
            if(obj.status == "success"){
                $("#project_list").datagrid('reload');
                parent.init_project_list();
                close_win('{0}'.lym_format(win_id));
            }
            show_msg("提示", obj.msg);
        }
    });
}

function edit_project(){
    var row = $('#project_list').datagrid('getSelected');
    console.log(row);
    if (row){
        $("#edit_project_fm input[name='id']").val(row["id"]);
        $("#edit_project_fm select#category").combobox('select', row["分类"]);
        $("#edit_project_fm select#product_id").combobox('select', row["product_id"]);
        $("#edit_project_fm input#name").textbox('setValue', row["名称"]);
        $("#edit_project_fm input#desc").textbox('setValue', row["描述"]);
        $("#edit_project_fm input#cron").textbox('setValue', row["cron"]);
        open_win('edit_project_win');
    }
    else{
        show_msg("提示", "请选择要编辑的项目");
    }
}

function delete_project(){
    var row = $('#project_list').datagrid('getSelected');
    if (row){
        $("#del_project_fm input[name='id']").val(row["id"]);
        $("#edit_project_fm select#category").combobox('select', row["分类"]);
        $("#del_project_fm select#product_id").combobox('select', row["product_id"]);
        $("#del_project_fm input#name").textbox('setValue', row["名称"]);
        $("#del_project_fm input#desc").textbox('setValue', row["描述"]);
        $("#del_project_fm input#cron").textbox('setValue', row["cron"]);
        open_win('del_project_win');
    }
    else{
        show_msg("提示", "请选择要删除的项目");
    }
}

function run_project_manage(value, row, index){
    console.log(row);
    return "<a href=\"#\" class=\"easyui-linkbutton\" data-options=\"iconCls:'icon-task'\" onclick=\"parent.test_frame_run('{0}', '{1}');\">运行</a>".lym_format(row.id, row["分类"]);
}