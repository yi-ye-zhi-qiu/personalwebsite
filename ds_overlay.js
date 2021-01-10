var paths =
[ "manhattan_distribution.svg", "manhattan_income.svg", "manhattan_heatmap.png"];

var img = document.getElementById("img");
var i = 0;
var timer = setInterval(function(){
// If we've reached the end of the array...
  if(i >= paths.length){
    i=0;
  }
  img.src = paths[i++];
}, 1000);
