const SERVER_LOCATION = "http://localhost:5000";
const ENTRYPOINT = SERVER_LOCATION + "/rooms/";
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
    apiurl = ENTRYPOINT;
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

        for (i = 0; i < rooms.length; i++) {

            var room = rooms[i];

            var name =  room.name;
            var room_url = "/chirrup/room/" + room.room_id;

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
        url: apiurl,
        dataType:DEFAULT_DATATYPE
    }).always(function(){

        $("#userslist").empty();

    }).done(function (data, textStatus, jqXHR){
        if (DEBUG) {
            console.log ("RECEIVED RESPONSE: data:",data,"; textStatus:",textStatus);
        }

        var users = data["users-all"];

        for (i = 0; i < users.length; i++) {

            var user = users[i];
            var name =  user.nickname;
            var user_url = "/chirrup/user/" + user.user_id;
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
        url: apiurl,
        dataType:DEFAULT_DATATYPE,
        processData:false
    }).done(function (data, textStatus, jqXHR){
        if (DEBUG) {
            console.log ("RECEIVED RESPONSE: data:",data,"; textStatus:",textStatus);
        }

        /*

        user_id=user["user_id"],
            username=user["username"],
            email=user["email"],
            status=user["status"],
            created=user["created"],
            updated=user["updated"],
            nickname=user["nickname"],
            image=user["image"]

          */

        var $user = data["users-info"];

        //Fill basic information from the user_basic_form
        $("#user_name").append($user.username);
        //delete(data.username);
        $("#nick_name").append($user.nickname || "??" );
        //delete(data.nickname);
        $("#image").val($user.image||"??");

        $("#user_form").attr("action", apiurl);

        //Extract user information
        var user_links = data["@controls"];
        //Extracts urls from links. I need to get if the different links in the
        //response.

        if ("delete" in user_links)
            var delete_link = user_links["delete"].href; // User delete linke
        if ("edit" in user_links)
            var edit_link = user_links["edit"].href;

        if (delete_link){
            $("#user_form").attr("action", delete_link);
            $("#deleteUser").show();
        }
        if (edit_link){
            $("#user_form").attr("action", edit_link);
            $("#editUser").show();
        }

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
        url: apiurl,
        dataType:DEFAULT_DATATYPE
    }).always(function(){

        $("#messages_list").empty();

    }).done(function (data, textStatus, jqXHR){
        if (DEBUG) {
            console.log ("get_messages: RECEIVED RESPONSE: data:",data,"; textStatus:",textStatus);
        }

        var messages = data["room-messages"];
        var max_messages;

        if (messages.length < 10 ) {
            max_messages = 0;
        } else
            max_messages = messages.length - 10;

        for (i = max_messages; i < messages.length; i++) {

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
    var nickname = user.nickname;
    return $.ajax({
        url: apiurl,
        type: "POST",
        //dataType:DEFAULT_DATATYPE,
        data:userData,
        processData:false,
        contentType: PLAINJSON
    }).always(function(){

        console.log(userData);

    }).done(function (data, textStatus, jqXHR){
        if (DEBUG) {
            console.log ("RECEIVED RESPONSE: data:",data,"; textStatus:",textStatus);
        }
        alert ("User successfully added");
        //Add the user to the list and load it.
        $user = appendUserToList(jqXHR.getResponseHeader("Location"),nickname);

    }).fail(function (jqXHR, textStatus, errorThrown){
        if (DEBUG) {
            console.log ("RECEIVED ERROR: textStatus:",textStatus, ";error:",errorThrown);
        }
        alert ("Could not create new user:"+jqXHR.responseJSON.message);
    });
}

function add_room(apiurl,room){
    var roomData = JSON.stringify(room);
    var name = room.name;
    return $.ajax({
        url: apiurl,
        type: "POST",
        //dataType:DEFAULT_DATATYPE,
        data:roomData,
        processData:false,
        contentType: PLAINJSON
    }).always(function(){

        console.log(roomData);

    }).done(function (data, textStatus, jqXHR){
        if (DEBUG) {
            console.log ("RECEIVED RESPONSE: data:",data,"; textStatus:",textStatus);
        }
        alert ("Room successfully added");
        //Add the user to the list and load it.
        $room = appendRoomToList(jqXHR.getResponseHeader("Location"),name);

    }).fail(function (jqXHR, textStatus, errorThrown){
        if (DEBUG) {
            console.log ("RECEIVED ERROR: textStatus:",textStatus, ";error:",errorThrown);
        }
        alert ("Could not create new room:"+jqXHR.responseJSON.message);
    });
}

function get_room(apiurl) {
    return $.ajax({
        url: apiurl,
        dataType:DEFAULT_DATATYPE,
        processData:false
    }).done(function (data, textStatus, jqXHR){
        if (DEBUG) {
            console.log ("RECEIVED RESPONSE: data:",data,"; textStatus:",textStatus);
        }

        var $room = data["rooms-info"];

        $("#room_name").empty().append($room.name);

        var room_url = data["@controls"].self.href;

        get_members(room_url + "members/");
        get_messages(room_url + "messages/");


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
        url: apiurl,
        dataType:DEFAULT_DATATYPE
    }).always(function(){

        $("#members_list").empty();

    }).done(function (data, textStatus, jqXHR){
        if (DEBUG) {
            console.log ("get_members: RECEIVED RESPONSE: data:",data,"; textStatus:",textStatus);
        }

        var members = data["room-members"];

        for (i = 0; i < members.length; i++) {

            var member = members[i];
            var id =  member.id;
            var user_url = "/users/" + id + "/";
            list_names(user_url);
        }

    }).fail(function (jqXHR, textStatus, errorThrown){
        if (DEBUG) {
            console.log ("RECEIVED ERROR: textStatus:",textStatus, ";error:",errorThrown);
        }
        alert("Cannot get information from message: "+ apiurl);
    });
}

function list_names(apiurl) {
    return $.ajax({
        url: apiurl,
        dataType:DEFAULT_DATATYPE,
        processData:false,
    }).done(function (data, textStatus, jqXHR){
        if (DEBUG) {
            console.log ("RECEIVED RESPONSE: data:",data,"; textStatus:",textStatus);
        }

        var name = data ["users-info"].nickname;
        appendMemberToList(name);

    }).fail(function (jqXHR, textStatus, errorThrown){
        if (DEBUG) {
            console.log ("RECEIVED ERROR: textStatus:",textStatus, ";error:",errorThrown);
        }
        //Show an alert informing that I cannot get info from the user.
        alert ("Cannot extract information about this room from the forum service.");

    });

}

function list_sender(apiurl) {
    return $.ajax({
        url: apiurl,
        dataType:DEFAULT_DATATYPE,
        processData:false,
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
        url: "/users/" + id,
        dataType:DEFAULT_DATATYPE,
        processData:false,
    }).done(function (data, textStatus, jqXHR){
        if (DEBUG) {
            console.log ("RECEIVED RESPONSE: data:",data,"; textStatus:",textStatus);
        }

        var name = data["users-info"].nickname;
        $( ".sender_name" ).each(function( i ) {

            console.log(id);
            console.log($(this).html());

            if($(this).html() == id) {
                console.log("hello");
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

    console.log(envelope);
    /*
    var subforms = $form.find(".form_content .subform");
    subforms.each(function() {

        var data = {}

        $(this).children("input").each(function() {
            data[this.id] = $(this).val();
        });

        envelope[this.id] = data
    });
    */
    return envelope;
}

function edit_user(apiurl, body){
    $.ajax({
        url: apiurl,
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
        url: apiurl,
        type: "PUT",
        data:JSON.stringify(body),
        processData:false,
        contentType: PLAINJSON
    }).always(function(){

        console.log(data);

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
        url: apiurl,
        type: "DELETE"

    }).done(function (data, textStatus, jqXHR){
        if (DEBUG) {
            console.log ("RECEIVED RESPONSE: data:",data,"; textStatus:",textStatus);
        }
        alert ("The user information has been deleted from the database");
        //Update the list of users from the server.
        getUsers();

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

    }).always(function(){

        console.log(apiurl);

    }).done(function (data, textStatus, jqXHR){
        if (DEBUG) {
            console.log ("RECEIVED RESPONSE: data:",data,"; textStatus:",textStatus);
        }
        alert ("The room information has been deleted from the database");
        //Update the list of users from the server.
        get_rooms();

    }).fail(function (jqXHR, textStatus, errorThrown){
        if (DEBUG) {
            console.log ("RECEIVED ERROR: textStatus:",textStatus, ";error:",errorThrown);
        }
        alert ("The room information could not be deleted from the database. ");
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
    console.log(room_url);
    delete_room(room_url);

    return false;
}

function handleGetRoom(event){

    if (DEBUG) {
        console.log ("Triggered handleGetRoom");
    }
    var $form = $(this).closest("form");
    var url = $form.attr("action");

    return false; //Avoid executing the default submit
}

function handleEditRoom(event){
    if (DEBUG) {
        console.log ("Triggered handleEditUser");
    }
    var $form = $(this).closest("form");
    var body = serializeFormTemplate($form);
    var url = $form.attr("action");

    console.log(url);
    console.log(body);

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
    add_user(url, template);
    return false; //Avoid executing the default submit
}

function handleCreateRoom(event){
    if (DEBUG) {
        console.log ("Triggered handleCreateRoom");
    }
    var $form = $(this).closest("form");
    var template = serializeFormTemplate($form);
    var url = $form.attr("action");
    console.log(template);
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

    var sender = ('<li class="chat_bubble" style="float: left; font-size: smaller">'+name+'</li>');
    $("#messages_list").append(sender);
}

function appendMessageToList(content, sender) {

    //list_sender("/api/users/" + sender);

    var message = ('<li class="chat_bubble sender_name" style="float: left; font-size: smaller">' + sender + '</li>');
    message += ('<li class="chat_bubble chat_bubble-received">' + content + '</li>');

    $("#messages_list").append(message);
}


 $(function(){
       // $("#deleteUser").on("click", handleDeleteUser);
        $("#user_info").on("click",".deleteUser",handleDeleteUser);
        $("#roomlist").on("click", "a", handleGetRoom);

    });


