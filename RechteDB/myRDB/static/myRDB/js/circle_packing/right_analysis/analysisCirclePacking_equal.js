(function(){
$(document).ready(function(){
    var svgIndex = window.iEqual;
    window.iEqual=window.iEqual+1

    var svg = d3.select("#analysisCirclePackingSVG_equal"+svgIndex),
        margin = 20,
        diameter = +svg.attr("width"),
        g = svg.append("g").attr("transform", "translate(" + diameter / 2 + "," + diameter / 2 + ")");

    var pack = d3.pack()
        .size([diameter - margin, diameter - margin])
        .padding(2);

    function get_tooltip_text(d) {
          var text;
          if (window.level === "Role"||window.level === "ROLLE") {
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
      function get_color(d) {
         if (d.depth === 0) return "darkgrey";
         if (window.level === "Role" || window.level === "ROLLE") {
             if(d.depth===1)return "grey";
             else if(d.depth===2)return "dimgrey";
             else if(d.depth===3)return "lightgrey";
         } else if (window.level === "AF") {
             if(d.depth===1)return "dimgrey";
             else if(d.depth===2)return "lightgrey";
         } else if (window.level === "GF") {
             if (d.depth === 1) return "lightgrey";
         }
     }

    var root = window['jsondata_equal'+svgIndex];

      root = d3.hierarchy(root)
          .sum(function(d) { return d.size; })
          .sort(function(a, b) { return b.value - a.value; });

      var focus = root,
          nodes = pack(root).descendants(),
          view;

      var circle = g.selectAll("circle")
        .data(nodes)
        .enter().append("circle")
          .attr("class", function(d) { return d.parent ? d.children ? "node" : "node node--leaf" : "node node--root"; })
          .style("fill", function(d) { return get_color(d) })
          .style("stroke","grey")
          .on("click", function(d) { if (focus !== d) zoom(d), d3.event.stopPropagation(); })
          .on("contextmenu", function(d) { d3.event.preventDefault(); })
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

    var div = d3.select("body").append("div")
          .attr("class","tooltip")
          .attr("id","CPtooltip")
          .style("opacity",0);

      var node = g.selectAll("circle,text");

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
    });
}());
