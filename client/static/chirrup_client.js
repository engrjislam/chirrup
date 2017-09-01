const SERVER_LOCATION = "http://localhost:5000";
var DEBUG = true;

/**
 * Mason+JSON mime-type
 * @constant {string}
 * @default
 */
const MASONJSON = "application/vnd.mason+json";

const PLAINJSON = "application/json";
const DEFAULT_DATATYPE = "json";

function get_rooms(apiurl){
    apiurl = SERVER_LOCATION + apiurl;
    $.ajax({
        url: apiurl,
        dataType:DEFAULT_DATATYPE
    }).always(function(){

        $("#roomlist").empty();

    }).done(function (data, textStatus, jqXHR){
        if (DEBUG) {
            console.log ("RECEIVED RESPONSE: data:",data,"; textStatus:",textStatus);
        }

        var rooms = data["rooms-all"];

        for (let i = 0; i < rooms.length; i++) {

            var room = rooms[i];

            var name =  room.name;
            var room_url = "/room/" + room.room_id;

            appendRoomToList(room_url, name);

        }

    }).fail(function (jqXHR, textStatus, errorThrown){
        if (DEBUG) {
            console.log ("RECEIVED ERROR: textStatus:",textStatus, ";error:",errorThrown);
        }
        alert("Cannot get information from message: "+ apiurl);
    });
}

function get_users(apiurl){
    $.ajax({
        url: SERVER_LOCATION + apiurl,
        dataType:DEFAULT_DATATYPE
    }).always(function(){

        $("#userslist").empty();

    }).done(function (data, textStatus, jqXHR){
        if (DEBUG) {
            console.log ("RECEIVED RESPONSE: data:",data,"; textStatus:",textStatus);
        }

        var users = data["users-all"];

        for (let i = 0; i < users.length; i++) {

            var user = users[i];
            var name =  user.nickname;
            var user_url = "/user/" + user.user_id;
            appendUserToList(user_url, name);
        }

    }).fail(function (jqXHR, textStatus, errorThrown){
        if (DEBUG) {
            console.log ("RECEIVED ERROR: textStatus:",textStatus, ";error:",errorThrown);
        }
        alert("Cannot get information from message: "+ apiurl);
    });
}

function get_user(apiurl) {
    return $.ajax({
        url: SERVER_LOCATION + apiurl,
        dataType:DEFAULT_DATATYPE,
        processData:false
    }).done(function (data, textStatus, jqXHR){
        if (DEBUG) {
            console.log ("RECEIVED RESPONSE: data:",data,"; textStatus:",textStatus);
        }

        var $user = data;

        //Fill basic information from the user_basic_form
        $("#user_name").append($user.username);
        //delete(data.username);
        $("#nick_name").append($user.nickname || "??" );
        //delete(data.nickname);
        $("#image").val($user.image||"??");
        $("#nickname").val($user.nickname||"??");
        $("#username").val($user.username||"??");
        $("#email").val($user.email||"??");

        $("#user_form").attr("action", apiurl + "/");

        $("#picture").attr("src", "/" + $user.image);


    }).fail(function (jqXHR, textStatus, errorThrown){
        if (DEBUG) {
            console.log ("RECEIVED ERROR: textStatus:",textStatus, ";error:",errorThrown);
        }
        //Show an alert informing that I cannot get info from the user.
        alert ("Cannot extract information about this user from the forum service.");

    });
}

function get_messages(apiurl){
    $.ajax({
        url: SERVER_LOCATION + apiurl,
        dataType:DEFAULT_DATATYPE
    }).always(function(){

        $("#messages_list").empty();

    }).done(function (data, textStatus, jqXHR){
        if (DEBUG) {
            console.log ("get_messages: RECEIVED RESPONSE: data:",data,"; textStatus:",textStatus);
        }

        var messages = data["messages-all"];
        var max_messages;

        if (messages.length < 10 ) {
            max_messages = 0;
        } else
            max_messages = messages.length - 10;

        for (let i = messages.length - 1; i >= max_messages; i--) {

            var message = messages[i];
            appendMessageToList(message.content, message.sender);
            replaceIdWithName(message.sender);

        }

    }).fail(function (jqXHR, textStatus, errorThrown){
        if (DEBUG) {
            console.log ("RECEIVED ERROR: textStatus:",textStatus, ";error:",errorThrown);
        }
        alert("Cannot get information from message: "+ apiurl);
    });
}

function add_user(apiurl,user){
    var userData = JSON.stringify(user);
    console.log(userData);
    return $.ajax({
        url: apiurl,
        type: "POST",
        //dataType:DEFAULT_DATATYPE,
        data:userData,
        processData:false,
        contentType: PLAINJSON
    }).done(function (data, textStatus, jqXHR){
        if (DEBUG) {
            console.log ("RECEIVED RESPONSE: data:",data,"; textStatus:",textStatus);
        }
        alert ("User successfully added");
        //Add the user to the list and load it.

    }).fail(function (jqXHR, textStatus, errorThrown){
        if (DEBUG) {
            console.log ("RECEIVED ERROR: textStatus:",textStatus, ";error:",errorThrown);
        }
    });
}

function add_room(apiurl,room){
    var roomData = JSON.stringify(room);
    return $.ajax({
        url: SERVER_LOCATION + apiurl,
        type: "POST",
        data:roomData,
        processData:false,
        contentType: PLAINJSON
    }).done(function (data, textStatus, jqXHR){
        if (DEBUG) {
            console.log ("RECEIVED RESPONSE: data:",data,"; textStatus:",textStatus);
        }
        alert ("Room successfully added");
        //Add the user to the list and load it.

    }).fail(function (jqXHR, textStatus, errorThrown){
        if (DEBUG) {
            console.log ("RECEIVED ERROR: textStatus:",textStatus, ";error:",errorThrown);
        }
    });
}

function get_room(apiurl) {
    return $.ajax({
        url: SERVER_LOCATION + apiurl,
        dataType:DEFAULT_DATATYPE,
        processData:false
    }).done(function (data, textStatus, jqXHR){
        if (DEBUG) {
            console.log ("RECEIVED RESPONSE: data:",data,"; textStatus:",textStatus);
        }

        var $room = data;

        $("#room_name").empty().append($room.name);

        init_socket();

        $("#name").val($room.name||"??");
        $("#admin").val($room.admin||"??");
        $("#type").val($room.type||"PUBLIC");


        $("#room_form").attr("action", apiurl + "/");

        get_members(apiurl + "/members/");
        get_messages(apiurl + "/messages/");


    }).fail(function (jqXHR, textStatus, errorThrown){
        if (DEBUG) {
            console.log ("RECEIVED ERROR: textStatus:",textStatus, ";error:",errorThrown);
        }
        //Show an alert informing that I cannot get info from the user.
        alert ("Cannot extract information about this room from the forum service.");

    });
}

function get_members(apiurl) {
    $.ajax({
        url: SERVER_LOCATION + apiurl,
        dataType:DEFAULT_DATATYPE
    }).always(function(){

        $("#members_list").empty();

    }).done(function (data, textStatus, jqXHR){
        if (DEBUG) {
            console.log ("get_members: RECEIVED RESPONSE: data:",data,"; textStatus:",textStatus);
        }

        var members = data["members-all"];
        console.log(members);

        for (let i = 0; i < members.length; i++) {

            var member = members[i];
            var id =  member.id;
            var name = member.nickname;
            appendMemberToList(name);
        }

    }).fail(function (jqXHR, textStatus, errorThrown){
        if (DEBUG) {
            console.log ("RECEIVED ERROR: textStatus:",textStatus, ";error:",errorThrown);
        }
        alert("Cannot get information from message: "+ apiurl);
    });
}
/*
function list_names(apiurl) {
    return $.ajax({
        url: SERVER_LOCATION + apiurl,
        dataType:DEFAULT_DATATYPE,
        processData:false,
    }).done(function (data, textStatus, jqXHR){
        if (DEBUG) {
            console.log ("RECEIVED RESPONSE: data:",data,"; textStatus:",textStatus);
        }

        var name = data.nickname;
        appendMemberToList(name);

    }).fail(function (jqXHR, textStatus, errorThrown){
        if (DEBUG) {
            console.log ("RECEIVED ERROR: textStatus:",textStatus, ";error:",errorThrown);
        }
        //Show an alert informing that I cannot get info from the user.
        alert ("Cannot extract information about this room from the forum service.");

    });

}
*/

function list_sender(apiurl) {
    return $.ajax({
        url: SERVER_LOCATION + apiurl,
        dataType:DEFAULT_DATATYPE,
        processData:false
    }).done(function (data, textStatus, jqXHR){
        if (DEBUG) {
            console.log ("RECEIVED RESPONSE: data:",data,"; textStatus:",textStatus);
        }

        var name = data ["users-info"].nickname;
        appendSenderToList(name);

    }).fail(function (jqXHR, textStatus, errorThrown){
        if (DEBUG) {
            console.log ("RECEIVED ERROR: textStatus:",textStatus, ";error:",errorThrown);
        }
        //Show an alert informing that I cannot get info from the user.
        alert ("Cannot extract information about this room from the forum service.");

    });

}

function replaceIdWithName(id) {
    return $.ajax({
        url: SERVER_LOCATION + "/users/" + id,
        dataType:DEFAULT_DATATYPE,
        processData:false
    }).done(function (data, textStatus, jqXHR){
        if (DEBUG) {
            console.log ("RECEIVED RESPONSE: data:",data,"; textStatus:",textStatus);
        }

        var name = data.nickname;
        $( ".sender_name" ).each(function() {

            if($(this).html() == id) {
                $(this).empty().append(name);
            }
        });

    }).fail(function (jqXHR, textStatus, errorThrown){
        if (DEBUG) {
            console.log ("RECEIVED ERROR: textStatus:",textStatus, ";error:",errorThrown);
        }
        //Show an alert informing that I cannot get info from the user.
        alert ("Cannot extract information about this room from the forum service.");

    });

}

function serializeFormTemplate($form){
    var envelope={};
    // get all the inputs into an array.
    var $inputs = $form.find("input");
    $inputs.each(function() {
        envelope[this.id] = $(this).val();
    });

    return envelope;
}

function edit_user(apiurl, body){
    console.log(JSON.stringify(body));
    $.ajax({
        url: SERVER_LOCATION + apiurl,
        type: "PUT",
        data:JSON.stringify(body),
        processData:false,
        contentType: PLAINJSON
    }).done(function (data, textStatus, jqXHR){
        if (DEBUG) {
            console.log ("RECEIVED RESPONSE: data:",data,"; textStatus:",textStatus);
        }
        alert ("User information have been modified successfully");

    }).fail(function (jqXHR, textStatus, errorThrown){
        if (DEBUG) {
            console.log ("RECEIVED ERROR: textStatus:",textStatus, ";error:",errorThrown);
        }
        var error_message = $.parseJSON(jqXHR.responseText).message;
        alert ("Could not modify user information;\r\n"+error_message);
    });
}

function edit_room(apiurl, body){
    $.ajax({
        url: SERVER_LOCATION + apiurl,
        type: "PUT",
        data:JSON.stringify(body),
        processData:false,
        contentType: PLAINJSON

    }).done(function (data, textStatus, jqXHR){
        if (DEBUG) {
            console.log ("RECEIVED RESPONSE: data:",data,"; textStatus:",textStatus);
        }
        alert ("Room information have been modified successfully");

    }).fail(function (jqXHR, textStatus, errorThrown){
        if (DEBUG) {
            console.log ("RECEIVED ERROR: textStatus:",textStatus, ";error:",errorThrown);
        }
        var error_message = $.parseJSON(jqXHR.responseText).message;
        alert ("Could not modify room information;\r\n"+error_message);
    });
}


function delete_user(apiurl){
    $.ajax({
        url: SERVER_LOCATION + apiurl,
        type: "DELETE"

    }).done(function (data, textStatus, jqXHR){
        if (DEBUG) {
            console.log ("RECEIVED RESPONSE: data:",data,"; textStatus:",textStatus);
        }
        alert ("The user information has been deleted from the database. url: " + apiurl);
        //Update the list of users from the server.

    }).fail(function (jqXHR, textStatus, errorThrown){
        if (DEBUG) {
            console.log ("RECEIVED ERROR: textStatus:",textStatus, ";error:",errorThrown);
        }
        alert ("The user information could not be deleted from the database. ");
    });
}

function delete_room(apiurl){
    $.ajax({
        url: SERVER_LOCATION + apiurl,
        type: "DELETE"

    }).done(function (data, textStatus, jqXHR){
        if (DEBUG) {
            console.log ("RECEIVED RESPONSE: data:",data,"; textStatus:",textStatus);
        }
        alert ("The room information has been deleted from the database");
        //Update the list of users from the server.s

    }).fail(function (jqXHR, textStatus, errorThrown){
        if (DEBUG) {
            console.log ("RECEIVED ERROR: textStatus:",textStatus, ";error:",errorThrown);
        }
        alert ("The room information could not be deleted from the database. url: " + apiurl);
    });
}


/**
 * Uses the API to create a new user with the form attributes in the present form.
 *
 * TRIGGER: #createUser
 **/

function handleEditUser(event){
    if (DEBUG) {
        console.log ("Triggered handleEditUser");
    }
    var $form = $(this).closest("form");
    var body = serializeFormTemplate($form);
    var url = $form.attr("action");

    console.log(url);
    console.log(body);

    edit_user(url, body);
    return false; //Avoid executing the default submit
}

function handleDeleteUser(event){
    //Extract the url of the resource from the form action attribute.
    if (DEBUG) {
        console.log ("Triggered handleDeleteUser");
    }

    var user_url = $(this).closest("form").attr("action");
    console.log("url: " + user_url);
    delete_user(user_url);

    return false;
}

function handleDeleteRoom(event){
    //Extract the url of the resource from the form action attribute.
    if (DEBUG) {
        console.log ("Triggered handleDeleteRoom");
    }

    var room_url = $(this).closest("form").attr("action");
    delete_room(room_url);

    return false;
}

function handleEditRoom(event){
    if (DEBUG) {
        console.log ("Triggered handleEditRoom");
    }
    var $form = $(this).closest("form");
    var body = serializeFormTemplate($form);
    var url = $form.attr("action");

    edit_room(url, body);
    return false; //Avoid executing the default submit
}

function handleCreateUser(event){
    if (DEBUG) {
        console.log ("Triggered handleCreateUser");
    }
    var $form = $(this).closest("form");
    var template = serializeFormTemplate($form);
    var url = $form.attr("action");
    console.log(template);
    add_user(SERVER_LOCATION + url, template);
    return false; //Avoid executing the default submit
}

function handleCreateRoom(event){
    if (DEBUG) {
        console.log ("Triggered handleCreateRoom");
    }
    var $form = $(this).closest("form");
    var template = serializeFormTemplate($form);
    var url = $form.attr("action");
    add_room(url, template);
    return false; //Avoid executing the default submit
}


function appendRoomToList(url, name) {


    var $room = $('<tr><td>' + name + '</td><td><form id="joinRoom" action='+ url + ' >' + '<a href="'+ url +'" class = "btn btn-info btn-sm"> Join </a></form></td>');

    //var $room = $('<tr><td><a href=' +url+ ' >' + name + '</a></td></tr>');
    //Append to list
    $("#roomlist").append($room);

}

function appendUserToList(url, name) {

    var $user = $('<tr><td><a href=' +url+ ' >' + name + '</a></td></tr>');

    $("#userslist").append($user);
}

function appendMemberToList(name) {

    var $member = $('<li>' + name + '</li>');

    $("#members_list").append($member);
}

function appendSenderToList(name) {

    var msg = ('<li class="chat_bubble" style="float: left; font-size: smaller">'+name+'</li>');
    $("#messages_list").append(msg);
}

function appendMessageToList(content, sender) {

    //list_sender("/api/users/" + sender);

    var message = ('<li class="chat_bubble sender_name" style="float: left; font-size: smaller">' + sender + '</li>');
    message += ('<li class="chat_bubble chat_bubble-received">' + content + '</li>');

    $("#messages_list").append(message);
}

/**
 * Socket.io chat
 *
 **/

/**
 * Socket.io chat
 *
 **/

var nickname = 'rICK';
var room_name;
var socket;

function init_socket() {

    var room_name = $("#room_name").html();
    console.log(room_name);

    console.log('socket init');
    // Endpoint is the same for every message. Dynamic endpoints weren't supported.
    //socket = io.connect('http://' + document.domain + ':' + location.port + '/chat');
    socket = io.connect('http://localhost:5000/chat');

    socket.on('connect', function () {
        // socket.emit('foo', {key: value}) sends an foo event to connected route.
        socket.emit('joined', {room_name: room_name, nickname: nickname});
    });
    socket.on('status', function (data) {
        //     $('#chat').val($('#chat').val() + '<' + data.msg + '>\n');
        //   $('#chat').scrollTop($('#chat')[0].scrollHeight);
        var message = ('<li class="chat_bubble sender_name" style="float: left; font-size: smaller">' + data.msg + '</li>');
        $("#messages_list").append(message);
        $("#chatbox").scrollTop($('#chatbox')[0].scrollHeight);

    });
    socket.on('message', function (data) {
        //  $('#chat').val($('#chat').val() + data.msg + '\n');
        //  $('#chat').scrollTop($('#chat')[0].scrollHeight);

        var msg = data.msg.split(":");

        var message = ('<li class="chat_bubble chat_bubble-sent">' + msg[1] + '</li>');
        $("#messages_list").append(message);
        $("#chatbox").scrollTop($('#chatbox')[0].scrollHeight);

    });
    $('#text').keypress(function (e) {
        var code = e.keyCode || e.which;
        if (code == 13) {
            var text = $('#text').val();
            $('#text').val('');
            socket.emit('text', {msg: text, room_name: room_name, nickname: nickname});
        }
    });
}

function leave_room() {
    socket.emit('left', {room_name: room_name, nickname: nickname}, function () {
        socket.disconnect();
    });
}
