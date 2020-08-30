var modal = document.createElement("div");
modal.style.display = "none";
modal.style.position = "fixed";
modal.style.zIndex = 1;
modal.style.left = 0;
modal.style.top = 0;
modal.style.width = "100%";
modal.style.height = "100%";
modal.style.backgroundColor = "rgba(0,0,0,0.4)";
modal.style.flexDirection = "column-reverse";// Put modalContent to the left

var modalContent = document.createElement("div");
modalContent.style.backgroundColor = document.body.style.backgroundColor;
modalContent.style.maxWidth = "50%";
modalContent.style.overflow = "auto";
modalContent.style.height = "100%";
modalContent.style.padding = "10px";
modalContent.style.border = "1px solid";

modal.appendChild(modalContent);
document.body.appendChild(modal);

var el = document.querySelectorAll('a');
for(var i = 0; i < el.length; i++){
    if(el[i].getAttribute("epub:type") == "noteref"){
        el[i].addEventListener("click", function(event){
            event.preventDefault();
            // Get href of footnote
            var href = event.currentTarget.getAttribute("href");
            // Remove characters before and including # to get id
            var note = document.getElementById(href.slice(href.lastIndexOf("#") + 1));
            modalContent.innerHTML = note.innerHTML;
            modal.style.display = "flex";
        });
    }
}

window.onclick = function(event) {
  if (event.target == modal) {
    modal.style.display = "none";
  }
}
