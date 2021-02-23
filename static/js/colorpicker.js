//changes css property constantly to change colors


//For movie backgrounds on movie image hover:
// array with colors
var colors = [
  "#7f78d2",
  "#efb1ff",
  "#ffe2ff",
  "#ffb3ba",
  "#ffdfba",
  "#baffc9",
  "#bae1ff"
];

// get random color from array
function getColor() {
   var color_picked = colors[
     Math.floor(Math.random() * colors.length)
   ];
   //set that random color equal to css variable for background color of movies
   document.documentElement.style.setProperty('--movie-bg-color', color_picked)
   //run this every 800 miliseconds
   setTimeout(getColor, 800);
}
//run function
getColor()

let scores = document.querySelectorAll('.value')

var hsv2rgb = function(h, s, v) {
  var rgb, i, data = [];
  if (s === 0) {
    rgb = [v,v,v];
  } else {
    h = h / 60;
    i = Math.floor(h);
    data = [v*(1-s), v*(1-s*(h-i)), v*(1-s*(1-(h-i)))];
    switch(i) {
      case 0:
        rgb = [v, data[2], data[0]];
        break;
      case 1:
        rgb = [data[1], v, data[0]];
        break;
      case 2:
        rgb = [data[0], v, data[2]];
        break;
      case 3:
        rgb = [data[0], data[1], v];
        break;
      case 4:
        rgb = [data[2], data[0], v];
        break;
      default:
        rgb = [v, data[0], data[1]];
        break;
    }
  }
  return '#' + rgb.map(function(x){
    return ("0" + Math.round(x*255).toString(16)).slice(-2);
  }).join('');
};

scores.forEach(score => {

  var val = score.innerHTML;

  if (val >= 8.0 ) {
    score.style.backgroundColor = '#68ff68'
  }
  if (val <= 8.0  && val > 7.9) {
    score.style.backgroundColor = '#56c783'
  }
  if (val <= 7.9  && val > 7.6) {
    score.style.backgroundColor = '#68cd91'
  }
  if (val <= 7.6  && val > 7.3) {
    score.style.backgroundColor = '#95f2aa'
  }
  if (val <= 7.3  && val > 7.0) {
    score.style.backgroundColor = '#ff8989'
  }
  if (val <= 7.0  && val > 6.8) {
    score.style.backgroundColor = '#f66'
  }
  if (val <= 6.8  && val > 6.6) {
    score.style.backgroundColor = '#ff1e1e'
  }
  
})
