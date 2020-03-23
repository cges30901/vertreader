//Set margin of body to prevent beginning of document not displaying.
//This needs more investigation.
var bodyMargin = 8
document.body.style.marginLeft = bodyMargin + 'px'
document.body.style.marginRight = bodyMargin + 'px'

var el = document.querySelectorAll('img');
for(var i = 0; i < el.length; i++){
    //wrap image in div so two consecutive images can be separated
    var wrapper = document.createElement('div');
    el[i].parentNode.insertBefore(wrapper, el[i]);
    wrapper.appendChild(el[i]);

    //prevent pagination failure when wide images exist
    el[i].style.maxHeight = "100%";
    el[i].style.maxWidth = window.innerWidth - bodyMargin * 2 + "px";
    el[i].style.margin = 0;
}

//paginate with CSS Multiple Columns
var columnInit = Math.floor(document.documentElement.scrollWidth / window.innerWidth);
if(columnInit === 0){
    columnInit = 1
}
var column = columnInit;
//column <= columnInit * 2 is used to prevent infinite loop.
//I am not sure if this value is appropriate.
for(column = columnInit; column <= columnInit * 2; column++){
    document.body.style.columnCount = column;
    document.body.style.height = column + "00vh";
    if(document.documentElement.scrollWidth <= window.innerWidth){
        break;
    }
}

//hide scroll bar
document.body.style.overflow = 'hidden';

//send result to paginateFinished()
column

