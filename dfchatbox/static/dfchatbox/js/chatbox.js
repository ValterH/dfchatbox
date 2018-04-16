//ČE UPORABNIK FUKNE NOT JS, IZVEDE. ONEMOGOČI!

var j = 0;

//RETURNS CURRENT TIME
function cur_date(){
    var n = new Date
        , date = "";

    date += " (" + ("0" + n.getHours()).slice(-2) + ":" + ("0" + n.getMinutes()).slice(-2) + ":" + ("0" + n.getSeconds()).slice(-2) + ")";
    return date
};

//FORMATS THE DATE
function format_date(date){
};

//ADDS ANIMATED BUBBLES WHEN USER IS TYPING
function typing(start,typer) {
    if (start) {
        $(".socketchatbox-chatArea").append('<div class="socketchatbox-message-wrapper" id="typing_wrapper"><div style="width:150px;height:20px;" class="socketchatbox-message socketchatbox-message-' + typer + '"><span style="width:100%;height:100%;" class="socketchatbox-messageBody socketchatbox-messageBody-' + typer + '"><div class="cssload-loader"><div></div><div></div><div></div><div></div><div></div></div></span></div></div>');
        document.getElementById("typing_wrapper").scrollIntoView({behavior: "smooth"});
    }
    else {
        $("#typing_wrapper").remove();
    }
};

//DISABLES THE INPUT FIELD WHEN INPUT IS BEING PROCESSED
function disable_input(start) {
    if (start) {
        $("#inputField").prop('disabled', true);
    }
    else {
        $("#inputField").prop('disabled', false);
    }
};

//TAKES USER INPUT AND COMMUNICATES WITH DIALOGFLOW
function communicate(message,j){
    disable_input(true);
    typing(1,"me");

    //CHECKS FOR URLS IN THE QUERY

    $.post('/check_links', {'message':message}, function(response){

    if (response != ""){
        //APPEND THE URL TITLE AND IMAGE OF THE WEBSITE IF THERE ARE LINKS
        data = JSON.parse(response);
        static_string = "static/dfchatbox/img/" + data['image_name']

        typing(0,"me");

        $(".socketchatbox-chatArea").append( '<div class="socketchatbox-message-wrapper" id="wrapper' + j + '"><div class="socketchatbox-message socketchatbox-message-me"><div class="socketchatbox-username">Uporabnik<span class="socketchatbox-messagetime">' + date + '</span></div><span class="socketchatbox-messageBody socketchatbox-messageBody-me">' + message +  '</span><br><span class="socketchatbox-messageBody socketchatbox-messageBody-me"><a target="_blank" href="' + data['url'] + '">' + data['data'] + '</a><img src="' + static_string + '" style="width:100%;height:100%;"></span></div></div>');
        }
    else {
        //APPEND THE MESSAGE IF THERE ARE NO URLS 
        typing(0,"me");

        $(".socketchatbox-chatArea").append( '<div class="socketchatbox-message-wrapper" id="wrapper' + j + '"><div class="socketchatbox-message socketchatbox-message-me"><div class="socketchatbox-username">Uporabnik<span class="socketchatbox-messagetime">' + date + '</span></div><span class="socketchatbox-messageBody socketchatbox-messageBody-me">' + message +  '</span></div></div>');
    }

    document.getElementById("wrapper" + j).scrollIntoView({behavior: "smooth"});

    //DIALOFLOW RESPONSE

    typing(1,"others");

    //$(".socketchatbox-typing").show();

    //SENDS DATA TO DJANGO WHICH COMMUNICATES WITH DIALOFLOW
    $.post(window.location.href, {"message": message},function(response){

        try {
            //DIALOGFLOW RESPONSE CONTAINS DATA
            response = JSON.parse(response);

            if (response['data'] == "" || response['data'] == "[]") {
                throw "No data"
            }

            try {
                $("#URLiFrame").remove();
            }
            catch(err){}

            if (response['url']) {
                $("body").append('<iframe frameborder="0" style="overflow:hidden;height:100%;width:100%" id="URLiFrame" src="' + response['url'] + '" height="100%" width="100%"></iframe>')
            }

            typing(0,"others");

            //APPENDS TEXT RESPONSE
            $(".socketchatbox-chatArea").append( '<div style="padding-bottom:1%;" class="socketchatbox-message-wrapper" id="wrapper' + j + '"><div class="socketchatbox-message socketchatbox-message-others"><div class="socketchatbox-username">DialogFlow<span class="socketchatbox-messagetime">' + date + '</span></div><span class="socketchatbox-messageBody socketchatbox-messageBody-others">' + response['text_answer'] + '</span><br></div></div>');

            //<span id="option_holder' + j + '" class="socketchatbox-messageBody socketchatbox-messageBody-me"></span>

            var i = 0;

            //*************************************************************************** USER OPTION BUTTONS ***********************************************************************************************
            // for (msg in response) {
            //     $(".socketchatbox-chatArea").append('<button class="choice_btn socketchatbox-messageBody socketchatbox-messageBody-me" id="btn' + i + j + '" type="button">' + response[i] + '</button>');
            //     i += 1;
            // }
            //*************************************************************************** USER OPTION BUTTONS ***********************************************************************************************


            data = JSON.parse(response['data'].replace(/'/g, '"'));
            response_type = response['response_type'];

            if (response_type == "list") {
                //DATA IS LIST OF JSON OBJECTS
                for (var k = 0; k < data.length; k++) {
                    var keys = Object.keys(data[k]);
                    var slo_keys = ["Datum","Ime","Vrednost"];

                    var oldDateFormat = new Date(data[k]['date']);
                    data[k]['date'] = oldDateFormat.toLocaleDateString();

                    $(".socketchatbox-chatArea").append( '<div style="padding:0;" class="socketchatbox-message-wrapper" id="wrapper' + j + i + '"><div id="holder' + j + i + '" class="socketchatbox-message socketchatbox-message-others"><span style="margin-top:1%;margin-bottom:1%;width:200px;" id="data' + j + i + '" class="socketchatbox-messageBody socketchatbox-messageBody-others"></span></div></div>');

                    for (var l = 0; l < keys.length; l++) {
                        //console.log("KEY,PROP: " + key + " " + msg[key]);
                        $("#data" + j + i).append(slo_keys[l] + ": " + data[k][keys[l]] + "<br>");
                    };

                    i+=1;
                }
            }

            else if (response_type == "userInfo") {
                //DATA IS USER INFO
                var keys = Object.keys(data);
                var slo_keys = ["Priimek","Ime","Datum rojstva","Spol"];

                if (data['gender'] == "MALE"){
                    data[keys[1]] = "Moški";
                }
                else {
                    data['gender'] = "Ženski";
                };


                var oldDateFormat = new Date(data['dateofbirth']);
                data['dateofbirth'] = oldDateFormat.toLocaleDateString();

                $(".socketchatbox-chatArea").append( '<div style="padding:0;" class="socketchatbox-message-wrapper" id="wrapper' + j + i + '"><div id="holder' + j + i + '" class="socketchatbox-message socketchatbox-message-others"><span style="margin-top:1%;margin-bottom:2%;width:300px;" id="data' + j + i + '" class="socketchatbox-messageBody socketchatbox-messageBody-others"></span></div></div>');

                for (var l = 0; l < keys.length; l++) {
                        $("#data" + j + i).append(slo_keys[l] + ": " + data[keys[l]] + "<br>");
                };

                i+=1;

            }

            //$(".socketchatbox-typing").hide();
            disable_input(false);
            document.getElementById("data" + j + (i-1)).scrollIntoView({behavior: "smooth"});
        }
        catch(err) {
            //DIALOGFLOW RESPONSE DOES NOT CONTAIN DATA

            typing(0,"others");

            $(".socketchatbox-chatArea").append( '<div class="socketchatbox-message-wrapper" id="wrapper' + j + '"><div class="socketchatbox-message socketchatbox-message-others"><div class="socketchatbox-username">DialogFlow<span class="socketchatbox-messagetime">' + date + '</span></div><span class="socketchatbox-messageBody socketchatbox-messageBody-others">' + response['text_answer'] +  '</span></div></div>');

            //$(".socketchatbox-typing").hide();
            disable_input(false);
            document.getElementById("wrapper" + j).scrollIntoView({behavior: "smooth"});
        }

        date = cur_date();
    });

    document.getElementById("wrapper" + j).scrollIntoView({behavior: "smooth"});
    });
};

//SHOWS AND HIDES CHATBOX
$("#socketchatbox-top").click(function(){
    if ($("#socketchatbox-body").is(":visible")){
        $("#socketchatbox-showHideChatbox").text("↑");
    }
    else {
        $("#socketchatbox-showHideChatbox").text("↓");
    }

    $("#socketchatbox-body").toggle();
});

//PROCESSES DATA FROM INPUT FIELD WHEN USER CLICKS ENTER
$(".socketchatbox-page").keydown(function(t){
    if (t.which == 13) {
        var message = $(".socketchatbox-inputMessage").val();

        if (message == "") {
            return
        }
        if (!message.replace(/\s/g, '').length) {
            return
        }

        document.getElementById("inputField").value =  "";

        date = cur_date();

        communicate(message,j);

        j += 1;
    }
});

//PROCESSES DATA FROM INPUT FIELD WHEN USER CLICKS THE BUTTON
$("#socketchatbox-sendFileBtn").click(function(t){
    var message = $(".socketchatbox-inputMessage").val();

    if (message == "") {
        return
    }
    if (!message.replace(/\s/g, '').length) {
            return
    }

    document.getElementById("inputField").value =  "";

    date = cur_date();

    communicate(message,j);

    j += 1;    
});

//REMOVES CHOICE BUTTONS
$(document).on("click", ".choice_btn", function(){
    message = document.getElementById(event.target.id).innerHTML;
    $(".choice_btn").fadeOut(100, function(){ $(this).remove();});

    communicate(message,j);
    j += 1;
});

//BOX RESIZING
var a = -1
  , i = -1
  , s = null;

$(".socketchatbox-resize").mousedown(function(event) {
    a = event.clientX; 
    i = event.clientY; 
    s = $(this).attr("id"),
    event.preventDefault(),
    event.stopPropagation()
});

$(document).mousemove(function(event) {
    if (-1 != a) {
        var t = $("#socketchatbox-body").outerWidth()
          , o = $("#socketchatbox-body").outerHeight()
          , c = event.clientX - a
          , r = event.clientY - i;
        s.indexOf("n") > -1 && (o -= r),
        s.indexOf("w") > -1 && (t -= c),
        s.indexOf("e") > -1 && (t += c),
        250 > t && (t = 250),
        70 > o && (o = 70),
        $("#socketchatbox-body").css({
            width: t + "px",
            height: o + "px"
        }),
        a = event.clientX,
        i = event.clientY
    }
});

$(document).mouseup(function() {
    a = -1,
    i = -1
});

//OLD DIALOGFLOW RESPONSE FUNCTION

    // $.post(window.location.href, {"message": message},function(response){
    //     console.log(response);
    //     console.log(typeof(response));

    //     try {
    //         //DIALOGFLOW RESPONSE CONTAIN DATA

    //         response = JSON.parse(response);
    //         console.log(response);

    //         typing(0,"others");

    //         $(".socketchatbox-chatArea").append( '<div class="socketchatbox-message-wrapper" id="wrapper' + j + '"><div class="socketchatbox-message socketchatbox-message-me"><div class="socketchatbox-username">DialogFlow<span class="socketchatbox-messagetime">' + date + '</span></div><span class="socketchatbox-messageBody socketchatbox-messageBody-others">Choose your reply:</span><br></div></div>');

    //         //<span id="option_holder' + j + '" class="socketchatbox-messageBody socketchatbox-messageBody-me"></span>

    //         var i = 0;

    //         for (msg in response) {
    //             $(".socketchatbox-chatArea").append('<button class="choice_btn socketchatbox-messageBody socketchatbox-messageBody-me" id="btn' + i + j + '" type="button">' + response[i] + '</button>');
    //             i += 1;
    //         }

    //         //$(".socketchatbox-typing").hide();
    //         //disable_input(false);
    //         document.getElementById("btn" + (i-1) + j).scrollIntoView({behavior: "smooth"});
    //     }
    //     catch(err) {
    //         //DIALOGFLOW RESPONSE DOES NOT CONTAIN DATA

    //         console.log("Couldn't parse.", err)
    //         typing(0,"others");

    //         $(".socketchatbox-chatArea").append( '<div class="socketchatbox-message-wrapper" id="wrapper' + j + '"><div class="socketchatbox-message socketchatbox-message-others"><div class="socketchatbox-username">DialogFlow<span class="socketchatbox-messagetime">' + date + '</span></div><span class="socketchatbox-messageBody socketchatbox-messageBody-others">' + response +  '</span></div></div>');

    //         //$(".socketchatbox-typing").hide();
    //         disable_input(false);
    //         document.getElementById("wrapper" + j).scrollIntoView({behavior: "smooth"});
    //     }

    //     date = cur_date();
    // });

