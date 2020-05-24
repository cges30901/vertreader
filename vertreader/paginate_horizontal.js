//Set margin of body to prevent beginning of document not displaying.
//This needs more investigation.
var bodyMargin = 8
document.body.style.marginTop = bodyMargin + 'px'
document.body.style.marginBottom = bodyMargin + 'px'

//Set columnGap to look like body margin
marginRight = parseInt(window.getComputedStyle(document.body).marginRight);
marginLeft = parseInt(window.getComputedStyle(document.body).marginLeft);
document.body.style.columnGap = marginRight + marginLeft + 'px';

var el = document.querySelectorAll('img');
for(var i = 0; i < el.length; i++){
    //prevent pagination failure when wide images exist
    el[i].style.maxWidth = "100%";
    el[i].style.maxHeight = window.innerHeight - bodyMargin * 2 + "px";
    el[i].style.margin = 0;
    //This is used to avoid area under baseline.
    //See https://stackoverflow.com/a/60823927/3926429.
    //display:block also works, but images are no longer inline.
    el[i].style.verticalAlign = "middle";

    //Set image display to block so two consecutive images can be separated.
    //I should find a better method to keep images inline.
    el[i].style.display = "block";
}

//paginate with CSS Multiple Columns
var columnInit = Math.floor(document.documentElement.scrollHeight / window.innerHeight);
if(columnInit === 0){
    columnInit = 1
}
var column = columnInit;
//column <= columnInit * 2 is used to prevent infinite loop.
//I am not sure if this value is appropriate.
for(column = columnInit; column <= columnInit * 2; column++){
    document.body.style.columnCount = column;
    document.body.style.width = column + "00%";
    if(document.documentElement.scrollHeight <= window.innerHeight){
        break;
    }
}

//hide scroll bar
document.body.style.overflow = 'hidden';

if(column > columnInit * 2){
    //pagination failed
    column--
}

//send result to paginateFinished()
column

