(function(){
$(document).ready(function(){
    var svgIndex = window.iUnequalModel;
    window.iUnequalModel=window.iUnequalModel+1;


    var svg = d3.select("#analysisModelCirclePackingSVG_unequal"+svgIndex),
        margin = 20,
        diameter = +svg.attr("width"),
        g = svg.append("g").attr("transform", "translate(" + diameter / 2 + "," + diameter / 2 + ")");

    var color = d3.scaleLinear()
        .domain([-1, 5])
        .range(["hsl(360,100%,100%)", "hsl(0,0%,0%)"])
        .interpolate(d3.interpolateHcl);


    var pack = d3.pack()
        .size([diameter - margin, diameter - margin])
        .padding(2);

    var data_root = window['jsonModeldata_unequal'+svgIndex];

      var root = d3.hierarchy(data_root)
          .sum(function(d) { return d.size; })
          .sort(function(a, b) { return b.value - a.value; });

      var focus = root,
          nodes = pack(root).descendants(),
          view;


          var div = d3.select("body").append("div")
          .attr("class","tooltip")
          .attr("id","compareCPtooltip")
          .style("opacity",0);

      //TODO: compare auch auf my_requests!
      function compare_graphs(d, compare_data, transferbool){
          if(transferbool){
              if (window.level === 'GF') {
                  for (var i in compare_data) {
                      var user_rollen = compare_data[i]['children'];
                      for (var j in user_rollen) {
                          if(user_rollen[j].name === d.parent.parent.parent.data.name){
                              var rollen_afs = user_rollen[j]['children'];
                              for (var k in rollen_afs) {
                                  if (rollen_afs[k].name === d.parent.parent.data.name){
                                      var af_gfs = rollen_afs[k]['children'];
                                      for(var l in af_gfs){
                                           if (af_gfs[l].name === d.parent.data.name){
                                               var gf_tfs = af_gfs[l]['children'];
                                               for(var m in gf_tfs){
                                                   if (gf_tfs[m].name === d.data.name) return true;
                                               }
                                           }
                                      }
                                  }
                              }
                          }
                      }
                  }
              }
              else if (window.level === 'AF') {
                  if(d.depth===1) {
                      for (i in compare_data) {
                          user_rollen = compare_data[i]['children'];
                          for (j in user_rollen) {
                              if( user_rollen[j].name === d.parent.parent.data.name){
                                  rollen_afs = user_rollen[j]['children'];
                                  for (k in rollen_afs) {
                                      if (rollen_afs[k].name === d.parent.data.name){
                                          af_gfs = rollen_afs[k]['children'];
                                          for(l in af_gfs){
                                               if (af_gfs[l].name === d.data.name)return true;
                                          }
                                      }
                                  }
                              }
                          }
                      }
                  }
                  if(d.depth===2) {
                      for (i in compare_data) {
                          user_rollen = compare_data[i]['children'];
                          for (j in user_rollen) {
                              if( user_rollen[j].name === d.parent.parent.parent.data.name){
                                  rollen_afs = user_rollen[j]['children'];
                                  for (k in rollen_afs) {
                                      if (rollen_afs[k].name === d.parent.parent.data.name){
                                          af_gfs = rollen_afs[k]['children'];
                                          for(l in af_gfs){
                                               if (af_gfs[l].name === d.parent.data.name){
                                                   gf_tfs = af_gfs[l]['children'];
                                                   for(m in gf_tfs){
                                                       if (gf_tfs[m].name === d.data.name) return true;
                                                   }
                                               }
                                          }
                                      }
                                  }
                              }
                          }
                      }
                  }
              }
              else if (window.level === 'ROLLE') {
                  if(d.depth===1) {
                      for (i in compare_data) {
                          user_rollen = compare_data[i]['children'];
                          for (j in user_rollen) {
                              if( user_rollen[j].name === d.parent.data.name){
                                  rollen_afs = user_rollen[j]['children'];
                                  for (k in rollen_afs) {
                                      if (rollen_afs[k].name === d.data.name) return true;
                                  }
                              }
                          }
                      }
                  }
                  if(d.depth===2) {
                      for (i in compare_data) {
                          user_rollen = compare_data[i]['children'];
                          for (j in user_rollen) {
                              if( user_rollen[j].name === d.parent.parent.data.name){
                                  rollen_afs = user_rollen[j]['children'];
                                  for (k in rollen_afs) {
                                      if (rollen_afs[k].name === d.parent.data.name){
                                          af_gfs = rollen_afs[k]['children'];
                                          for(l in af_gfs){
                                               if (af_gfs[l].name === d.data.name)return true;
                                          }
                                      }
                                  }
                              }
                          }
                      }
                  }
                  if(d.depth===3) {
                      for (i in compare_data) {
                          user_rollen = compare_data[i]['children'];
                          for (j in user_rollen) {
                              if( user_rollen[j].name === d.parent.parent.parent.data.name){
                                  rollen_afs = user_rollen[j]['children'];
                                  for (k in rollen_afs) {
                                      if (rollen_afs[k].name === d.parent.parent.data.name){
                                          af_gfs = rollen_afs[k]['children'];
                                          for(l in af_gfs){
                                               if (af_gfs[l].name === d.parent.data.name){
                                                   gf_tfs = af_gfs[l]['children'];
                                                   for(m in gf_tfs){
                                                       if (gf_tfs[m].name === d.data.name) return true;
                                                   }
                                               }
                                          }
                                      }
                                  }
                              }
                          }
                      }
                  }
              }
          }
          else{
              if(d.depth===1){
                  for(i in compare_data){
                      if(compare_data[i].name===d.data.name) return true;
                  }
              }
              else if (d.depth === 2){
                  for(i in compare_data){
                      if(compare_data[i].name===d.parent.data.name){
                          var level_2 = compare_data[i]['children'];
                          for(j in level_2){
                              if(level_2[j].name===d.data.name) return true;
                          }
                      }
                  }
              }
              else if (d.depth === 3){
                  for(i in compare_data){
                      if(compare_data[i].name===d.parent.parent.data.name){
                          var level_2 = compare_data[i]['children'];
                          for(j in level_2){
                              if(level_2[j].name===d.parent.data.name){
                                  var level_3 = level_2[j]['children'];
                                  for(k in level_3){
                                      if(level_3[k].name===d.data.name) return true;
                                  }
                              }
                          }
                      }
                  }
              }
              else if (d.depth === 4){
                  for(i in compare_data){
                      if(compare_data[i].name===d.parent.parent.parent.data.name){
                          var level_2 = compare_data[i]['children'];
                          for(j in level_2){
                              if(level_2[j].name===d.parent.parent.data.name){
                                  var level_3 = level_2[j]['children'];
                                  for(k in level_3){
                                      if(level_3[k].name===d.parent.data.name){
                                          var level_4 = level_3[k]['children'];
                                          for(l in level_4){
                                               if(level_4[l].name===d.data.name) return true;
                                          }
                                      }
                                  }
                              }
                          }
                      }
                  }
              }
          }
          return false;
      }
      function get_color(d, svgIndex) {
          if(d.depth===0){
              return "white";
          }
          else{
              var exists_in_compar_graph = compare_graphs(d,window['jsondata_unequal'+svgIndex]['children'],false);
              var exists_in_transfer_graph = compare_graphs(d,window.transferlistdata['children'], true);
              if(window.level === "ROLLE"){
                  if(exists_in_compar_graph||exists_in_transfer_graph){
                      d['exists'] = true;
                      if(d.depth===1)return "darkgrey";
                      if(d.depth===2)return "grey";
                      if(d.depth===3)return "lightgrey";
                  }else{
                      d['exists'] = false;
                      //if(d.depth===3){return d.data.tf_application.color}
                      if(d.depth===3){return d.data.color}
                      else{return "white"}
                  }
              }
              else if(window.level === "AF"){
                  if(exists_in_compar_graph||exists_in_transfer_graph){
                      d['exists'] = true;
                      if(d.depth===1)return "grey";
                      if(d.depth===2)return "lightgrey";
                  }else{
                      d['exists'] = false;
                      //if(d.depth===2){return d.data.tf_application.color}
                      if(d.depth===2){return d.data.color}
                      else{return "white"}
                  }
              }
              else if (window.level === "GF"){
                  if(exists_in_compar_graph||exists_in_transfer_graph){
                      d['exists'] = true;
                      if(d.depth===1)return "lightgrey";
                  }else{
                      d['exists'] = false;
                      //if(d.depth===1){return d.data.tf_application.color}
                      if(d.depth===1){return d.data.color}
                      else{return "white"}
                  }
              }
          }
      }
      function get_tooltip_text(d) {
          var text;
          if (window.level === "ROLLE") {
              if(d.depth === 1){
                  text = "<b>AF:</b> "+d.data.name+"<br/>"+"<b>AF-Beschreibung:</b> "+d.data.description
              }else if(d.depth === 2){
                  text = "<b>GF:</b> "+d.data.name+"<br/>"+ "<b>AF:</b> "+d.parent.data.name+"<br/>"+"<b>AF-Beschreibung:</b> "+d.parent.data.description
              }else if(d.depth === 3){
                  text = "<b>TF:</b> "+d.data.name+"<br/>"+"<b>GF:</b> "+d.parent.data.name+"<br/>"+ "<b>AF:</b> "+d.parent.parent.data.name+"<br/>"+"<b>AF-Beschreibung:</b> "+d.parent.parent.data.description
              }
          }else if (window.level === "AF") {
              if(d.depth === 1){
                  text = "<b>GF:</b> "+d.data.name+"<br/>"+ "<b>AF:</b> "+d.parent.data.name+"<br/>"+"<b>AF-Beschreibung:</b> "+d.parent.data.description
              }else if(d.depth === 2){
                  text = "<b>TF:</b> "+d.data.name+"<br/>"+"<b>GF:</b> "+d.parent.data.name+"<br/>"+ "<b>AF:</b> "+d.parent.parent.data.name+"<br/>"+"<b>AF-Beschreibung:</b> "+d.parent.parent.data.description
              }
          }else if(window.level === "GF"){
              if(d.depth === 1){
                  text = "<b>TF:</b> "+d.data.name+"<br/>"+"<b>GF:</b> "+d.parent.data.name+"<br/>"
              }
          }
          return text
      }

    //TODO: bei erstellen von json color für leaves mitgeben!!!
      var circle = g.selectAll("circle")
        .data(nodes)
        .enter().append("circle")
          .attr("class", function(d) { return d.parent ? d.children ? "node" : "node node--leaf" : "node node--root"; })
          .style("stroke","grey")
          .style("fill", function(d) {return get_color(d,svgIndex)})
          .on("click", function(d) { if(d3.event.defaultPrevented) return;
                console.log("clicked");
              if (focus !== d) zoom(d), d3.event.stopPropagation(); })
          .on("contextmenu",function(d,i){confirm_transfer(d,i,svgIndex)})
          .on("mouseover",function (d) {
              d3.select(this).style("stroke","black");
              div.transition()
                  .duration(200)
                  .style("opacity",9);
              var text = get_tooltip_text(d);
              div .html(text)
                  .style("left",(d3.event.pageX)+"px")
                  .style("top",(d3.event.pageY-28)+"px")
          })
          .on("mouseout",function (d) {
              d3.select(this).style("stroke","grey");
              div.transition()
                  .duration(500)
                  .style("opacity",0)
          });

        var node = g.selectAll("circle");

      svg
          .style("background", "white")
          .on("click", function() { zoom(root); });

      zoomTo([root.x, root.y, root.r * 2 + margin]);

      function zoom(d) {
          if (!d.hasOwnProperty('children')) return;
        var focus0 = focus; focus = d;

        var transition = d3.transition()
            .duration(d3.event.altKey ? 7500 : 750)
            .tween("zoom", function(d) {
              var i = d3.interpolateZoom(view, [focus.x, focus.y, focus.r * 2 + margin]);
              return function(t) { zoomTo(i(t)); };
            });
      }

      function zoomTo(v) {
        var k = diameter / v[2]; view = v;
        node.attr("transform", function(d) { return "translate(" + (d.x - v[0]) * k + "," + (d.y - v[1]) * k + ")"; });
        circle.attr("r", function(d) { return d.r * k; });
      }

    function update(updated_data,svgIndex){
          console.log(updated_data);
          root = updated_data;

          svg = d3.select("#analysisModelCirclePackingSVG_unequal"+svgIndex),
        margin = 20,
        diameter = +svg.attr("width"),
        g = svg.append("g").attr("transform", "translate(" + diameter / 2 + "," + diameter / 2 + ")");
/*
        color = d3.scaleLinear()
            .domain([-1, 5])
            .range(["hsl(360,100%,100%)", "hsl(0,0%,0%)"])
            .interpolate(d3.interpolateHcl);
*/

        pack = d3.pack()
            .size([diameter - margin, diameter - margin])
            .padding(2);
      root = d3.hierarchy(root)
          .sum(function(d) { return d.size; })
          .sort(function(a, b) { return b.value - a.value; });

      focus = root,
          nodes = pack(root).descendants(),
          view;

      var div = d3.select("body").append("div")
          .attr("class","tooltip")
          .attr("id","compareCPtooltip")
          .style("opacity",0);

    //TODO: bei erstellen von json color für leaves mitgeben!!!
      circle = g.selectAll("circle")
        .data(nodes)
        .enter().append("circle")
          .attr("class", function(d) { return d.parent ? d.children ? "node" : "node node--leaf" : "node node--root"; })
          .style("stroke","grey")
          .style("fill", function(d) {return get_color(d,svgIndex)})
          .on("click", function(d) { if(d3.event.defaultPrevented) return;
                console.log("clicked");
              if (focus !== d) zoom(d), d3.event.stopPropagation(); })
          .on("contextmenu", function(d,i){confirm_transfer(d,i,svgIndex)})
          .on("mouseover",function (d) {
              d3.select(this).style("stroke","black");
              div.transition()
                  .duration(200)
                  .style("opacity",9);
              var text = get_tooltip_text(d);
              div .html(text)
                  .style("left",(d3.event.pageX)+"px")
                  .style("top",(d3.event.pageY-28)+"px")
          })
          .on("mouseout",function (d) {
              d3.select(this).style("stroke","grey");
              div.transition()
                  .duration(500)
                  .style("opacity",0)
          });


        node = g.selectAll("circle");

      svg
          .style("background", "white")
          .on("click", function() { zoom(root); });

      zoomTo([root.x, root.y, root.r * 2 + margin]);
    }
    window.updateUnequalModelCP=function (originSvgIndex) {
        update(window['jsonModeldata_unequal'+originSvgIndex],originSvgIndex)
    };

    function check_user_rights_for_existance(d,right_type) {
        var exists_in_user_rights = false;
        var exists_in_transfer_rights = false;
        if(right_type==="af"){
            if (!d.exists){
                return false;
            }else{
                bootbox.alert("AF existiert bereits\nund kann nicht übertragen werden!");
                return true;
            }
        }
        if(right_type==="gf"){
            if(!d.exists){
                if(window.level === 'ROLLE'){
                    if(d.parent.exists){
                        return false
                    }
                    else{
                        bootbox.alert("GF kann nicht übertragen werden!\n\nUser besitzt nicht die nötige AF!");
                        return true;
                    }
                }
                if(window.level === 'AF'){
                    return false;
                }
            }else{
                bootbox.alert("GF existiert bereits\nund kann nicht übertragen werden!");
                return true;
            }
        }
        if(right_type==="tf") {
            if (!d.exists) {
                if(window.level === 'ROLLE'){
                    if (d.parent.exists && d.parent.parent.exists) {
                        return false;
                    }else if (!d.parent.exists && d.parent.parent.exists) {
                        bootbox.alert("TF kann nicht übertragen werden!\n\nUser besitzt benötigte AF\naber nicht die nötige GF!");
                        return true;
                    }else if (!d.parent.exists && !d.parent.parent.exists) {
                        bootbox.alert("TF kann nicht übertragen werden!\n\nUser besitzt nicht die benötigte AF!");
                        return true;
                    }
                }
                if(window.level === 'AF'){
                    if (d.parent.exists) {
                        return false;
                    }else{
                        bootbox.alert("TF kann nicht übertragen werden!\n\nUser besitzt benötigte AF\naber nicht die nötige GF!");
                        return true;
                    }
                }else if(window.level === 'GF'){
                    return false;
                }
            }else{
                bootbox.alert("TF existiert bereits\nund kann nicht übertragen werden!");
                return true;
            }
        }
    }
    function get_type_and_parents(d){
        var right_type="",right_parent = "",right_grandparent = "",right_greatgrandparent = "";
        if (window.level === "ROLLE") {
            if(d.depth===1) {
                right_type = "af";
                right_parent = d.parent.data.name;
            }
            else if(d.depth===2) {
                right_type="gf";
                right_parent = d.parent.data.name;
                right_grandparent = d.parent.parent.data.name;
            }
            else if(d.depth===3){
                right_type="tf";
                right_greatgrandparent = d.parent.parent.parent.data.name;
                right_grandparent = d.parent.parent.data.name;
                right_parent = d.parent.data.name;
            }
        }else if (window.level === "AF") {
            if(d.depth===1){
                right_type="gf";
                right_parent = d.parent.data.name;
                right_grandparent = d.parent.parent.data.name;
            }
            else if(d.depth===2) {
                right_type="tf";
                right_greatgrandparent = d.parent.parent.parent.data.name;
                right_grandparent = d.parent.parent.data.name;
                right_parent = d.parent.data.name;
            }
        }else if (window.level === "GF") {
            if(d.depth===1) right_type="tf";
            right_greatgrandparent = d.parent.parent.parent.data.name;
            right_grandparent = d.parent.parent.data.name;
            right_parent = d.parent.data.name;
        }
        return [right_type,right_parent,right_grandparent,right_greatgrandparent]
    }
    function confirm_transfer(d,i,svgIndex) {
        d3.event.preventDefault();
          bootbox.confirm("Berechtigung:\n\n"+d.data.name+"\n\nwirklich zu Transferliste hinzufügen?\n\n", function (result) {
                console.log('This was logged in the callback: ' + result);
                if(result===true){
                    transferfunction(d,i,svgIndex)
                }
            });
    }
    function transferfunction(d,i,svgIndex){
        var right_info = get_type_and_parents(d);
        if(check_user_rights_for_existance(d,right_info[0])){
            return;
        }
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

            var data = {"X-CSRFToken":getCookie("csrftoken"),"X_METHODOVERRIDE":'PATCH',"user_pk":window.user,
                "action_type":"analysis_transfer","right_type":right_info[0],"right_name":d.data.name,"right_pk":d.data.id,
                "parent":right_info[1],"grandparent":right_info[2],"greatgrandparent":right_info[3]};
            var successful=false;
            $.ajax({type:'POST',
                    data:data,
                    url:window.current_host+'/api/userhatuseridundnamen/'+window.user_userid_combi_id+'/',
                    async:false,
                    success: function(res){console.log(res);
                        successful=true},
                    error: function(res){console.log(res);}
                    });
            if(successful===true){
                var compare_rights = window['jsonModeldata_unequal'+svgIndex]['children'];
                var user_rights = window['jsondata_unequal'+svgIndex]['children'];
                var transfer = window.transferlistdata['children'];
                update_rights(user_rights,compare_rights, transfer, d);

                d3.select("body").selectAll("#compareCPtooltip").remove();

                d3.select('#transferSVG').select('g').data(window.transferlistdata).exit().remove();
                window.updateTransfer();

                d3.select("#analysisModelCirclePackingSVG_unequal"+svgIndex).select("g").data(window['jsonModeldata_unequal'+svgIndex]).exit().remove();
                update(window['jsonModeldata_unequal'+svgIndex],svgIndex);

                //d3.select('#circlePackingSVG').select('g').data(window.jsondata).exit().remove();
                //window.updateCP();
                bootbox.alert("Berechtigung zur\n\nTransferliste hinzugefügt\n");
                //update_session();
            }
            else{
                bootbox.alert('Beim Übertragen der Berechtigung\nist ein Fehler aufgetreten!')
            }

      }
      function update_right_counters(right,type){
        if (type === "af"){
            for (j in right['children']){
                window.transfer_table_count+=right['children'][j]['children'].length;
            }
            document.getElementById('graph_transfer_badge').innerHTML = window.transfer_table_count;
        }
        else if (type === "gf"){
            window.transfer_table_count+=right['children'].length;
            document.getElementById('graph_transfer_badge').innerHTML = window.transfer_table_count;
        }
        else if (type === "tf"){
            window.transfer_table_count+=1;
            document.getElementById('graph_transfer_badge').innerHTML = window.transfer_table_count;
        }
      }
      function add_to_transfer_list(transfer, right, parent_right, grandparent_right, greatgrandparent_right, level){
        if(level === "af"){
            for(var i in transfer){
                var curr_user = transfer[i];
                if(curr_user['children'].length!==0){
                    for(var j in curr_user['children']){
                        var curr_rolle = curr_user['children'][j];
                        if(curr_rolle['name']===parent_right['name']){
                            curr_rolle['children'].push(right);
                            return;
                        }
                    }
                }
                var parent_cpy = jQuery.extend({},parent_right);
                parent_cpy['children']=[right];
                curr_user['children'].push(parent_cpy);
                return;
            }
        }
        if(level === "gf"){
            curr_user = transfer[0];
            if(curr_user['children'].length!==0){
                for(j in curr_user['children']){
                    curr_rolle = curr_user['children'][j];
                    console.log("curr_rolle",curr_rolle);
                     if(curr_rolle['name']===grandparent_right['name']){
                        if(curr_rolle['children'].length!==0){
                            for(var k in curr_rolle['children']){
                                var curr_af = curr_rolle['children'][k];
                                console.log("curr_af",curr_af);
                                console.log(parent_right['name']);
                                console.log(curr_af['name']);
                                if (curr_af['name'] === parent_right['name']){
                                    curr_af['children'].push(right);
                                    return;
                                }
                            }
                        }
                        parent_cpy = jQuery.extend({},parent_right);
                        parent_cpy['children']=[right];
                        curr_rolle['children'].push(parent_cpy);
                        return;
                    }
                }
            }
            var grandparent_cpy = jQuery.extend({},grandparent_right);
            parent_cpy = jQuery.extend({},parent_right);
            parent_cpy['children']=[right];
            grandparent_cpy['children']=[parent_cpy];
            curr_user['children'].push(grandparent_cpy);
            return;

        }
        if(level === "tf") {
            curr_user = transfer[0];
            if (curr_user['children'].length !== 0) {
                for (j in curr_user['children']) {
                    curr_rolle = curr_user['children'][j];
                    if (curr_rolle['name'] === greatgrandparent_right['name']) {
                        if (curr_rolle['children'].length !== 0) {
                            for (k in curr_rolle['children']) {
                                curr_af = curr_rolle['children'][k];
                                console.log("curr_af",curr_af);
                                if (curr_af['name'] === grandparent_right['name']) {
                                    if (curr_af['children'].length !== 0) {
                                        for (var l in curr_af['children']){
                                            var curr_gf = curr_af['children'][l];
                                            console.log("curr_gf",curr_gf);
                                            console.log(parent_right['name']);
                                            console.log(curr_gf['name']);
                                            if (curr_gf['name'] === parent_right['name']) {
                                                curr_gf['children'].push(right);
                                                return;
                                            }
                                        }
                                    }
                                    parent_cpy = jQuery.extend({}, parent_right);
                                    parent_cpy['children'] = [right];
                                    curr_rolle['children'].push(parent_cpy);
                                    return;
                                }
                            }
                        }
                        parent_cpy = jQuery.extend({}, parent_right);
                        grandparent_cpy = jQuery.extend({}, grandparent_right);
                        parent_cpy['children'] = [right];
                        grandparent_cpy['children'] = [parent_cpy];
                        curr_rolle['children'].push(grandparent_cpy);
                        return;
                    }
                }
            }
            var greatgrandparent_cpy = jQuery.extend({}, greatgrandparent_right);
            grandparent_cpy = jQuery.extend({}, grandparent_right);
            parent_cpy = jQuery.extend({}, parent_right);
            parent_cpy['children'] = [right];
            grandparent_cpy['children'] = [parent_cpy];
            greatgrandparent_cpy['children'] = [grandparent_cpy];
            curr_user['children'].push(greatgrandparent_cpy);
            return;
        }
      }

      //-------> TODO: an ein level für Rollen denken sobald rollen eingefügt
      function update_rights(user_rights,compare_rights, transfer, d){
        if (d.depth ===1){
            for (i in compare_rights) {
                if (compare_rights[i]['name'] === d.data.name) {
                    console.log(i + "," + d.data.name);
                    if(window.level==="ROLLE") {
                        update_right_counters(compare_rights[i], "af");
                        add_to_transfer_list(transfer,compare_rights[i],d.parent.data, null, null,'af');
                    }else if(window.level==="AF") {
                        //TODO:  TESTEN
                        update_right_counters(compare_rights[i], "gf");
                        add_to_transfer_list(transfer,compare_rights[i],d.parent.data, d.parent.parent.data,null,'gf');
                    }else if(window.level==="GF") {
                        //TODO:  TESTEN
                        update_right_counters(compare_rights[i], "tf");
                        add_to_transfer_list(transfer,compare_rights[i],d.parent.data, d.parent.parent.data, d.parent.parent.parent.data,'tf');
                    }
                    return;
                }
            }
        }
        else if(d.depth===2){
            //TODO:  TESTEN
            for (i in compare_rights) {
                var right = compare_rights[i];
                if (right['name'] === d.parent.data.name) {
                    for (j in right['children']) {
                        var right_lev_2 = right['children'][j];
                        if (right_lev_2['name'] === d.data.name) {
                            console.log(j + "," + d.data.name);
                            right_lev_2["parent"]=d.parent.data.name;
                            if(window.level==="ROLLE"){
                                update_right_counters(right_lev_2,"gf");
                                add_to_transfer_list(transfer,right_lev_2,right,d.parent.parent.data,null,'gf');
                            }
                            if(window.level==="AF"){
                                update_right_counters(right_lev_2,"tf");
                                add_to_transfer_list(transfer,right_lev_2,right,d.parent.parent.data,d.parent.parent.parent.data,'tf');
                            }
                            return;
                        }
                    }
                }
            }
        }
        else if(d.depth===3){
            //TODO:  TESTEN
            for (i in compare_rights) {
                var right = compare_rights[i];
                if (right['name'] === d.parent.parent.data.name) {
                    for (j in right['children']) {
                        var right_lev_2 = right['children'][j];
                        if (right_lev_2['name'] === d.parent.data.name) {
                            for (k in right_lev_2['children']) {
                                var right_lev_3 = right_lev_2['children'][k];
                                if (right_lev_3['name'] === d.data.name) {
                                    console.log(k + "," + d.data.name);
                                    right_lev_3["grandparent"]= d.parent.parent.data.name;
                                    right_lev_3["greatgrandparent"]= d.parent.parent.parent.data.name;
                                    right_lev_3["parent"]=d.parent.data.name;
                                    update_right_counters(right_lev_3,"tf");
                                    //user_rights.push(right_lev_3);
                                    add_to_transfer_list(transfer,right_lev_3,right_lev_2,right,d.parent.parent.parent.data,'tf');
                                    return;
                                }
                            }
                        }
                    }
                }
            }
        }
      }
    });
}());
