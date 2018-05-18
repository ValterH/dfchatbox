//ČE UPORABNIK FUKNE NOT JS, IZVEDE. ONEMOGOČI!
//INIT
var j = 0;

$(document).ready(function(){
    //localStorage.removeItem("sessionID");
    //session_isValid();
    $("#socketchatbox-sendFileBtn").css("background","#9a969a");
    $(".arrow-right").css("border-left","25px solid #bcbabb")
    //console.log("SESSION ID: " + localStorage.getItem("sessionID"));
});

$(".socketchatbox-page").keydown(function(t){
    var message = $(".socketchatbox-inputMessage").val();

    if (message == "") {
        $("#socketchatbox-sendFileBtn").css("background","#9a969a");
        $(".arrow-right").css("border-left","25px solid #bcbabb");
    }
    if (!message.replace(/\s/g, '').length) {
        $("#socketchatbox-sendFileBtn").css("background","#9a969a");
        $(".arrow-right").css("border-left","25px solid #bcbabb");
    }
    else {
        $("#socketchatbox-sendFileBtn").css("background","#4DACFF");
        $(".arrow-right").css("border-left","25px solid #80DFFF");
    }
});


//EXTREMELY FANCY USER SESSION ID GENERATOR, MIGHT BE IMPROVED LATER
function UUSID() {
    return Math.floor(10000000*Math.random())
};

//SET SESSION ID
function set_sessionID() {
    var sessionID = UUSID();

    localStorage.setItem("sessionID",sessionID);
    localStorage.setItem("sessionStart",timestamp())
};

//UNIX TIMESTAMP
function timestamp() {
    var timestamp = new Date;
    return timestamp.getTime()/1000
};

//CHECK THE VALIDITY OF SESSION AND SET IT IF NOT VALID
function session_isValid() {
    var sessionTimeout = 900;

    var sessionID = localStorage.getItem("sessionID");
    var sessionStart = localStorage.getItem("sessionStart");

    var currentTime = timestamp();

    if (sessionID != null && sessionStart != null) {
        if ((currentTime - sessionStart) > sessionTimeout) {
            set_sessionID();
            return false
        }
        else {
            return true
        }
    }
    else {
        set_sessionID();
        return false
    }
};

//SET SESSION INDEX
$(document).ready(function(){
    if (sessionStorage.getItem("index") == null) {
        sessionStorage.setItem("index",0);
    }
});

//RETURNS CURRENT TIME
function cur_date() {
    var n = new Date
        , date = "";

    date += " (" + ("0" + n.getHours()).slice(-2) + ":" + ("0" + n.getMinutes()).slice(-2) + ":" + ("0" + n.getSeconds()).slice(-2) + ")";
    return date
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
        $("#socketchatbox-sendFileBtn").css("background","#9a969a");
        $(".arrow-right").css("border-left","25px solid #bcbabb");
        $(".socketchatbox-inputMessage").css("border","1px solid #9a969a");
    }
    else {
        $("#inputField").prop('disabled', false);
        $("#socketchatbox-sendFileBtn").css("background","#4DACFF");
        $(".arrow-right").css("border-left","25px solid #80DFFF");
        $(".socketchatbox-inputMessage").css("border","1px solid #4DACFF");
    }
};


//SAVES CONVERSATION TO SESSION STORAGE
function saveElement(element) {
        var index = sessionStorage.getItem("index");

        sessionStorage.setItem(index, element);
        sessionStorage.setItem("index", parseInt(index) + 1);
};

//RELOADS SAVED CONVERSATION
function reload_session_storage() {
    if (j == 0){
        var index = parseInt(sessionStorage.getItem("index"));

        if (index == 0) {
            return
        }

        for (var i = 0; i < index; i++) {
            var element = sessionStorage.getItem(i);
            $(".socketchatbox-chatArea").append(element)
        }

        parser = new DOMParser();
        element = parser.parseFromString(element, "text/xml");

        document.getElementById(element.firstChild.id).scrollIntoView({behavior: "instant"});

        j = Math.floor(index/2.0);

    }
};

//TAKES USER INPUT AND COMMUNICATES WITH DIALOGFLOW
function communicate(message,j){
    disable_input(true);
    typing(1,"me");

    if (typeof(message) == 'object'){
        var value = message[0];
        message = message[1];
    }

    message = message.replace(/</g, "&lt;").replace(/>/g, "&gt;");

    //CHECKS FOR URLS IN THE QUERY
    ////////////////////////////////////////////////////////////////////////////////// CURRENTLY DISABLED URL CHECKING //////////////////////////////////////////////////////////////////////////////////////
    //$.post('/check_links', {'message':message}, function(response){

    //if (response != ""){
    ////////////////////////////////////////////////////////////////////////////////// CURRENTLY DISABLED URL CHECKING //////////////////////////////////////////////////////////////////////////////////////
    if (false){
        //APPEND THE URL TITLE AND IMAGE OF THE WEBSITE IF THERE ARE LINKS
        data = JSON.parse(response);
        static_string = "static/dfchatbox/img/" + data['image_name']

        typing(0,"me");

        var reply_me = '<div class="socketchatbox-message-wrapper" id="wrapper-me' + j + '"><div class="socketchatbox-message socketchatbox-message-me"><div class="socketchatbox-username">Uporabnik<span class="socketchatbox-messagetime">' + date + '</span></div><span class="socketchatbox-messageBody socketchatbox-messageBody-me">' + message +  '</span><br><span class="socketchatbox-messageBody socketchatbox-messageBody-me"><a target="_blank" href="' + data['url'] + '">' + data['data'] + '</a><img src="' + static_string + '" style="width:100%;height:100%;"></span></div></div>';

        $(".socketchatbox-chatArea").append(reply_me);

        //SAVING TO SESSION STORAGE
        saveElement(reply_me);

        }

    else {
        //APPEND THE MESSAGE IF THERE ARE NO URLS 
        typing(0,"me");

        var reply_me = '<div class="socketchatbox-message-wrapper" id="wrapper-me' + j + '"><div class="socketchatbox-message socketchatbox-message-me"><div class="socketchatbox-username">Uporabnik<span class="socketchatbox-messagetime">' + date + '</span></div><span class="socketchatbox-messageBody socketchatbox-messageBody-me">' + message +  '</span></div></div>';

        $(".socketchatbox-chatArea").append(reply_me);

        //SAVING TO SESSION STORAGE
        saveElement(reply_me);

    }

    document.getElementById("wrapper-me" + j).scrollIntoView({behavior: "smooth"});

    //DIALOFLOW RESPONSE

    typing(1,"others");

    //$(".socketchatbox-typing").show();

    if (value) {
        message = value;
    }

    //CHECKS SESSION
    session_isValid();
    var sessionID = localStorage.getItem("sessionID");
    localStorage.setItem("sessionStart", timestamp());

    //SENDS DATA TO DJANGO WHICH COMMUNICATES WITH DIALOFLOW
    $.post(window.location.href, {"message": message, "sessionID": sessionID},function(response){

        try {
            //DIALOGFLOW RESPONSE CONTAINS DATA
            response = response.replace(/\n/g, "\\n");
            response = response.replace(/\r/g, "\\r");
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
            var reply_others = '<div style="padding-bottom:1%;" class="socketchatbox-message-wrapper" id="wrapper-others' + j + '"><div class="socketchatbox-message socketchatbox-message-others"><div class="socketchatbox-username">DialogFlow<span class="socketchatbox-messagetime">' + date + '</span></div><span class="socketchatbox-messageBody socketchatbox-messageBody-others">' + response['text_answer'] + '</span><br></div></div>';

            $(".socketchatbox-chatArea").append(reply_others);

            saveElement(reply_others);;

            //<span id="option_holder' + j + '" class="socketchatbox-messageBody socketchatbox-messageBody-me"></span>

            var i = 0;

            //*************************************************************************** USER OPTION BUTTONS ***********************************************************************************************
            // for (msg in response) {
            //     $(".socketchatbox-chatArea").append('<button class="choice_btn socketchatbox-messageBody socketchatbox-messageBody-me" id="btn' + i + j + '" type="button">' + response[i] + '</button>');
            //     i += 1;
            // }
            //*************************************************************************** USER OPTION BUTTONS ***********************************************************************************************

            console.log(response['data']);
            data = JSON.parse(response['data'].replace(/'/g, '"'));
            response_type = response['response_type'];
            if (response_type == "list") {
                //DATA IS LIST OF JSON OBJECTS
                console.log(data.length);
                console.log(data[0]);
                for (var k = 0; k < data.length; k++) {
                    var keys = Object.keys(data[k]);
                    var slo_keys = ["Datum","Ime","Vrednost"];

                    var oldDateFormat = new Date(data[k]['date']);
                    data[k]['date'] = oldDateFormat.toLocaleDateString();

                    var reply_others = '<div style="padding:0;" class="socketchatbox-message-wrapper" id="wrapper' + j + i + '"><div id="holder' + j + i + '" class="socketchatbox-message socketchatbox-message-others"><span style="margin-top:1%;margin-bottom:1%;width:200px;" id="data' + j + i + '" class="socketchatbox-messageBody socketchatbox-messageBody-others">'

                    //$(".socketchatbox-chatArea").append( '<div style="padding:0;" class="socketchatbox-message-wrapper" id="wrapper' + j + i + '"><div id="holder' + j + i + '" class="socketchatbox-message socketchatbox-message-others"><span style="margin-top:1%;margin-bottom:1%;width:200px;" id="data' + j + i + '" class="socketchatbox-messageBody socketchatbox-messageBody-others"></span></div></div>');

                    for (var l = 0; l < keys.length; l++) {
                        reply_others += slo_keys[l] + ": " + data[k][keys[l]] + "<br>";
                        //$("#data" + j + i).append(keys[l] + ": " + data[k][keys[l]] + "<br>");
                    };

                    reply_others += '</span></div></div>';

                    $(".socketchatbox-chatArea").append(reply_others);

                    saveElement(reply_others);

                    i+=1;
                }
                disable_input(false);

                $("#inputField").focus();
            }

            else if (response_type == "entry") {
                //DATA IS DICTIONARY
                console.log("entry");
                var keys = Object.keys(data);
                console.log(keys);

                if (response['tree_url']) {
                    $("body").append('<iframe frameborder="0" style="overflow:hidden;height:100%;width:100%" id="URLiFrame" src="' + response['tree_url'] + '" height="100%" width="100%"></iframe>')
                }

                for (var k = 0; k < keys.length; k++) {

                    var reply_others = '<div style="padding:0;" class="socketchatbox-message-wrapper" id="wrapper' + j + i + '"><div id="holder' + j + i + '" class="socketchatbox-message socketchatbox-message-others"><span style="margin-top:1%;margin-bottom:1%;width:300px;" id="data' + j + i + '" class="socketchatbox-messageBody socketchatbox-messageBody-others">'

                    reply_others += keys[k] + ": " + data[keys[k]] + "<br>";


                    reply_others += '</span></div></div>';

                    $(".socketchatbox-chatArea").append(reply_others);

                    saveElement(reply_others);

                    i+=1;
                }
                disable_input(false);

                $("#inputField").focus();
            }
            
            else if (response_type == "waitingTimes") {
                    //DATA IS LIST OF JSON OBJECTS
                    for (var k = 0; k < data.length; k++) {
                    var keys = ["hospital","reception","email","phone"]
                    var slo_keys = ["Bolnišnica","Sprejem","E-mail","Telefon"];

                    var oldDateFormat = new Date(data[k]['date']);
                    data[k]['date'] = oldDateFormat.toLocaleDateString();

                    var reply_others = '<div style="padding:0;" class="socketchatbox-message-wrapper" id="wrapper' + j + i + '"><div id="holder' + j + i + '" class="socketchatbox-message socketchatbox-message-others"><span style="margin-top:1%;margin-bottom:1%;width:300px;" id="data' + j + i + '" class="socketchatbox-messageBody socketchatbox-messageBody-others">'


                    for (var l = 0; l < keys.length; l++) {
                        if (typeof(data[k][keys[l]]) == 'object'){
                            reply_others += slo_keys[l] + ": ";
                            reception = data[k][keys[l]];
                            //reception = JSON.parse(data[k][keys[l]]);

                            reception_keys = ["availability", "days_to"];
                            if (isNaN(reception[reception_keys[1]])){
                                reply_others += reception[reception_keys[0]] + "<br>";
                            }
                            else if (reception[reception_keys[1]] == 1){
                                reply_others += reception[reception_keys[0]] + " (čez " + reception[reception_keys[1]] + " dan)" + "<br>";
                            }
                            else {
                                reply_others += reception[reception_keys[0]] + " (čez " + reception[reception_keys[1]] + " dni)" + "<br>";
                            }

                            // for (var m = 0; m < reception_keys.length; m++) {
                            //     reply_others += reception[m]
                            // }
                        }
                        else {
                            reply_others += slo_keys[l] + ": " + data[k][keys[l]] + "<br>";
                        }
                    };

                    reply_others += '</span></div></div>';

                    $(".socketchatbox-chatArea").append(reply_others);

                    saveElement(reply_others);
                    last = "" + j + i;
                    i+=1;
                }
                disable_input(false);
                console.log("wrapper" + last);
                $("#inputField").focus();
                document.getElementById("wrapper" + last).scrollIntoView({behavior: "smooth"});
            }

            else if (response_type == "userInfo") {
                //DATA IS USER INFO
                var keys = Object.keys(data);
                var slo_keys = ["Ime","Priimek","Spol","Datum rojstva"];

                if (data['gender'] == "MALE"){
                    data[keys[1]] = "Moški";
                }
                else {
                    data['gender'] = "Ženski";
                };


                var oldDateFormat = new Date(data['dateofbirth']);
                data['dateofbirth'] = oldDateFormat.toLocaleDateString();

                reply_others = '<div style="padding:0;" class="socketchatbox-message-wrapper" id="wrapper' + j + i + '"><div id="holder' + j + i + '" class="socketchatbox-message socketchatbox-message-others"><span style="margin-top:1%;margin-bottom:2%;width:300px;" id="data' + j + i + '" class="socketchatbox-messageBody socketchatbox-messageBody-others">'

                //$(".socketchatbox-chatArea").append( '<div style="padding:0;" class="socketchatbox-message-wrapper" id="wrapper' + j + i + '"><div id="holder' + j + i + '" class="socketchatbox-message socketchatbox-message-others"><span style="margin-top:1%;margin-bottom:2%;width:300px;" id="data' + j + i + '" class="socketchatbox-messageBody socketchatbox-messageBody-others"></span></div></div>');

                for (var l = 0; l < keys.length; l++) {
                    reply_others += slo_keys[l] + ": " + data[keys[l]] + "<br>"
                        //$("#data" + j + i).append(slo_keys[l] + ": " + data[keys[l]] + "<br>");
                };

                reply_others += '</span></div></div>';

                $(".socketchatbox-chatArea").append(reply_others);

                saveElement(reply_others);

                i+=1;

                disable_input(false);

                $("#inputField").focus();

                document.getElementById("data" + j + (i-1)).scrollIntoView({behavior: "smooth"});

            }

            else if (response_type == "procedures") {
                //DATA GIVES OPTIONS FOR USER
                first = i.toString() + j.toString();
                for (var k = 0; k < data.length; k++) {
                    $(".socketchatbox-chatArea").append('<button name="' + data[k]['value'] + '" class="choice_btn socketchatbox-messageBody socketchatbox-messageBody-me" id="btn' + i + j + '" type="button">' + data[k]['name'] + '</button>');
                    i += 1;
                }

                //document.getElementById("btn" + first).scrollIntoView({behavior: "smooth"});
                document.getElementById("wrapper-others" + j).scrollIntoView({behavior: "smooth"});
            }


           
        }
        catch(err) {
            console.log(err);
            //DIALOGFLOW RESPONSE DOES NOT CONTAIN DATA
            try {
                //return
            }
            catch(err){
            }

            typing(0,"others");
            console.log(err);
            var reply_others = '<div class="socketchatbox-message-wrapper" id="wrapper-others' + j + '"><div class="socketchatbox-message socketchatbox-message-others"><div class="socketchatbox-username">DialogFlow<span class="socketchatbox-messagetime">' + date + '</span></div><span class="socketchatbox-messageBody socketchatbox-messageBody-others">' + response['text_answer'] +  '</span></div></div>';

            $(".socketchatbox-chatArea").append(reply_others);
            saveElement(reply_others);

            //$(".socketchatbox-typing").hide();
            disable_input(false);

            $("#inputField").focus();

            document.getElementById("wrapper-others" + j).scrollIntoView({behavior: "smooth"});
        }

        date = cur_date();
    });
    //document.getElementById("wrapper-others" + j).scrollIntoView({behavior: "smooth"});
    //});
};

//SHOWS AND HIDES CHATBOX
$("#socketchatbox-top").click(function(){
    if ($("#socketchatbox-body").is(":visible")){
        $("#socketchatbox-showHideChatbox").text("↑");
    }
    else {
        $("#socketchatbox-showHideChatbox").text("↓");
        //LOAD SESSION STORAGE IF PAGE REFRESHED
        
    }

    $("#socketchatbox-body").toggle();

    setTimeout(function() {
        reload_session_storage();
    }, 100);

    $("#inputField").focus();
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

        $("#inputField").focus();

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

    $("#inputField").focus();

    j += 1;    
});

//REMOVES CHOICE BUTTONS
$(document).on("click", ".choice_btn", function(){
    message1 = document.getElementById(event.target.id).name;
    message2 = document.getElementById(event.target.id).innerHTML;
    message = [message1,message2];
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



//old RELOADS SAVED CONVERSATION
// function reload_session_storage() {
//     if (j == 0){
//         console.log("are we doing this? j = " + j)
//         //try {
//             while (true) {
//                 console.log(j);
//                 if (sessionStorage.getItem("me-" + j) == null){
//                     console.log("No saved data");
//                     console.log("wrapper-others" + (j-1));
//                     console.log(document.getElementById("wrapper-others" + (j-1)));
//                     console.log("scrolling into view");
//                     document.getElementById("wrapper-others" + (j-1)).scrollIntoView({behavior: "instant"});

//                     return

//                 }

//                 $(".socketchatbox-chatArea").append(sessionStorage.getItem("me-" + j));
//                 $(".socketchatbox-chatArea").append(sessionStorage.getItem("others-" + j));

//                 for (var l = 0; true; l++) {
//                     console.log(l);
//                     if (sessionStorage.getItem("others-" + j + l) == null) {
//                         console.log("no more appended data");
//                         break;
//                     }
//                     else {
//                         $(".socketchatbox-chatArea").append(sessionStorage.getItem("others-" + j + l));
//                     }
//                 }

//                 try {
//                     // console.log("J,L: " + j + l);
//                     // console.log("wrapper-others" + j);
//                     // console.log(document.getElementById("wrapper-others" + j));
//                 }
//                 catch(err){
//                     console.log(err);
//                 }

//                 j += 1;
//             }

//         //}
//         //catch(err) {
//         //    console.log(err);
//         //}
//     }
// };