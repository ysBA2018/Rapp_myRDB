$(document).ready(function(){
    var index = window.dotI;
    var svg = d3.select("#profileLegendSVG"+index);

    var data = window['dotData'+index];
    var j = 0;

    svg.append("circle").style('fill', function () {
        return d3.hsl(window['dotData'+index].color,0.5,0.5);
    }).attr("cx",20).attr("cy",32).attr("r", 6);

    svg.append("text").attr("x", 35).attr("y", 38).text(data.tf_technische_plattform).style("font-size", function () {
        var strLen = this.textContent.length;
        if(strLen<16){return "15px"}
        if(strLen>=16 && strLen <20){return "12px"}
        else{return "10px"}
    }).attr("alignment-baseline","middle");
    window.dotI+=1;

});