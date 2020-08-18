var el = document.querySelectorAll('a');
for(var i = 0; i < el.length; i++){
    if(el[i].getAttribute("epub:type") == "noteref"){
        note = document.getElementById(el[i].getAttribute("href").slice(1));
        el[i].addEventListener("click", function(event){
            showFootnote(note.innerText);
            event.preventDefault();
        });
    }
}

function showFootnote(note) {
  window.alert(note);
}
