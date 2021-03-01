const first_accent = document.querySelectorAll('.first_accent'),
      second_accent = document.querySelectorAll('.second_accent'),
      third_accent = document.querySelectorAll('.third_accent');

accent(first_accent);
accent(second_accent);
accent(third_accent);

function accent(q){

  q.forEach(el => el.addEventListener('mouseover', function(){
    for (let a=0; a<q.length; a++) {
      this_a = q[a]
      console.log(this_a);
      this_a.classList.add('hovered');
      //this_a.classList.add('hovered');
    }

    var highlight_reveals = document.querySelector('.'+el.classList[0]+'_trigger')
    var opacity = 0;

    function fadeIn(x) {
      if (opacity<1){
        opacity += .1;
        setTimeout(function(){fadeIn()},30);
      }
      document.querySelector('.'+el.classList[0]+'_trigger').style.opacity = opacity;
    }

    fadeIn(highlight_reveals);

    highlight_reveals.style.background = 'black';
    highlight_reveals.style.color = '#ffd9d3';
    //document.querySelector()

  }))

    q.forEach(el => el.addEventListener('mouseleave', function(){
      for (let a=0; a<q.length; a++) {
        this_a = q[a]
        this_a.classList.remove('hovered');
        //this_a.classList.add('hovered');
      }

      var highlight_reveals = document.querySelector('.'+el.classList[0]+'_trigger')
      var opacity = 1;

      function fadeOut(x) {
        if (opacity>0.3){
          opacity -= .1;
          setTimeout(function(){fadeOut()},20);
        }
        document.querySelector('.'+el.classList[0]+'_trigger').style.opacity = opacity;
      }

      fadeOut(highlight_reveals);

      highlight_reveals.style.background = '#E7ECEF';
      highlight_reveals.style.color = '#121314';

      }))

}
