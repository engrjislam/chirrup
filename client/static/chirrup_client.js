const SERVER_LOCATION = "http://localhost:5000";
const ENTRYPOINT = SERVER_LOCATION + "/api/rooms/";
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
    apiurl = apiurl || ENTRYPOINT;
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
            var room_url = SERVER_LOCATION + room["@controls"].self.href;

            appendRoomToList(room_url, name);

        }

                var create_ctrl = data["@controls"]["add-room"];

                if (create_ctrl.schema) {
                    createFormFromSchema(create_ctrl.href, create_ctrl.schema, "new_room_form");
                }
                else if (create_ctrl.schemaUrl) {
                    $.ajax({
                        url: create_ctrl.schemaUrl,
                        dataType: DEFAULT_DATATYPE
                    }).done(function (data, textStatus, jqXHR) {
                        createFormFromSchema(create_ctrl.href, data, "new_room_form");
                    }).fail(function (jqXHR, textStatus, errorThrown) {
                        if (DEBUG) {
                            console.log ("RECEIVED ERROR: textStatus:",textStatus, ";error:",errorThrown);
                        }
                        alert ("Could not fetch form schema.  Please, try again");
                    });
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
            var user_url = SERVER_LOCATION + user["@controls"].self.href;
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
        $("#username").append($user.username);
        //delete(data.username);
        $("#nickname").append($user.nickname || "??" );
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

        /*

         item = ChirrupObject(
         room_id=room["room_id"],
         name=room["name"],
         admin=room["admin"],
         created=room["created"],
         updated=room["updated"]
         )

         */

        var $room = data["rooms-info"];

        console.log($room);

        //$("#room_name").empty().append($room.name);

        console.log("This rooms name is: " + $room.name);

        $("#room_name").append($room.name);

        //delete(data.username);

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
}

function handleDeleteRoom(event){
    //Extract the url of the resource from the form action attribute.
    if (DEBUG) {
        console.log ("Triggered handleDeleteRoom");
    }

    var room_url = $(this).closest("form").attr("action");
    console.log(room_url);
    delete_room(room_url);
}

function handleGetRoom(event){

    if (DEBUG) {
        console.log ("Triggered handleGetRoom");
    }
    var $form = $(this).closest("form");
    var url = $form.attr("action");
    console.log("attr url: " + url);
    window.location.href = "index.html";

    $( document ).ready(function() {

        get_room(url);
        console.log("hello");

    });
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


    var $room = $('<tr><td>' + name + '</td> ' +
        '<td><form id="joinRoom" action='+ url + ' >' + '<a href="index.html" class = "btn btn-info btn-sm"> <span class="glyphicon glyphicon-plus"></span> Join </a></form></td></tr>');
    //Append to list
    $("#roomlist").append($room);

}

function appendUserToList(url, name) {

    var $user = $('<tr><td><a href=' +url+ ' >' + name + '</a></td></tr>');

    $("#userslist").append($user);
}



 $(function(){
        $("#editUser").on("click", handleEditUser);
       // $("#deleteUser").on("click", handleDeleteUser);
        $("#user_info").on("click",".deleteUser",handleDeleteUser);
        $("#roomlist").on("click", "a", handleGetRoom);

    });

//get_users("http://localhost:5000/users");
//get_user("http://localhost:5000/api/users/2");



