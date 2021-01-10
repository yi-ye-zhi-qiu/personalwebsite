var post1 = document.querySelector(".post1");
console.log(post1);

post1.addEventListener('click', () => {
  var post1_content = post1.querySelector(".content")
  console.log(post1_content);
  if (post1_content.style.display === "none") {
     post1_content.style.display = "block";
  } else {
     post1_content.style.display = "none";
  }
 })
