/*
jquery selector stuff -- this is the magic
*/

$(document).ready(function(){
	$('#tableToolList').tablesorter();
	$(".updateTool").on("click", updateDivForm);
	$("#addTool").on("click", updateDivForm);
	$(".borrowTool").on("click", updateDivFormBorrowTool);
    $(".denyRequest").on("click", updateDivForm);
    $('.request').on('click',fancyLoadDiv);
    $('.displayTool').on('click',fancyLoadDiv);
    $('.fancyLoad').on('click',fancyLoadDiv);
    $('.deleteTool').on('click',fancyLoadDivDelete);
	$('#updateUser').on('click', updateDivForm);
    $('#changePass').on('click', updateDivForm); 

    //this is how the above should be called -- too late in the game to change it all
    $('.fancyFromDiv').on('click', updateDivForm);
    $(".fancyLoadForm").on("click", updateDivForm);
    $('.toolDesc').text(function() {
        if ($(this).text().length > 40 ){
            return $(this).text().substring(0, 30) + "...";
        }
        return $(this).text().substring(0, 30); 
    });



});


/*
dynamically fills the div addTool with an ajax call to its coresponding view
    basically magic
*/
function fancyLoadDiv() {
    var url = $(this).attr('href');
    //alert(url);
    jQuery("#fancyUpdateContent").load(
        url,
        function(){
            //alert('made it to inner function');
            var updateData = $('#fancyUpdateContent').html();
            $.fancybox(updateData,
            {
                afterClose  :  function() {
                                    window.location.reload(true);
                                }
            });
        }
    );
    return false;
}
/*
dynamically fills the div addTool with an ajax call to its coresponding view
    basically magic
*/
function fancyLoadDivDelete() {
    var answer = confirm('Are you sure want to delete one of your tools?');
        if(!answer) {
            return false;
        }
    var url = $(this).attr('href');
    //alert(url);
    jQuery("#fancyUpdateContent").load(
        url,
        function(){
            //alert('made it to inner function');
            var updateData = $('#fancyUpdateContent').html();
            $.fancybox(updateData,
            {
                afterClose  :  function() {
                                    window.location.reload(true);
                                }
            });
        }
    );
    return false;
}
/*
dynamically fills the div addTool with an ajax call to its coresponding view
    basically magic
*/
function updateDivForm() {

    //alert("hi mom" + allDays)
    var url = $(this).attr('href');
    jQuery("#fancyUpdateContent").load(
        url,
        function(){
            var updateData = $('#fancyUpdateContent').html();
            $.fancybox(updateData,
            {
                afterClose  :  function() {
                                    window.location.reload(true);
                                }
            });
            prepareUpdateForm();
        }
    );

    return false;
}


/*
dynamically fills the form with the form data from its coresponding view
    if valid submits 
    otherwise displays error messages
this javascript has to be in the document from my understanding. It will not load otherwise.
*/
function prepareUpdateForm(){
    $('.fancybox-inner #sendbutton').on("click",function(){
        var form = jQuery(".fancybox-inner #fancyForm");
        form.submit(function (e) {
            //jQuery("#sendwrapper").prepend('<span>Sending message, please wait... </span>')
            jQuery(".fancybox-inner #container").load(
                form.prop('action'),
                form.serializeArray(),
                function(){
                    prepareUpdateForm();                   
                }

            );
            e.preventDefault();
        });
    });
}



/***************************************************
********   Update the borrow stuff   ***************                                                                                                
****************************************************/      


/* this is the calendar to pull days from */
var allDays;

/*
Is called before a date is rendered. If the date is reserved, returns an
array of [false, ''], otherwise, [true, '']
*/
function renderCalendarCallback(date) {
    //$(".timeStart").data('dates')[0];
    //alert($(".timeStart").data('dates')[0]);
    //alert($.inArray(  date.toJSON().substring(0,10),   $(".timeStart").data('dates')   )   );
    // magic
    // inArray returns the first index of the element in the array, so if the date
    // has index -1, the it's not a reserved date and we're good to go!
    return [$.inArray(date.toJSON().substring(0,10), $(".timeStart").data('dates')) == -1, ''];
}


/*
dynamically fills the div addTool with an ajax call to its coresponding view
    basically magic
*/
function updateDivFormBorrowTool() {

    //alert("hi mom" + allDays)
    var url = $(this).attr('href');
    //alert(url);
    jQuery("#fancyUpdateContent").load(
        url,
        function(){
            //alert('made it to inner function');
            var updateData = $('#fancyUpdateContent').html();
            $.fancybox(updateData,
            {
                openEffect  : 'none',
                closeEffect : 'none',
                afterClose  :  function() {
                                window.location.reload();
                            } 
            });

            prepareUpdateFormToolBorrow();
        }
    );

    return false;
}

/* Gets the last reservable day 
(called once a user selects a day in the first calendar */
function getLastDay(selectedDate) {
    selected = new Date(selectedDate);
    var length = $(".timeStart").data('dates').length
    var maxDate = null;

    // Assign maxDate to the largest date in the array (yes, I know this sucks)
    for (var i = 0; i < length; i++) {
        if (new Date($(".timeStart").data('dates')[i]) > maxDate) {
            maxDate = new Date($(".timeStart").data('dates')[i]);
        }
    }

    // Now step maxDate backwards as far as possible without passing selected
    for (var i = 0; i < length; i++) {
        if (   new Date($(".timeStart").data('dates')[i]) > selected
            && new Date($(".timeStart").data('dates')[i]) < maxDate) {
            maxDate = new Date($(".timeStart").data('dates')[i]);
        }
    }

    // If there are no reservations, maxDate is still null, thus there is no max date
    // If maxDate is somehow less than selected, abort
    if (maxDate == null || maxDate < selected) {
        return null;
    }
    else {
        return maxDate;
    }
}




function prepareUpdateFormToolBorrow(){
    $(".timeStart").datepicker('destroy');
    $('.timeStart').removeClass("hasDatepicker").removeAttr('id');  
    $(".timeStart").datepicker({
        beforeShowDay: renderCalendarCallback,
        minDate: "+0d",
        onClose: function( selectedDate ) {

            if (selectedDate == "") {
                $(".timeEnd").datepicker("option", "minDate", "+0d");
            }
            else {
                $(".timeEnd").datepicker("option", "minDate", selectedDate);
            }
            $(".timeEnd").datepicker("option", "maxDate", getLastDay(selectedDate));
            
        },
    });

    $(".timeEnd").datepicker('destroy');
    $('.timeEnd').removeClass("hasDatepicker").removeAttr('id');  
    $(".timeEnd").datepicker({
        beforeShowDay: renderCalendarCallback,
        minDate: "+0d",
        onClose: function( selectedDate ) {
            if (selectedDate === "") {
                $(".timeEnd").datepicker("option", "minDate", "+0d");
            }
            else {
                $(".timeEnd").datepicker("option", "minDate", selectedDate);
            }
            $(".timeEnd").datepicker("option", "maxDate", getLastDay(selectedDate));
        }

    });





    $('.fancybox-inner #sendbutton').on("click",function(){
        var form = jQuery(".fancybox-inner #fancyForm");
        form.submit(function (e) {
            //jQuery("#sendwrapper").prepend('<span>Sending message, please wait... </span>')
            jQuery(".fancybox-inner #container").load(
                form.prop('action'),
                form.serializeArray(),
                function(){


                    prepareUpdateFormToolBorrow();
                }

            );
            e.preventDefault();
        });
    });
}