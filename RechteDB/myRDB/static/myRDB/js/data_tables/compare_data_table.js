function check_for_row_in_user_and_transfer_table(row,data,dataIndex){
    var data_table = window.user_table_data;
    var data_table_stripped = data_table.replace(/(&#39;)|(\s)/g,"");
    var data_str = "("+data[0]+","+data[1]+","+data[2]+","+data[3]+",";

    var contains = data_table_stripped.includes(data_str.replace(/(&#39;)|(\s)/g,""));
    if(contains){
        $(row).addClass("yellow");
    }
    data_table = window.transfer_table_data;
    data_table_stripped = data_table.replace(/(&#39;)|(\s)/g,"");
    contains = data_table_stripped.includes(data_str.replace(/(&#39;)|(\s)/g,""));
    if(contains){
        $(row).addClass("yellow");
    }
}

$(document).ready(function() {
    $('#compare_data_table tbody tr').each( function() {
        var sTitle;
        console.log(this);
        var user_data = window.compare_jsondata;

        loop1: for (i in user_data['children']){
            var rollen = user_data['children'][i]['children'];
            for(j in rollen){
                if(rollen[j]['name']===this.lastElementChild.previousElementSibling.textContent){
                    var rolle = rollen[j];
                    var afs = rolle['children'];
                    for(k in afs){
                        if(afs[k]['name']===this.lastElementChild.previousElementSibling.previousElementSibling.textContent){
                            var af = afs[k];
                            var gfs = af['children'];
                            for(l in gfs){
                                if(gfs[l]['name']===this.firstElementChild.nextElementSibling.textContent){
                                    var gf = gfs[l];
                                    var tfs = gf['children'];
                                    for(m in tfs){
                                        if(tfs[m]['name']===this.firstElementChild.textContent){
                                            var tf = tfs[m];
                                            break loop1;
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        var text = "Rolle: "+rolle['name']+" / Rollen-Beschreibung: "+ rolle['description']
            +"\nAF: "+af['name']+ " / AF-Beschreibung: "+af['description']
            +"\nGF: "+gf['name']+ " / GF-Beschreibung: "+gf['description']
            +"\nTF: "+tf['name']+ " / TF-Beschreibung: "+tf['description'];

        this.setAttribute( 'title', text );
    } );

    compare_data_table = $('#compare_data_table').DataTable({
        "pageLength":10,
        "scrollY": "70vh",
        "aLengthMenu":[[10,25,50,100,-1],[10,25,50,100,"All"]],
        "createdRow":function (row, data, dataIndex) {
            check_for_row_in_user_and_transfer_table(row,data,dataIndex);
        },
        "order":[[2,'asc']]
    });

    compare_data_table.$('tr').tooltip();

    function check_for_parent_existance(type, parent, grandparent){
        var data_table = window.transfer_table_data;
        var data_table_stripped = data_table.replace(/(&#39;)|(\s)/g,"");
        if(type==="gf"){
            var contains = data_table_stripped.includes(parent);
            if(contains){
                return true;
            }
            else{
                data_table = window.user_table_data;
                data_table_stripped = data_table.replace(/(&#39;)|(\s)/g,"");
                contains = data_table_stripped.includes(parent);
                if(contains){
                    return true;
                }
                bootbox.alert("GF kann nicht übertragen werden!\n\nUser besitzt nicht die nötige AF!", function () {
                    console.log("GF kann nicht übertragen werden!\n\nUser besitzt nicht die nötige AF!");
                });
                return false;
            }

        }
        if(type==="tf"){
            var contains = data_table_stripped.includes(grandparent);
            if(contains){
                contains = data_table_stripped.includes(parent);
                if(contains) {
                    return true;
                }
                else{
                    bootbox.alert("TF kann nicht übertragen werden!\n\nUser besitzt benötigte AF\naber nicht die nötige GF!", function () {
                        console.log("TF kann nicht übertragen werden!\n\nUser besitzt benötigte AF\naber nicht die nötige GF!");
                    });
                    return false;
                }
            }
            else{
                data_table = window.user_table_data;
                data_table_stripped = data_table.replace(/(&#39;)|(\s)/g,"");
                contains = data_table_stripped.includes(grandparent);
                if(contains){
                    contains = data_table_stripped.includes(parent);
                    if(contains) {
                        return true;
                    }
                    else{
                        bootbox.alert("TF kann nicht übertragen werden!\n\nUser besitzt benötigte AF\naber nicht die nötige GF!", function () {
                            console.log("TF kann nicht übertragen werden!\n\nUser besitzt benötigte AF\naber nicht die nötige GF!");
                        });
                        return false;
                    }
                }
                bootbox.alert("TF kann nicht übertragen werden!\n\nUser besitzt nicht die nötige AF!", function () {
                    console.log("TF kann nicht übertragen werden!\n\nUser besitzt nicht die nötige AF!");
                });
                return false;
            }
        }
    }

    $('#compare_data_table tbody').on('contextmenu', 'td', function (e) {
        e.preventDefault();

        var cell_data = window.compare_data_table.cell( this ).data();
        var colIndex = window.compare_data_table.cell(this).index().column;
        var rowIndex = window.compare_data_table.cell( this ).index().row;
        var row_data=window.compare_data_table.row(rowIndex).data();

        var row_node = window.compare_data_table.row(rowIndex).node();
        var right_type="",right_parent = "",right_grandparent = "";
        if(colIndex===0){
            right_type="tf";
            right_grandparent = row_data[2];
            right_parent = row_data[1];
        }else if (colIndex===1){
            right_type="gf";
            right_parent = row_data[2];
        }else if (colIndex===2){
            right_type="af";
        }
        if(right_type!=="af"&&!check_for_parent_existance(right_type,right_parent,right_grandparent)){
            return;
        }
        //console.log(this.parentElement.className);
        if(!(this.parentElement.className==="yellow even")&&!(this.parentElement.className==="yellow odd")){
            var r = confirm("Berechtigung:\n\n"+cell_data+"\n\nwirklich zu Transferliste hinzufügen?\n\n");
        }else{
            bootbox.alert("Berechtigung existiert bereits!\n", function () {
                console.log("Berechtigung existiert bereits!\n");
            });
            return;
        }
        if (r === true){

            function getCookie(name) {
                var cookieValue = null;
                if (document.cookie && document.cookie !== '') {
                    var cookies = document.cookie.split(';');
                    for (var i = 0; i < cookies.length; i++) {
                        var cookie = jQuery.trim(cookies[i]);
                        // Does this cookie string begin with the name we want?
                        if (cookie.substring(0, name.length + 1) === (name + '=')) {
                            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                            break;
                        }
                    }
                }
                return cookieValue;
            }
            function csrfSafeMethod(method) {
                // these HTTP methods do not require CSRF protection
                return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
            }
            $.ajaxSetup({
                beforeSend: function(xhr, settings) {
                    if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                        xhr.setRequestHeader("X-CSRFToken", getCookie("csrftoken"));
                    }
                }
            });
            var data = {"X-CSRFToken":getCookie("csrftoken"),"X_METHODOVERRIDE":'PATCH',"user":window.user,"compare_user":window.compare_user,"action_type":"transfer","right_type":right_type,"right_name":cell_data,"parent":right_parent,"grandparent":right_grandparent};
            var successful=false;
            $.ajax({type:'POST',
                    data:data,
                    url:'http://127.0.0.1:8000/users/'+window.user+'/',
                    async:false,
                    success: function(res){console.log(res);
                        bootbox.alert("Berechtigung zur\n\nTransferliste hinzugefügt\n", function () {
                            console.log("Berechtigung zur\n\nTransferliste hinzugefügt\n");
                        });
                        successful=true},
                    error: function(res){console.log(res);}
                    });
            if(successful===true){
                console.log("success!");
                update_table_data(cell_data,right_type,row_data);
            }
        }
    } ).on('mouseenter', 'td', function (e) {
        e.preventDefault();
        var colIndex = window.compare_data_table.cell(this).index().column;
        $(window.compare_data_table.cells().nodes()).removeClass('highlight');
        //$(window.compare_data_table.column(colIndex).nodes()).addClass('highlight');
    });
    function update_table_data(cell_data,right_type,row_data) {
        if (right_type==="af"){
            window.compare_data_table.rows().every(function(rowIdx,tableLoop,rowLoop){
               var data = this.data();
               if(data[2]===cell_data){
                   this.nodes().to$().addClass("yellow");
                   window.transfer_table.row.add(data).draw();
                   window.transfer_table_count+=1;
                   document.getElementById('transfer_badge').innerHTML = window.transfer_table_count;
               }
            });
        }
        if (right_type==="gf"){
            window.compare_data_table.rows().every(function(rowIdx,tableLoop,rowLoop){
               var data = this.data();
               if(data[1]===cell_data&&data[2]===row_data[2]){
                   this.nodes().to$().addClass("yellow");
                   window.transfer_table.row.add(data).draw();
                   window.transfer_table_count+=1;
                   document.getElementById('transfer_badge').innerHTML = window.transfer_table_count;
               }
            });

        }
        //TODO: noch so ändern, dass row nicht ers gesucht werden muss sondern direkt getransfert wird!
        if (right_type==="tf"){
            window.compare_data_table.rows().every(function(rowIdx,tableLoop,rowLoop){
               var data = this.data();
               if(data[0]===cell_data&&data[1]===row_data[1]&&data[2]===row_data[2]){
                   this.nodes().to$().addClass("yellow");
                   window.transfer_table.row.add(data).draw();
                   window.transfer_table_count+=1;
                   document.getElementById('transfer_badge').innerHTML = window.transfer_table_count;
               }
            });
        }
    }
} );