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

//For saturation of red->green for Liamometer background-colors:

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


$(document).on({
    change: function(e) {

        var self = this,
            span = $(self).parent("span"),
            val = parseInt(self.value);
        if (val > 100) {
            val = 100;
        }
        else if (val < 0) {
            val = 0;
        }
        $(".value", span).text(val);

        var h= Math.floor((100 - val) * 120 / 100);
        var s = Math.abs(val - 50)/50;
        var v = 1;

        span.css({
            backgroundColor: hsv2rgb(h, s, 1)
        });
    }
}, "input[type='range']");
