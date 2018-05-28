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

/*
 * 全局变量
*/
var G_SYS_KEYWORD_LIST = null;

/*
 * for string format
*/
String.prototype.lym_format = function() {
    if (arguments.length == 0) {
        return this;
    }
    for (var StringFormat_s = this, StringFormat_i = 0; StringFormat_i < arguments.length; StringFormat_i++) {
        StringFormat_s = StringFormat_s.replace(new RegExp("\\{" + StringFormat_i + "\\}", "g"), arguments[StringFormat_i]);
    }
    return StringFormat_s;
}

/*
 * for form to json
*/
$.fn.serializeObject = function() {
    var json = {};
    var arrObj = this.serializeArray();
    $.each(arrObj, function() {
      if (json[this.name]) {
           if (!json[this.name].push) {
            json[this.name] = [ json[this.name] ];
           }
           json[this.name].push(this.value || '');
      } else {
           json[this.name] = this.value || '';
      }
    });

    return json;
};

(function($){

});

function init_project_list(){
    $.ajax({
        type : 'POST',
        url : '/api/v1/project/',
        data:  {
               "method": "query",
               "id": "-2"
            },
        success : function(data, textStatus, request) {
            $('select#project_list').combobox("loadData", data["rows"]);
            }
    });

    $('select#project_list').combobox({
	onSelect: function(record){
	    load_project_tree(record["id"]);
	    var tabs = $("#editor_tabs").tabs('tabs');
	    var titles = new Array("开始", "产品管理", "项目管理", "调度管理","系统设置");
	    for(var index=0;index<tabs.length; index++){
	        var title = $("#editor_tabs").tabs('getTab', index).panel('options').title;
	        var flag = false;
	        for(var t in titles){
	            if(titles[t] == title) {
	                flag=true;
	            }
	        }
	        if(!flag){
	            $("#editor_tabs").tabs('close', title);
	        }
	    }
	}
});
}

function load_project_tree(id){
   $.ajax({
        type : 'get',
        url : '/api/v1/project/',
        data:  {
               "id": id
            },
        success : function(data, textStatus, request) {
            $('#project_tree').tree("loadData", data);
            }
    });
}

function onShowKeywordPanel(){
    var root = $('#project_tree').tree("getRoot");
    var keyword=[];
    for(var i in G_SYS_KEYWORD_LIST){
        keyword.push(G_SYS_KEYWORD_LIST[i]);
    }
    if(root){
        $(this).combotree('reload', "/api/v1/keyword/?project_id={0}".lym_format(root.id));
    }
}

function onContextMenu(e, node){
    e.preventDefault();
    // select the node
    $('#project_tree').tree('select', node.target);
    // display context menu

    $('#{0}_menu'.lym_format(node.attributes['category'])).menu('show', {
        left: e.pageX,
        top: e.pageY
    });
}

function onDblClick(node) {
    if(node.attributes["category"]=="object"){
        addManageTab('对象管理', '/manage/var', 'icon-var');
    }
    else if(node.attributes["category"]=="suite"){
        addManageTab('用例管理', '/manage/case', 'icon-case');
    }
    else if(node.attributes["category"]=="case"){
        addManageTab('用例步骤', '/manage/step', 'icon-step');
    }
    else if(node.attributes["category"]=="var"){
        show_var_win('var_win', 'var_fm', 'edit');
    }
    else if(node.attributes["category"]=="step"){
        show_ui_step_win('ui_step_win', 'ui_step_fm', 'edit');
    }
}

function addTab(title, url, icon){
    var editor_tabs = $("#editor_tabs");
    if (editor_tabs.tabs('exists', title)){
        //如果tab已经存在,则选中并刷新该tab
        editor_tabs.tabs('select', title);
        refreshTab({title: title, url: url});
    }
    else {
        var content='<iframe scrolling="yes" frameborder="0"  src="{0}" style="width:100%;height:700px;"></iframe>'.lym_format(url);
        editor_tabs.tabs('add',{
            title: title,
            closable: true,
            content: content,
            iconCls: icon||'icon-default'
        });
    }
}

function refreshTab(cfg){
    var tab = cfg.title?$('#editor_tabs').tabs('getTab',cfg.title):$('#editor_tabs').tabs('getSelected');
    if(tab && tab.find('iframe').length > 0){
        var frame = tab.find('iframe')[0];
        var url = cfg.url?cfg.url:fram.src;
        frame.contentWindow.location.href = url;
    }
}

function addManageTab(title, url, icon){
    var selected = $('#project_tree').tree('getSelected');
    var editor_tabs = $("#editor_tabs");
    if (editor_tabs.tabs('exists', title)){
        //如果tab已经存在,则选中并刷新该tab
        editor_tabs.tabs('select', title);
        refreshTab({title: title, url: "{0}/{1}".lym_format(url,selected.attributes["id"])});
    }
    else {
        var content='<iframe scrolling="yes" frameborder="0"  src="{0}/{1}" style="width:100%;height:700px;"></iframe>'.lym_format(url, selected.attributes["id"]);

        editor_tabs.tabs('add',{
            title: title,
            closable: true,
            content: content,
            iconCls: icon||'icon-default'
        });
    }
}

function addReportTab(project_id, build_no){
    var editor_tabs = $("#editor_tabs");
    var url = "/report/{0}/{1}".lym_format(project_id, build_no)
    if (editor_tabs.tabs('exists', '详细报告')){
        //如果tab已经存在,则选中并刷新该tab
        editor_tabs.tabs('select', '详细报告');
        refreshTab({title: title, url: url});
    }
    else {
        var content='<iframe scrolling="yes" frameborder="0"  src="{0}" style="width:100%;height:960px;"></iframe>'.lym_format(url);
        editor_tabs.tabs('add',{
            title: '详细报告',
            closable: true,
            content: content,
            iconCls: 'icon-report'
        });
    }
}

function addLogTab(project_id, build_no){
    var editor_tabs = $("#editor_tabs");
    var url = "/run_logs/{0}/{1}".lym_format(project_id, build_no)
    if (editor_tabs.tabs('exists', '查看日志')){
        //如果tab已经存在,则选中并刷新该tab
        editor_tabs.tabs('select', '查看日志');
        refreshTab({title: title, url: url});
    }
    else {
        var content='<iframe scrolling="yes" frameborder="0"  src="{0}" style="width:100%;height:740px;"></iframe>'.lym_format(url);
        editor_tabs.tabs('add',{
            title: '查看日志',
            closable: true,
            content: content,
            iconCls: 'icon-report'
        });
    }
}

function addTaskTab(title, url, icon){
    var editor_tabs = $("#editor_tabs");
    if (editor_tabs.tabs('exists', title)){
        //如果tab已经存在,则选中并刷新该tab
        editor_tabs.tabs('select', title);
        refreshTab({title: title, url: url});
    }
    else {
        var content='<iframe scrolling="yes" frameborder="0"  src="{0}" style="width:100%;height:700px;"></iframe>'.lym_format(url);

        editor_tabs.tabs('add',{
            title: title,
            closable: true,
            content: content,
            iconCls: icon || 'icon-task'
        });
    }
}

function addViewImageTab(project_id, build_no, filename){
    var editor_tabs = $("#editor_tabs");
    var url = "/view_image/{0}/{1}/{2}".lym_format(project_id, build_no, filename)
    if (editor_tabs.tabs('exists', '查看截图')){
        //如果tab已经存在,则选中并刷新该tab
        editor_tabs.tabs('select', '查看截图');
        refreshTab({title: title, url: url});
    }
    else {
        var content='<iframe scrolling="yes" frameborder="0"  src="{0}" style="width:100%;height:1024px;"></iframe>'.lym_format(url);
        editor_tabs.tabs('add',{
            title: '查看截图',
            closable: true,
            content: content,
            iconCls: 'icon-report'
        });
    }
}

function open_win(id){
    $('#{0}'.lym_format(id)).window('open');
}

function close_win(id){
    $('#{0}'.lym_format(id)).window('close');
}

function show_msg(title, msg){
    $.messager.show({
        title: title,
        msg: msg,
        timeout: 3000,
        showType: 'slide'
    });
}

function collapse(){
    var node = $('#project_tree').tree('getSelected');
    $('#project_tree').tree('collapse',node.target);
}

function expand(){
    var node = $('#project_tree').tree('getSelected');
    $('#project_tree').tree('expand',node.target);
}

function test_run(category){
    var node = $('#project_tree').tree('getRoot');
    if(node){
        $.ajax({
            type : 'get',
            url : '/test_run/{0}/{1}'.lym_format(category, node.attributes["id"]),
            success : function(data, textStatus, request) {
                var d = JSON.parse(data);
                if(d["status"] == "success"){

                    show_msg("提示信息", d["msg"]);
                    addManageTab('查看任务', '/task', 'icon-task');
                }
                else{
                    show_msg("提示信息", d["msg"]);
                }
            }
        });
    }
}

function test_frame_run(id, category){
    $.ajax({
        type : 'get',
        url : '/test_run/{0}/{1}'.lym_format(category, id),
        success : function(data, textStatus, request) {
            var d = JSON.parse(data);
            if(d["status"] == "success"){
                show_msg("提示信息", d["msg"]);
                parent.addTaskTab('查看任务', '/task/{0}'.lym_format(id), 'icon-task');
            }
            else{
                show_msg("提示信息", d["msg"]);
            }
        }
    });
}

function debug_run(){
    var node = $('#project_tree').tree('getSelected');
    addTaskTab("调试运行", "/debug/{0}".lym_format(node.attributes["id"]), "icon-debug");
}