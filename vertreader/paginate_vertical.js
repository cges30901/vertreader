//hide scroll bar
document.body.style.overflow = 'hidden';

//Set margin of body to prevent large margin at left and right
//when margin is percentage.
marginLeft = parseInt(window.getComputedStyle(document.body).marginLeft);
marginRight = parseInt(window.getComputedStyle(document.body).marginRight);
document.body.style.marginRight = marginRight + "px";
document.body.style.marginLeft = marginLeft + "px";

//Set columnGap to look like body margin
marginTop = parseInt(window.getComputedStyle(document.body).marginTop);
marginBottom = parseInt(window.getComputedStyle(document.body).marginBottom);
document.body.style.columnGap = marginTop + marginBottom + 'px';

var el = document.querySelectorAll('img');
for(var i = 0; i < el.length; i++){
    //prevent pagination failure when wide images exist
    el[i].style.maxHeight = "100%";
    el[i].style.maxWidth = window_width - marginLeft - marginRight + "px";
    // Fix image aspect ratio when publisher set "width: 100%;"
    el[i].style.width = "auto";
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

var columnInit = Math.floor(document.documentElement.scrollWidth / window_width);
if(columnInit === 0){
    columnInit = 1;
}
var column = columnInit;
//column <= columnInit * 2 is used to prevent infinite loop.
//I am not sure if this value is appropriate.
for(column = columnInit; column <= columnInit * 2; column++){
    document.body.style.columnCount = column;
    document.documentElement.style.height = column * window_height + "px";
    if(document.body.scrollWidth + marginLeft + marginRight <= window_width){
        break;
    }
}

if(column > columnInit * 2){
    //pagination failed
    column--;
    var fail = 1;
}
else{
    var fail = 0;
}
//send result to paginateFinished()
[column, fail];
