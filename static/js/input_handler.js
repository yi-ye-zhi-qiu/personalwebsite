//focus input on page load
input = $("#input-box")
input.focus()

//form-delay;
const form = $("#riot-api-form");
    form.submit(() => {
  //some other functions you need to proceed before submit
    var box_opacity = $('.ghgtu').css('opacity', '1');
    setTimeout(() => {}, 5);
           return true;
});

//manipulate input datastate
const a = document.querySelector('input')
a.addEventListener('input', evt => {
  const value = a.value
  if (!value) {
    a.dataset.state = ''
    return
  }
  const trimmed = value.trim()
  if (trimmed) {
    a.dataset.state = 'valid'
  } else {
    a.dataset.state = 'invalid'
  }
})
