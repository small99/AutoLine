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

function manage_product(win_id, fm_id){
    $('#{0}'.lym_format(fm_id)).form('submit',{
        url: "/api/v1/product/",
        type: "post",
        success:function(data){
            var obj = JSON.parse(data);
            if(obj.status == "success"){
                $("#product_list").datagrid('reload');
                parent.init_project_list();
                close_win('{0}'.lym_format(win_id));
            }
            show_msg("提示", obj.msg);
        }
    });
}

function edit_product(){
    var row = $('#product_list').datagrid('getSelected');
    if (row){
        $("#edit_product_fm input[name='id']").val(row["id"]);
        $("#edit_product_fm input#name").textbox('setValue', row["名称"]);
        $("#edit_product_fm input#desc").textbox('setValue', row["描述"]);
        open_win('edit_product_win');
    }
    else{
        show_msg("提示", "请选择要编辑的产品");
    }
}

function delete_product(){
    var row = $('#product_list').datagrid('getSelected');
    if (row){
        $("#del_product_fm input[name='id']").val(row["id"]);
        $("#del_product_fm input#name").textbox('setValue', row["名称"]);
        $("#del_product_fm input#desc").textbox('setValue', row["描述"]);
        open_win('del_product_win');
    }
    else{
        show_msg("提示", "请选择要删除的产品");
    }
}