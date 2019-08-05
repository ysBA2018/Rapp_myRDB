(function(){
$(document).ready(function(){
    var svg = d3.select("#circlePackingSVG"),
        margin = 20,
        diameter = +svg.attr("width"),
        g = svg.append("g").attr("transform", "translate(" + diameter / 2 + "," + diameter / 2 + ")");
    /*
    var color = d3.scaleLinear()
        .domain([-1, 5])
        .range(["hsl(360,0%,100%)", "hsl(0,100%,100%)"])
        .interpolate(d3.interpolateHcl);
    */

    var pack = d3.pack()
        .size([diameter - margin, diameter - margin])
        .padding(2);

    var root = window.jsondata;
    console.log(root);

      root = d3.hierarchy(root)
          .sum(function(d) { return d.size; })
          .sort(function(a, b) { return b.value - a.value; });

      var focus = root,
          nodes = pack(root).descendants(),
          view;

      var div = d3.select("body").append("div")
          .attr("class","tooltip")
          .attr("id","CPtooltip")
          .style("opacity",0);

      function compare_graphs(d){
          var compare_data = window.compare_jsondata['children'];
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
          return false;
      }
      function get_color(d) {
          if(d.depth===0){
              return "white";
          }
          else{
              console.log(window.current_site);
              if(window.current_site==="compare"){
                  if(compare_graphs(d)){
                      if(d.depth===1)return "darkgrey";
                      if(d.depth===2)return "grey";
                      if(d.depth===3)return "lightgrey";
                  }else{
                      if(d.depth===3){return d.data.color}
                      else{return "white"}
                  }
              }
              else{
                  if(d.depth===5){return d.data.color}
                  else{return "white"}
              }
          }
      }

    //TODO: bei erstellen von json color für leaves mitgeben!!!
      var circle = g.selectAll("circle")
        .data(nodes)
        .enter().append("circle")
          .attr("class", function(d) { return d.parent ? d.children ? "node" : "node node--leaf" : "node node--root"; })
          .style("stroke","grey")
          .style("fill", function(d) {return get_color(d)}) //else{return d.children ? color(d.depth) : null; }
          .on("click", function(d) { if(d3.event.defaultPrevented) return;
                console.log("clicked");
              if (focus !== d) zoom(d), d3.event.stopPropagation(); })
          .on("contextmenu",function(d,i){confirm_deletion(d,i)})
          .on("mouseover",function (d) {
              d3.select(this).style("stroke","black");
              div.transition()
                  .duration(200)
                  .style("opacity",9);
              var text;
              if(d.depth === 1){
                  text = "<b>User:</b> "+d.data.name+"<br/>"
              }else if(d.depth === 2){
                  text = "<b>Rolle:</b> "+d.data.name+"<br/>"+"<b>Rollen-Beschreibung:</b> "+d.data.description
              }else if(d.depth === 3){
                  text = "<b>AF:</b> "+d.data.name+"<br/>"+"<b>AF-Beschreibung:</b> "+d.data.description
              }else if(d.depth === 4){
                  text = "<b>GF:</b> "+d.data.name+"<br/>"+"<b>GF-Beschreibung:</b> "+d.data.description
              }else if(d.depth === 5){
                  text = "<b>TF:</b> "+d.data.name+"<br/>"+"<b>TF-Beschreibung:</b> "+d.data.description
              }
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
      /*
      var leaves = d3.selectAll("circle").filter(function(d){
        return d.children === null;
      });
       */
      //var text = g.selectAll("text")
      //  .data(nodes)
      //  .enter().append("text")
      //    .attr("class", "label")
      //    .style("fill-opacity", function(d) { return d.parent === root ? 1 : 0; })
      //    .style("display", function(d) { return d.parent === root ? "inline" : "none"; })
      //    .text(function(d) { return d.data.name; });

        var node = g.selectAll("circle");
      //var node = g.selectAll("circle,text");
      //.call(d3.drag()
        //                   .on("start",dragstarted)
        //                   .on("drag",dragged)
        //                   .on("end",dragended))

      svg
          .style("background", "white")
          .on("click", function() { zoom(root); });

      zoomTo([root.x, root.y, root.r * 2 + margin]);

      function zoom(d) {
          if (d.depth===5) return;
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

      //function dragstarted(d){
      //    d3.event.sourceEvent.stopPropagation()
      //    console.log("dragstarted");
      //    d3.select(this).raise().classed("active",true);
      //}
      //function dragged(d) {
      //    console.log("dragged");
      //    d.x += d3.event.dx;
      //    d.y += d3.event.dy;
      //    draw();
      //}
      //function dragended(d) {
      //    console.log("dragended");
      //    d3.select(this).classed("active",false);
      //}
      //function draw() {
      //    var k = diameter / (root.r * 2 + margin);
      //    node.attr("transform", function(d){
      //        return "translate("+(d.x -root.x)*k+","+(d.y-root.y)*k+")";
      //    });
      //    circle.attr("r", function(d){
      //        return d.r*k;
      //    });
      //}
    function update(updated_data){
          console.log(updated_data);
          root = updated_data;

          svg = d3.select("#circlePackingSVG"),
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
          .attr("id","CPtooltip")
          .style("opacity",0);

    //TODO: bei erstellen von json color für leaves mitgeben!!!
      circle = g.selectAll("circle")
        .data(nodes)
        .enter().append("circle")
          .attr("class", function(d) { return d.parent ? d.children ? "node" : "node node--leaf" : "node node--root"; })
          .style("stroke","grey")
          .style("fill", function(d) { return get_color(d)}) //else{return d.children ? color(d.depth) : null; }
          .on("click", function(d) { if(d3.event.defaultPrevented) return;
                console.log("clicked");
              if (focus !== d) zoom(d), d3.event.stopPropagation(); })
          .on("contextmenu", function(d,i){confirm_deletion(d,i);})
          .on("mouseover",function (d) {
              d3.select(this).style("stroke","black");
              div.transition()
                  .duration(200)
                  .style("opacity",9);
              var text;
              if(d.depth === 1){
                  text = "<b>User:</b> "+d.data.name+"<br/>"
              }else if(d.depth === 2){
                  text = "<b>Rolle:</b> "+d.data.name+"<br/>"+"<b>Rollen-Beschreibung:</b> "+d.data.description
              }else if(d.depth === 3){
                  text = "<b>AF:</b> "+d.data.name+"<br/>"+"<b>AF-Beschreibung:</b> "+d.data.description
              }else if(d.depth === 4){
                  text = "<b>GF:</b> "+d.data.name+"<br/>"+"<b>GF-Beschreibung:</b> "+d.data.description
              }else if(d.depth === 5){
                  text = "<b>TF:</b> "+d.data.name+"<br/>"+"<b>TF-Beschreibung:</b> "+d.data.description
              }
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

      /*
        leaves = d3.selectAll("circle").filter(function(d){
        return d.children === null;
      });
        */
      //var text = g.selectAll("text")
      //  .data(nodes)
      //  .enter().append("text")
      //    .attr("class", "label")
      //    .style("fill-opacity", function(d) { return d.parent === root ? 1 : 0; })
      //    .style("display", function(d) { return d.parent === root ? "inline" : "none"; })
      //    .text(function(d) { return d.data.name; });

        node = g.selectAll("circle");
      //var node = g.selectAll("circle,text");
      //.call(d3.drag()
        //                   .on("start",dragstarted)
        //                   .on("drag",dragged)
        //                   .on("end",dragended))

      svg
          .style("background", "white")
          .on("click", function() { zoom(root); });

      zoomTo([root.x, root.y, root.r * 2 + margin]);
    }
    window.updateCP=function () {
        update(window.jsondata)
    };
      function confirm_deletion(d,i) {
          d3.event.preventDefault();
          if (d.depth !== 1){
              bootbox.confirm("Berechtigung:\n\n" + d.data.name + "\n\nwirklich zu Löschliste hinzufügen?\n\n", function (result) {
                  console.log('This was logged in the callback: ' + result);
                  if (result === true) {
                      deletefunction(d, i)
                  }
              });
          }
      }
    function deletefunction(d,i){

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
            var right_type="",right_parent = "",right_grandparent = "",right_greatgrandparent = "",
                right_greatgreatgrandparent = "",user_userid_combi_id = "";
            if(d.depth===1){
                right_type="user";
                user_userid_combi_id = d.data.user_userid_combi_id;
            }
            else if(d.depth===2) {
                right_type="role";
                right_parent = d.parent.data.name;
                user_userid_combi_id = d.parent.data.user_userid_combi_id;
            }
            else if(d.depth===3){
                right_type="af";
                right_parent = d.parent.data.name;
                right_grandparent = d.parent.parent.data.name;
                user_userid_combi_id = d.parent.parent.data.user_userid_combi_id;
            }else if(d.depth===4){
                right_type="gf";
                right_parent = d.parent.data.name;
                right_grandparent = d.parent.parent.data.name;
                right_greatgrandparent = d.parent.parent.parent.data.name;
                user_userid_combi_id = d.parent.parent.parent.data.user_userid_combi_id;
            }else if(d.depth===5){
                right_type="tf";
                right_parent = d.parent.data.name;
                right_grandparent = d.parent.parent.data.name;
                right_greatgrandparent = d.parent.parent.parent.data.name;
                right_greatgreatgrandparent = d.parent.parent.parent.parent.data.name;
                user_userid_combi_id = d.parent.parent.parent.parent.data.user_userid_combi_id;
            }
            var data = {"X-CSRFToken":getCookie("csrftoken"),"X_METHODOVERRIDE":'PATCH',"user":window.user,
                "action_type":"trash","right_type":right_type,"right_name":d.data.name,"parent":right_parent,
                "grandparent":right_grandparent, "greatgrandparent":right_greatgrandparent,
                "greatgreatgrandparent":right_greatgreatgrandparent, };
            var successful=false;
            $.ajax({type:'POST',
                    data:data,
                    url:window.current_host+'/api/userhatuseridundnamen/'+user_userid_combi_id+'/',
                    async:false,
                    success: function(res){console.log(res);
                        successful=true},
                    error: function(res){console.log(res);}
                    });
            if(successful===true){
                var rights = window.jsondata['children'];
                var trash = window.trashlistdata['children'];
                update_rights(rights, trash, d);

                d3.select("body").selectAll("#CPtooltip").remove();

                d3.select('#circlePackingSVG').select("g").data(window.jsondata).exit().remove();
                update(window['jsondata']);

                d3.select('#trashSVG').select('g').data(window.trashlistdata).exit().remove();
                window.updateTrash();

                if(window.current_site==="compare"){
                    d3.select('#compareCirclePackingSVG').select('g').data(window.compare_jsondata).exit().remove();
                    window.updateCompareCP();
                }
                bootbox.alert("Berechtigung "+d.data.name+" zur\n\nLöschliste hinzugefügt\n",function(){
                    console.log(d.data.name+'gelöscht!');
                });
            }
            else{
                bootbox.alert("Beim Löschen der Berechtigung\nist ein Fehler aufgetreten!",function(){
                    console.log('Fehler aufgetreten!');
                });
            }

      }


      function update_right_counters(right,type){
        if (type === "user"){
            for (h in right['children']) {
                for (i in right['children'][h]['children']) {
                    for (j in right['children'][h]['children'][i]['children']) {
                        window.trash_table_count += right['children'][h]['children'][i]['children'][j]['children'].length;
                    }
                    document.getElementById('graph_trash_badge').innerHTML = window.trash_table_count;
                }
            }
        }
        if (type === "role"){
            for (i in right['children']) {
                for (j in right['children'][i]['children']) {
                    window.trash_table_count += right['children'][i]['children'][j]['children'].length;
                }
                document.getElementById('graph_trash_badge').innerHTML = window.trash_table_count;
            }
        }
        if (type === "af"){
            for (j in right['children']){
                window.trash_table_count+=right['children'][j]['children'].length;
            }
            document.getElementById('graph_trash_badge').innerHTML = window.trash_table_count;
        }
        else if (type === "gf"){
            window.trash_table_count+=right['children'].length;
            document.getElementById('graph_trash_badge').innerHTML = window.trash_table_count;
        }
        else if (type === "tf"){
            window.trash_table_count+=1;
            document.getElementById('graph_trash_badge').innerHTML = window.trash_table_count;
        }
      }

      function add_to_delete_list(delete_list, right, parent_right, grandparent_right, greatgrandparent_right,
                                  greatgreatgrandparent_right, level) {
          if (level === "role") {
              var user_found = false;
              for (var i in delete_list) {
                  var curr_user = delete_list[i];
                  if (curr_user['name'] === parent_right['name']) {
                      user_found = true;
                      var role_found = false;
                      var roles = curr_user['children'];
                      for (var role in roles) {
                          var curr_role = roles[role];
                          if (curr_role['model_rolle_id'] === right['model_rolle_id']) {
                              role_found = true;
                              break
                          }
                      }
                      if (role_found) {
                          for (var child in right['children']) {
                              var af_found = false;
                              for(var s in curr_role['children']){
                                  var curr_af = curr_role['children'][s];
                                  if (curr_af['model_af_id'] === right['children'][child]['model_af_id']) {
                                      af_found = true;
                                      break
                                  }
                              }
                              if(af_found){
                                  for (var l in right['children'][child]['children']) {
                                      var gf_found = false;
                                      for(var t in curr_af['children']){
                                          var curr_gf = curr_af['children'][t];
                                          if (curr_gf['model_gf_id'] === right['children'][child]['children'][l]['model_gf_id']) {
                                              gf_found = true;
                                              break
                                          }
                                      }
                                      if(gf_found){
                                          for (var m in right['children'][child]['children'][l]['children']) {
                                              var tf_found = false;
                                              for(var u in curr_gf['children']){
                                                  var curr_tf = curr_gf['children'][u];
                                                  if (curr_tf['model_tf_id'] === right['children'][child]['children'][l]['children'][m]['model_tf_id']) {
                                                      tf_found = true;
                                                      break
                                                  }
                                              }
                                              if(!tf_found){
                                                  curr_gf['children'].push(right['children'][child]['children'][l]['children'][m]);
                                              }
                                          }
                                      }
                                      else{
                                          curr_af['children'].push(right['children'][child]['children'][l]);
                                      }
                                  }
                              }
                              else{
                                  curr_role['children'].push(right['children'][child]);
                              }
                          }
                          return;
                      }
                      break
                  }
              }
              if (user_found) {
                  curr_user['children'].push(right);
                  return;
              }
              var parent_cpy = jQuery.extend({}, parent_right);
              parent_cpy['children'] = [right];
              delete_list.push(parent_cpy);
          }
          else if (level === "af") {
              for (var i in delete_list) {
                  var curr_user = delete_list[i];
                  if (curr_user['name'] === grandparent_right['name']) {
                      var curr_user_roles = curr_user['children'];
                      var role_found = false;
                      for (var j in curr_user_roles) {
                          var curr_role = curr_user_roles[j];
                          var af_found = false;
                          if (curr_role['model_rolle_id'] === parent_right['model_rolle_id']) {
                              role_found = true;
                              var afs = curr_role['children']
                              for (var af in afs) {
                                  var curr_af = afs[af];
                                  if (curr_af['model_af_id'] === right['model_af_id']) {
                                      af_found = true;
                                      break
                                  }
                              }
                              if (af_found) {
                                  for (var gf in right['children']) {
                                      var curr_gfs = curr_af['children'];
                                      var gf_found = false;
                                      for (var s in curr_gfs) {
                                          var curr_gf = curr_gfs[s];
                                          if (curr_gf['model_gf_id'] === right['children'][gf]['model_gf_id']) {
                                              gf_found = true;
                                              break
                                          }
                                      }
                                      if (gf_found) {
                                          for (var tf in right['children'][gf]['children']) {
                                              var curr_tfs = curr_gf['children'];
                                              var tf_found = false;
                                              for (var t in curr_tfs) {
                                                  var curr_tf = curr_tfs[t];
                                                  if (curr_tf['model_tf_id'] === right['children'][gf]['children'][tf]['model_tf_id']) {
                                                      tf_found = true;
                                                      break
                                                  }
                                              }
                                              if (!tf_found) {
                                                  curr_gf['children'].push(right['children'][gf]['children'][tf]);
                                              }
                                          }
                                      }
                                      else{
                                          curr_af['children'].push(right['children'][gf]);
                                      }
                                  }
                                  return;
                              }
                          }
                      }
                      if (role_found) {
                          curr_role['children'].push(right);
                          return;
                      } else {
                          var parent_cpy = jQuery.extend({}, parent_right);
                          parent_cpy['children'] = [right];
                          curr_user_roles.push(parent_cpy);
                          return
                      }

                  }
              }
              var grandparent_cpy = jQuery.extend({}, grandparent_right);
              var parent_cpy = jQuery.extend({}, parent_right);
              parent_cpy['children'] = [right];
              grandparent_cpy['children'] = [parent_cpy];
              delete_list.push(grandparent_cpy);
          }else if (level === "gf") {
              user_found = false;
              for (var i in delete_list) {
                  var curr_user = delete_list[i];
                  if (curr_user['name'] === greatgrandparent_right['name']) {
                      user_found = true;
                      var curr_user_roles = curr_user['children'];
                      var role_found = false;
                      for (var j in curr_user_roles) {
                          var curr_role = curr_user_roles[j];
                          var af_found = false;
                          if (curr_role['model_rolle_id'] === grandparent_right['model_rolle_id']) {
                              var curr_role_afs = curr_role['children'];
                              role_found = true;
                              for (var k in curr_role_afs){
                                  var curr_af=curr_role_afs[k];
                                  var gf_found = false;
                                  if (curr_af['model_af_id'] === parent_right['model_af_id']) {
                                      var gfs = curr_af['children'];
                                      af_found = true;
                                      for (var gf in gfs) {
                                          var curr_gf = gfs[gf];
                                          if (curr_gf['model_gf_id'] === right['model_gf_id']) {
                                              gf_found = true;
                                              break
                                          }
                                      }
                                      if (gf_found) {
                                          var tfs = right['children'];
                                          for (var tf in tfs) {
                                              var curr_tfs = curr_gf['children'];
                                              var tf_found = false;
                                              for (var t in curr_tfs) {
                                                  var curr_tf = curr_tfs[t];
                                                  if (curr_tf['model_tf_id'] === tfs[tf]['model_tf_id']) {
                                                      tf_found = true;
                                                      break
                                                  }
                                              }
                                              if (!tf_found) {
                                                  curr_gf['children'].push(tfs[tf]);
                                              }
                                          }
                                          return;
                                      }
                                      break
                                  }
                              }
                              if (af_found) {
                                  curr_af['children'].push(right);
                                  return;
                              }
                          }
                      }
                      if (role_found){
                          var parent_cpy = jQuery.extend({}, parent_right);
                          parent_cpy['children'] = [right];
                          curr_role_afs.push(parent_cpy);
                          return;
                      }
                  }
              }
              if (user_found){
                  var parent_cpy = jQuery.extend({}, parent_right);
                  var grandparent_cpy = jQuery.extend({}, grandparent_right);
                  parent_cpy['children'] = [right];
                  grandparent_cpy['children'] = [parent_cpy];
                  curr_user_roles.push(grandparent_cpy);
                  return
              }
              var greatgrandparent_cpy = jQuery.extend({}, greatgrandparent_right);
              var grandparent_cpy = jQuery.extend({}, grandparent_right);
              var parent_cpy = jQuery.extend({}, parent_right);
              parent_cpy['children'] = [right];
              grandparent_cpy['children'] = [parent_cpy];
              greatgrandparent_cpy['children'] = [grandparent_cpy];
              delete_list.push(greatgrandparent_cpy);
          }else if (level === "tf") {
              user_found = false;
              for (var i in delete_list) {
                  var curr_user = delete_list[i];
                  if (curr_user['name'] === greatgreatgrandparent_right['name']) {
                      user_found = true;
                      var curr_user_roles = curr_user['children'];
                      var role_found = false;
                      for (var j in curr_user_roles) {
                          var curr_role = curr_user_roles[j];
                          var af_found = false;
                          if (curr_role['model_rolle_id'] === greatgrandparent_right['model_rolle_id']) {
                              var curr_role_afs = curr_role['children'];
                              role_found = true;
                              for (var k in curr_role_afs){
                                  var curr_af=curr_role_afs[k];
                                  var gf_found = false;
                                  if (curr_af['model_af_id'] === grandparent_right['model_af_id']) {
                                      var curr_af_gfs = curr_af['children'];
                                      af_found = true;
                                      for (var l in curr_af_gfs){
                                           var curr_gf=curr_af_gfs[l];
                                           if (curr_gf['model_gf_id'] === parent_right['model_gf_id']) {
                                               gf_found = true;
                                               break;
                                           }
                                      }
                                      if (gf_found) {
                                          curr_gf['children'].push(right);
                                          return;
                                      }
                                  }
                              }
                              if (af_found){
                                  var parent_cpy = jQuery.extend({}, parent_right);
                                  parent_cpy['children'] = [right];
                                  curr_af_gfs.push(parent_cpy);
                                  return;
                              }

                          }
                      }
                      if (role_found){
                          var parent_cpy = jQuery.extend({}, parent_right);
                          var grandparent_cpy = jQuery.extend({}, grandparent_right);
                          parent_cpy['children'] = [right];
                          grandparent_cpy['children'] = [parent_cpy];
                          curr_role_afs.push(grandparent_cpy);
                          return
                      }
                  }
              }
              if (user_found){
                  var parent_cpy = jQuery.extend({}, parent_right);
                  var grandparent_cpy = jQuery.extend({}, grandparent_right);
                  var greatgrandparent_cpy = jQuery.extend({}, greatgrandparent_right);

                  parent_cpy['children'] = [right];
                  grandparent_cpy['children'] = [parent_cpy];
                  greatgrandparent_cpy['children'] = [grandparent_cpy];
                  curr_user_roles.push(greatgrandparent_cpy);
                  return
              }
              var greatgreatgrandparent_cpy = jQuery.extend({}, greatgreatgrandparent_right);
              var greatgrandparent_cpy = jQuery.extend({}, greatgrandparent_right);
              var grandparent_cpy = jQuery.extend({}, grandparent_right);
              var parent_cpy = jQuery.extend({}, parent_right);
              parent_cpy['children'] = [right];
              grandparent_cpy['children'] = [parent_cpy];
              greatgrandparent_cpy['children'] = [grandparent_cpy];
              greatgreatgrandparent_cpy['children'] = [greatgrandparent_cpy];
              delete_list.push(greatgreatgrandparent_cpy);
          }
      }

      function update_rights(rights, trash, d){
        if(d.depth===2){
            for (var i in rights) {
                var right = rights[i];
                if (right['name'] === d.parent.data.name) {
                    for (var j in right['children']) {
                        var right_lev_2 = right['children'][j];
                        if (right_lev_2['name'] === d.data.name) {
                            console.log(j + "," + d.data.name);
                            right_lev_2["parent"]=d.parent.data.name;
                            update_right_counters(right_lev_2,"role");
                            add_to_delete_list(trash,right_lev_2,right,null,null,null,'role');
                            right['children'].splice(j, 1);
                            if(right['children'].length===0){
                                rights.splice(i,1)
                            }
                            return;
                        }
                    }
                }
            }
        }
        else if(d.depth===3){
            for (var i in rights) {
                var right = rights[i];
                if (right['name'] === d.parent.parent.data.name) {
                    for (var j in right['children']) {
                        var right_lev_2 = right['children'][j];
                        if (right_lev_2['name'] === d.parent.data.name) {
                            for (var k in right_lev_2['children']) {
                                var right_lev_3 = right_lev_2['children'][k];
                                if (right_lev_3['name'] === d.data.name) {
                                    console.log(k + "," + d.data.name);
                                    right_lev_3["grandparent"]= d.parent.parent.data.name;
                                    right_lev_3["parent"]=d.parent.data.name;
                                    update_right_counters(right_lev_3,"af");
                                    add_to_delete_list(trash,right_lev_3,right_lev_2,right,null,null,'af');
                                    right_lev_2['children'].splice(k, 1);
                                    if(right_lev_2['children'].length===0){
                                        right['children'].splice(j,1)
                                    }
                                    if(right['children'].length===0){
                                        rights.splice(i,1)
                                    }

                                    return;
                                }
                            }
                        }
                    }
                }
            }
        }else if(d.depth===4){
            for (var h in rights) {
                var right = rights[h];
                if (right['name'] === d.parent.parent.parent.data.name) {
                    for (var i in right['children']) {
                        var rightBase = right['children'][i];
                        if (rightBase['name'] === d.parent.parent.data.name) {
                            for (var j in rightBase['children']) {
                                var right_lev_2 = rightBase['children'][j];
                                if (right_lev_2['name'] === d.parent.data.name) {
                                    for (var k in right_lev_2['children']) {
                                        var right_lev_3 = right_lev_2['children'][k];
                                        if (right_lev_3['name'] === d.data.name) {
                                            console.log(k + "," + d.data.name);
                                            right_lev_3["greatgrandparent"] = d.parent.parent.parent.data.name;
                                            right_lev_3["grandparent"] = d.parent.parent.data.name;
                                            right_lev_3["parent"] = d.parent.data.name;
                                            update_right_counters(right_lev_3, "gf");
                                            add_to_delete_list(trash, right_lev_3, right_lev_2, rightBase, right, null,'gf');
                                            right_lev_2['children'].splice(k, 1);
                                            if (right_lev_2['children'].length === 0) {
                                                rightBase['children'].splice(j, 1)
                                            }
                                            if (rightBase['children'].length === 0) {
                                                right['children'].splice(i, 1)
                                            }
                                            if (right['children'].length === 0) {
                                                rights.splice(h, 1)
                                            }

                                            return;
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }else if(d.depth===5){
            for (g in rights) {
                var right = rights[g];
                if (right['name'] === d.parent.parent.parent.parent.data.name) {
                    for (h in right['children']) {
                        var rightBase = right['children'][h];
                        if (rightBase['name'] === d.parent.parent.parent.data.name) {
                            for (var i in rightBase['children']) {
                                var right0 = rightBase['children'][i];
                                if (right0['name'] === d.parent.parent.data.name) {
                                    for (var j in right0['children']) {
                                        var right_lev_2 = right0['children'][j];
                                        if (right_lev_2['name'] === d.parent.data.name) {
                                            for (var k in right_lev_2['children']) {
                                                var right_lev_3 = right_lev_2['children'][k];
                                                if (right_lev_3['name'] === d.data.name) {
                                                    console.log(k + "," + d.data.name);
                                                    right_lev_3["greatgreatgrandparent"] = d.parent.parent.parent.parent.data.name;
                                                    right_lev_3["greatgrandparent"] = d.parent.parent.parent.data.name;
                                                    right_lev_3["grandparent"] = d.parent.parent.data.name;
                                                    right_lev_3["parent"] = d.parent.data.name;
                                                    update_right_counters(right_lev_3, "tf");
                                                    add_to_delete_list(trash, right_lev_3, right_lev_2, right0, rightBase, right, 'tf');
                                                    right_lev_2['children'].splice(k, 1);
                                                    if (right_lev_2['children'].length === 0) {
                                                        right0['children'].splice(j, 1)
                                                    }
                                                    if (right0['children'].length === 0) {
                                                        rightBase['children'].splice(i, 1)
                                                    }
                                                    if (rightBase['children'].length === 0) {
                                                        right['children'].splice(h, 1)
                                                    }
                                                    if (right['children'].length === 0) {
                                                        rights.splice(g, 1)
                                                    }

                                                    return;
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

      }
    });
}());
