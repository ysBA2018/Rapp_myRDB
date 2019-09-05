(function(){
$(document).ready(function(){
    var svg = d3.select("#compareCirclePackingSVG"),
        margin = 20,
        diameter = +svg.attr("width"),
        g = svg.append("g").attr("transform", "translate(" + diameter / 2 + "," + diameter / 2 + ")");
/*
    var color = d3.scaleLinear()
        .domain([-1, 5])
        .range(["hsl(360,100%,100%)", "hsl(0,0%,0%)"])
        .interpolate(d3.interpolateHcl);
*/


    var pack = d3.pack()
        .size([diameter - margin, diameter - margin])
        .padding(2);

    var root = window.compare_jsondata;
    console.log(root);

      root = d3.hierarchy(root)
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
      function compare_graphs(d, compare_data){
          if (d.depth === 2){
              for(var i in compare_data){
                  var level_2 = compare_data[i]['children'];
                  for(var j in level_2){
                      if(level_2[j].model_rolle_id.rollenid===d.data.model_rolle_id.rollenid){
                          console.log("Compare_ROLLE:"+level_2[j].model_rolle_id.rollenid+"==="+d.data.model_rolle_id.rollenid);
                          return true;
                      }
                  }
              }
          }
          else if (d.depth === 3){
              for(var i in compare_data){
                  var level_2 = compare_data[i]['children'];
                  for(var j in level_2){
                      if(level_2[j].model_rolle_id.rollenid===d.parent.data.model_rolle_id.rollenid){
                          var level_3 = level_2[j]['children'];
                          for(var k in level_3){
                              if(level_3[k].model_af_id.id===d.data.model_af_id.id){
                                  console.log("Compare_AF: "+level_3[k].model_af_id.id+"==="+d.data.model_af_id.id);
                                  return true;
                              }
                          }
                      }
                  }
              }
          }else if (d.depth === 4){
              for(var i in compare_data){
                  var level_2 = compare_data[i]['children'];
                  for(var j in level_2){
                      if(level_2[j].model_rolle_id.rollenid===d.parent.parent.data.model_rolle_id.rollenid){
                          var level_3 = level_2[j]['children'];
                          for(var k in level_3){
                              if(level_3[k].model_af_id.id===d.parent.data.model_af_id.id) {
                                  var level_4= level_3[k]['children'];
                                  for (var l in level_4) {
                                      if (level_4[l].model_gf_id.id === d.data.model_gf_id.id){
                                         console.log("Compare_GF: "+ level_4[l].model_gf_id.id+"==="+d.data.model_gf_id.id);
                                         return true;
                                      }
                                  }
                              }
                          }
                      }
                  }
              }
          }else if (d.depth === 5){
              for(var i in compare_data){
                  var level_2 = compare_data[i]['children'];
                  for(var j in level_2){
                      if(level_2[j].model_rolle_id.rollenid===d.parent.parent.parent.data.model_rolle_id.rollenid){
                          var level_3 = level_2[j]['children'];
                          for(var k in level_3){
                              if(level_3[k].model_af_id.id===d.parent.parent.data.model_af_id.id) {
                                  var level_4= level_3[k]['children'];
                                  for (var l in level_4) {
                                      if(level_4[l].model_gf_id.id===d.parent.data.model_gf_id.id) {
                                          var level_5 = level_4[l]['children'];
                                          for (var m in level_5) {
                                              if (level_5[m].model_tf_id.tf === d.data.model_tf_id.tf){
                                                 console.log("Compare_TF: "+ level_5[m].model_tf_id.tf +"==="+ d.data.model_tf_id.tf);
                                                 return true;
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
          return false;
      }
      function get_color(d) {
          if(d.depth===0){
              return "white";
          }
          else{
              if(compare_graphs(d,window.jsondata['children'])||compare_graphs(d,window.transferlistdata['children'])){                      if(d.depth===2)return "darkgrey";
                  if(d.depth===2)return "darkgrey";
                  if(d.depth===3)return "grey";
                  if(d.depth===4)return "dimgrey";
                  if(d.depth===5)return "lightgrey";
              }else{
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
          .style("fill", function(d) {return get_color(d)})
          .on("click", function(d) { if(d3.event.defaultPrevented) return;
                console.log("clicked");
              if (focus !== d) zoom(d), d3.event.stopPropagation(); })
          .on("contextmenu",function(d,i){confirm_transfer(d,i)})
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

      var leaves = d3.selectAll("circle").filter(function(d){
        return d.children === null;
      });

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

          svg = d3.select("#compareCirclePackingSVG"),
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
          .style("fill", function(d) {return get_color(d)})
          .on("click", function(d) { if(d3.event.defaultPrevented) return;
                console.log("clicked");
              if (focus !== d) zoom(d), d3.event.stopPropagation(); })
          .on("contextmenu", function(d,i){confirm_transfer(d,i)})
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

      leaves = d3.selectAll("circle").filter(function(d){
        return d.children === null;
      });

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
    window.updateCompareCP=function () {
        update(window.compare_jsondata)
    };

    function check_user_rights_for_existance(d,right_type, parent, grandparent, greatgrandparent,
                                             greatgreatgrandparent, user_userids, transfer_userids) {
        var exists_in_user_rights = false;
        var exists_in_transfer_rights = false;
        var user_roles, transfer_roles;
        if(right_type==="role"){
            loop1: for(var i in user_userids){
                user_roles = user_userids[i]['children'];
                for(var j in user_roles){
                    if(user_roles[j]['name']===d.data.name){
                        exists_in_user_rights = true;
                        break loop1
                    }
                }
            }
            loop1: for(i in transfer_userids){
                transfer_roles = transfer_userids[i]['children'];
                for(j in transfer_roles) {
                    if (transfer_roles[j]['name'] === d.data.name) {
                        exists_in_transfer_rights = true;
                        break loop1;
                    }
                }
            }
            if (!exists_in_user_rights && !exists_in_transfer_rights){
                return false;
            }else{
                bootbox.alert("Rolle existiert bereits\nund kann nicht übertragen werden!");
                return true;
            }

        }//TODO: Hier weiter --- "AF" ---
        else if(right_type==="af"){
            var parent_exists_in_user_rights=false;
            var parent_exists_in_transfer_rights=false;
            var transferable = true;
            loop1: for(i in user_userids){
                user_roles = user_userids[i]['children'];
                for(j in user_roles){
                    if(user_roles[j]['name']===parent){
                        parent_exists_in_user_rights = true;
                        var user_afs = user_roles[j]['children'];
                        for(var k in user_afs){
                            if(user_afs[k]['name']===d.data.name){
                                exists_in_user_rights = true;
                                break loop1;
                            }
                        }
                    }
                }

            }
            loop1: for(i in transfer_userids){
                transfer_roles = transfer_userids[i]['children'];
                for(j in transfer_roles){
                    if(transfer_roles[j]['name']===parent){
                        parent_exists_in_transfer_rights = true;
                        var transfer_afs = transfer_roles[j]['children'];
                        for(k in transfer_afs){
                            if(transfer_afs[k]['name']===d.data.name){
                                exists_in_transfer_rights = true;
                                break loop1;
                            }
                        }
                    }
                }
            }
            if(!exists_in_user_rights && !exists_in_transfer_rights){
                if(parent_exists_in_user_rights || parent_exists_in_transfer_rights){
                    return false
                }
                else{
                    bootbox.alert("AF kann nicht übertragen werden!\n\nUser besitzt nicht die nötige Rolle!");
                    return true;
                }
            }else{
                bootbox.alert("AF existiert bereits\nund kann nicht übertragen werden!");
                return true;
            }
        }
        else if(right_type==="gf") {
            var grandparent_exists_in_user_rights = false;
            parent_exists_in_user_rights = false;
            var grandparent_exists_in_transfer_rights = false;
            parent_exists_in_transfer_rights = false;
            loop1: for (i in user_userids) {
                user_roles = user_userids[i]['children'];
                for(j in user_roles){
                    if (user_roles[j]['name'] === grandparent) {
                        grandparent_exists_in_user_rights = true;
                        user_afs = user_roles[j]['children'];
                        for (k in user_afs) {
                            if (user_afs[k]['name'] === parent) {
                                parent_exists_in_user_rights = true;
                                var user_gfs = user_afs[k]['children'];
                                for (var l in user_gfs) {
                                    if (user_gfs[l]['name'] === d.data.name) {
                                        exists_in_user_rights = true;
                                        break loop1;
                                    }
                                }
                            }
                        }
                    }
                }
            }
            loop1: for (i in transfer_userids) {
                transfer_roles = transfer_userids[i]['children'];
                for(j in transfer_roles){
                    if (transfer_roles[j]['name'] === grandparent) {
                        grandparent_exists_in_transfer_rights = true;
                        transfer_afs = transfer_roles[j]['children'];
                        for (k in transfer_afs) {
                            if (transfer_afs[k]['name'] === parent) {
                                parent_exists_in_transfer_rights = true;
                                var transfer_gfs = transfer_afs[k]['children'];
                                for (l in transfer_gfs) {
                                    if (transfer_gfs[l]['name'] === d.data.name) {
                                        exists_in_transfer_rights = true;
                                        break loop1;
                                    }
                                }
                            }
                        }
                    }
                }
            }
            if (!exists_in_user_rights && !exists_in_transfer_rights) {
                if ((grandparent_exists_in_user_rights && parent_exists_in_user_rights)||(grandparent_exists_in_transfer_rights && parent_exists_in_transfer_rights)) {
                    return false;
                } else if (!grandparent_exists_in_user_rights && !grandparent_exists_in_transfer_rights) {
                    bootbox.alert("GF kann nicht übertragen werden!\n\nUser besitzt nicht die nötige Rolle und AF!");
                    return true;
                } else if ((grandparent_exists_in_user_rights && !parent_exists_in_user_rights)||(grandparent_exists_in_transfer_rights && !parent_exists_in_transfer_rights)) {
                    bootbox.alert("GF kann nicht übertragen werden!\n\nUser besitzt benötigte Rolle\naber nicht die nötige AF!");
                    return true;
                }
            }else{
                bootbox.alert("GF existiert bereits\nund kann nicht übertragen werden!");
                return true;
            }
        }
        else if(right_type==="tf") {
            grandparent_exists_in_user_rights = false;
            var greatgrandparent_exists_in_user_rights = false;
            parent_exists_in_user_rights = false;
            grandparent_exists_in_transfer_rights = false;
            var greatgrandparent_exists_in_transfer_rights = false;
            parent_exists_in_transfer_rights = false;
            loop1:for (i in user_userids) {
                user_roles = user_userids[i]['children'];
                for(j in user_roles){
                    if (user_roles[j]['name'] === greatgrandparent) {
                        greatgrandparent_exists_in_user_rights = true;
                        user_afs = user_roles[j]['children'];
                        for (k in user_afs) {
                            if (user_afs[k]['name'] === grandparent) {
                                grandparent_exists_in_user_rights = true;
                                user_gfs = user_afs[k]['children'];
                                for (l in user_gfs) {
                                    if (user_gfs[l]['name'] === parent) {
                                        parent_exists_in_user_rights = true;
                                        var user_tfs = user_gfs[l]['children'];
                                        for (var m in user_tfs) {
                                            if (user_tfs[m]['name'] === d.data.name) {
                                                exists_in_user_rights = true;
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
            loop1: for (i in transfer_userids) {
                transfer_roles = transfer_userids[i]['children'];
                for(j in transfer_roles){
                    if (transfer_roles[j]['name'] === greatgrandparent) {
                        greatgrandparent_exists_in_transfer_rights = true;
                        transfer_afs = transfer_roles[j]['children'];
                        for (k in transfer_afs) {
                            if (transfer_afs[k]['name'] === grandparent) {
                                grandparent_exists_in_transfer_rights = true;
                                transfer_gfs = transfer_afs[k]['children'];
                                for (l in transfer_gfs) {
                                    if (transfer_gfs[l]['name'] === parent) {
                                        parent_exists_in_transfer_rights = true;
                                        var transfer_tfs = transfer_gfs[l]['children'];
                                        for (m in transfer_tfs) {
                                            if (transfer_tfs[m]['name'] === d.data.name) {
                                                exists_in_transfer_rights = true;
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
            if (!exists_in_user_rights && !exists_in_transfer_rights) {
                if ((grandparent_exists_in_user_rights && parent_exists_in_user_rights)||(grandparent_exists_in_transfer_rights && parent_exists_in_transfer_rights)) {
                    return false;
                } else if (!greatgrandparent_exists_in_user_rights && !greatgrandparent_exists_in_transfer_rights) {
                    bootbox.alert("TF kann nicht übertragen werden!\n\nUser besitzt nicht die nötige Rolle, AF und GF!");
                    return true;
                } else if ((greatgrandparent_exists_in_user_rights  && !grandparent_exists_in_user_rights)||
                    (greatgrandparent_exists_in_transfer_rights && !grandparent_exists_in_transfer_rights)) {
                    bootbox.alert("TF kann nicht übertragen werden!\n\nUser besitzt benötigte Rolle\naber nicht die nötige AF und GF!");
                    return true;
                } else if ((greatgrandparent_exists_in_user_rights && grandparent_exists_in_user_rights && !parent_exists_in_user_rights)
                    ||(greatgrandparent_exists_in_transfer_rights && grandparent_exists_in_transfer_rights && !parent_exists_in_transfer_rights)) {
                    bootbox.alert("TF kann nicht übertragen werden!\n\nUser besitzt benötigte Rolle und AF\naber nicht die nötige GF!");
                    return true;
                }
            }else{
                bootbox.alert("TF existiert bereits\nund kann nicht übertragen werden!");
                return true;
            }
        }
    }
    function confirm_transfer(d,i) {
        d3.event.preventDefault();
          bootbox.confirm("Berechtigung:\n\n"+d.data.name+"\n\nwirklich zu Transferliste hinzufügen?\n\n", function (result) {
                console.log('This was logged in the callback: ' + result);
                if(result===true){
                    transferfunction(d,i)
                }
            });
    }
    function transferfunction(d,i){
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
        if(check_user_rights_for_existance(d,right_type,right_parent,right_grandparent, right_greatgrandparent,
            right_greatgreatgrandparent, window.jsondata['children'],window.transferlistdata['children'])){
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

            var data = {"X-CSRFToken":getCookie("csrftoken"),"X_METHODOVERRIDE":'PATCH',
                "user":window.user,"compare_user":window.compare_user,"action_type":"transfer",
                "right_type":right_type,"right_name":d.data.name,"parent":right_parent,
                "grandparent":right_grandparent, "greatgrandparent":right_greatgrandparent,
                "greatgreatgrandparent":right_greatgreatgrandparent,};
            var successful=false;
            var comparing_user_userid_combi_id = window.jsondata['children'][0]['user_userid_combi_id'];

            $.ajax({type:'POST',
                    data:data,
                    url:window.current_host+'/api/userhatuseridundnamen/'+comparing_user_userid_combi_id+'/',
                    async:false,
                    success: function(res){console.log(res);
                        successful=true},
                    error: function(res){console.log(res);}
                    });
            if(successful===true){
                var compare_rights = window.compare_jsondata['children'];
                var user_rights = window.jsondata['children'];
                var transfer = window.transferlistdata['children'];
                update_rights(user_rights,compare_rights, transfer, d);

                d3.select("body").selectAll("#compareCPtooltip").remove();

                d3.select('#compareCirclePackingSVG').select("g").data(window.compare_jsondata).exit().remove();
                update(window['compare_jsondata']);

                d3.select('#transferSVG').select('g').data(window.transferlistdata).exit().remove();
                window.updateTransfer();
                //d3.select('#circlePackingSVG').select('g').data(window.jsondata).exit().remove();
                //window.updateCP();
                bootbox.alert("Berechtigung "+d.data.name+" zur Transferliste hinzugefügt\n");
                //update_session();
            }
            else{
                bootbox.alert('Beim Übertragen der Berechtigung '+d.data.name+' ist ein Fehler aufgetreten!')
            }

      }
      function update_right_counters(right,type){
        if (type === "role"){
            for (j in right['children']){
                for (k in right['children'][j]['children']){
                    window.transfer_table_count+=right['children'][j]['children'][k]['children'].length;
                }
            }
            document.getElementById('graph_transfer_badge').innerHTML = window.transfer_table_count;
        }
        else if (type === "af"){
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
      function add_to_transfer_list(transfer, right, parent_right, grandparent_right, greatgrandparent_right, greatgreatgrandparent_right, level){
        if(level === "role"){
            var curr_user = transfer[0];
            curr_user['children'].push(right);
            return;
        }
        else if(level === "af"){
            var curr_user = transfer[0];
            var curr_user_roles = curr_user['children'];
            for(j in curr_user_roles){
                var curr_role = curr_user_roles[j];
                if(curr_role['name']===parent_right['name']){
                    curr_role['children'].push(right);
                    return;
                }
            }
            var parent_cpy = jQuery.extend({},parent_right);
            parent_cpy['children']=[right];
            curr_user['children']=[parent_cpy];
        }
        else if(level === "gf"){
            var curr_user = transfer[0];
            var curr_user_roles = curr_user['children'];
            for(j in curr_user_roles){
                var curr_role = curr_user_roles[j];
                if(curr_role['name']===grandparent_right['name']){
                    var curr_role_afs = curr_role['children'];
                    for(k in curr_role_afs) {
                        var curr_af = curr_role_afs[k];
                        if (curr_af['name'] === parent_right['name']) {
                            curr_af['children'].push(right);
                            return;
                        }
                    }
                }
            }
            var grandparent_cpy = jQuery.extend({},grandparent_right);
            var parent_cpy = jQuery.extend({},parent_right);
            parent_cpy['children']=[right];
            grandparent_cpy['children']=[parent_cpy];
            curr_user['children']=[grandparent_cpy];

        }
        else if(level === "tf"){

            var curr_user = transfer[0];
            var curr_user_roles = curr_user['children'];
            for(j in curr_user_roles){
                var curr_role = curr_user_roles[j];
                if(curr_role['name']===greatgrandparent_right['name']){
                    var curr_role_afs = curr_role['children'];
                    for(k in curr_role_afs) {
                        var curr_af = curr_role_afs[k];
                        if (curr_af['name'] === grandparent_right['name']) {
                            var curr_af_gfs = curr_af['children'];
                            for(l in curr_af_gfs) {
                                var curr_gf = curr_af_gfs[l];
                                if (curr_gf['name'] === parent_right['name']) {
                                    curr_gf['children'].push(right);
                                    return;
                                }
                            }
                        }
                    }
                }
            }
            var greatgrandparent_cpy = jQuery.extend({},greatgrandparent_right);
            var grandparent_cpy = jQuery.extend({},grandparent_right);
            var parent_cpy = jQuery.extend({},parent_right);
            parent_cpy['children']=[right];
            grandparent_cpy['children']=[parent_cpy];
            greatgrandparent_cpy['children']=[grandparent_cpy];
            curr_user['children']=[greatgrandparent_cpy];
        }
      }

      //-------> TODO: an ein level für Rollen denken sobald rollen eingefügt
      function update_rights(user_rights,compare_rights, transfer, d){
        if(d.depth===2){
            for (i in compare_rights) {
                var user = compare_rights[i];
                for (j in user['children']) {
                    var role = user['children'][j];
                    if (role['name'] === d.data.name) {
                        console.log(j + "," + d.data.name);
                        role["parent"]=d.parent.data.name;
                        update_right_counters(role,"role");
                        add_to_transfer_list(transfer,role,user,null, null, null,'role');
                        return;
                    }
                }

            }
        }
        else if(d.depth===3){
            for (i in compare_rights) {
                var user = compare_rights[i];
                for (j in user['children']) {
                    var role = user['children'][j];
                    if (role['name'] === d.parent.data.name) {
                        for (k in role['children']) {
                            var af = role['children'][k];
                            if (af['name'] === d.data.name) {
                                console.log(k + "," + d.data.name);
                                af["grandparent"]= d.parent.parent.data.name;
                                af["parent"]=d.parent.data.name;
                                update_right_counters(af,"af");
                                add_to_transfer_list(transfer,af,role,user, null, null,'af');
                                return;
                            }
                        }
                    }
                }
            }
        }
        else if(d.depth===4){
            for (i in compare_rights) {
                var user = compare_rights[i];
                for (j in user['children']) {
                    var role = user['children'][j];
                    if (role['name'] === d.parent.parent.data.name) {
                        for (k in role['children']) {
                            var af = role['children'][k];
                            if (af['name'] === d.parent.data.name) {
                                for (l in af['children']) {
                                    var gf = af['children'][l];
                                    if (gf['name'] === d.data.name) {
                                        console.log(l + "," + d.data.name);
                                        gf["greatgrandparent"] = d.parent.parent.parent.data.name;
                                        gf["grandparent"] = d.parent.parent.data.name;
                                        gf["parent"] = d.parent.data.name;
                                        update_right_counters(gf, "gf");
                                        add_to_transfer_list(transfer, gf, af, role, user, null, 'gf');
                                        return;
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        else if(d.depth===4){
            for (i in compare_rights) {
                var user = compare_rights[i];
                for (j in user['children']) {
                    var role = user['children'][j];
                    if (role['name'] === d.parent.parent.parent.data.name) {
                        for (k in role['children']) {
                            var af = role['children'][k];
                            if (af['name'] === d.parent.parent.data.name) {
                                for (l in af['children']) {
                                    var gf = af['children'][l];
                                    if (gf['name'] === d.parent.data.name) {
                                        for (m in gf['children']) {
                                            var tf = gf['children'][m];
                                            if (tf['name'] === d.data.name) {
                                                console.log(m + "," + d.data.name);
                                                tf["greatgreatgrandparent"] = d.parent.parent.parent.parent.data.name;
                                                tf["greatgrandparent"] = d.parent.parent.parent.data.name;
                                                tf["grandparent"] = d.parent.parent.data.name;
                                                tf["parent"] = d.parent.data.name;
                                                update_right_counters(tf, "tf");
                                                add_to_transfer_list(transfer, tf, gf, af, role, user, 'tf');
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
    });
}());
