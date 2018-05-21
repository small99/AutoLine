var dynamicColors = function() {
    var r = Math.floor(Math.random() * 255);
    var g = Math.floor(Math.random() * 255);
    var b = Math.floor(Math.random() * 255);
    return "rgb(" + r + "," + g + "," + b + ")";
}


function project_stats(id){
    $.ajax({
        type : 'get',
        url : '/api/v1/stats/',
        data:  {
               "category": "project_stats"
            },
        success : function(data, textStatus, request) {
            var backcolor = [];
            for(var i=0; i<data.data.length; i++){
                backcolor.push(dynamicColors());
            }

            var ctx = document.getElementById(id).getContext('2d');
            var chart = new Chart(ctx,{
                type: 'pie',

                data: {
                    datasets: [
                    { data: data.data,
                     backgroundColor: backcolor}
                    ],
                    labels: data.label
                }
            });
        }
    });
}

function task_stats(id){
    $.ajax({
        type : 'get',
        url : '/api/v1/stats/',
        data:  {
               "category": "task_stats"
            },
        success : function(data, textStatus, request) {
            var backcolor = [];
            for(var i=0; i<data.data.length; i++){
                backcolor.push(dynamicColors());
            }

            var ctx = document.getElementById(id).getContext('2d');
            var chart = new Chart(ctx,{
                type: 'pie',

                data: {
                    datasets: [{
                        data: data.data,
                        backgroundColor: backcolor
                    }],
                    labels: data.label
                }
            });
        }
    });
}

function exec_stats(id){
    $.ajax({
        type : 'get',
        url : '/api/v1/stats/',
        data:  {
               "category": "exec_stats"
            },
        success : function(data, textStatus, request) {
            var backcolor = [];
            for(var i=0; i<data.data.length; i++){
                backcolor.push(dynamicColors());
            }

            var ctx = document.getElementById(id).getContext('2d');
            var chart = new Chart(ctx,{
                type: 'pie',

                data: {
                    datasets: [{
                        data: data.data,
                        backgroundColor: ["green", "blue", "red", "yellow"]
                    }],
                    labels: data.label
                }
            });
        }
    });
}