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

                var create_ctrl = data["@controls"]["add-room"]                                                 

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
    apiurl = "http://localhost:5000/users/";
    $.ajax({
        url: "http://localhost:5000/users/",
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

        var create_ctrl = data["@controls"]["add-user"];

        if (create_ctrl.schema) {
            createFormFromSchema(create_ctrl.href, create_ctrl.schema, "new_user_form");
        }
        else if (create_ctrl.schemaUrl) {
            $.ajax({
                url: create_ctrl.schemaUrl,
                dataType: DEFAULT_DATATYPE
            }).done(function (data, textStatus, jqXHR) {
                createFormFromSchema(create_ctrl.href, data, "new_user_form");
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

function get_user(apiurl) {
    return $.ajax({
        url: "http://localhost:5000/users/<id>",
        dataType:DEFAULT_DATATYPE,
        processData:false,
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

        //Fill basic information from the user_basic_form
        $("#username").val(data.username);
        delete(data.username);
        $("#nickname").val(data.nickname);
        delete(data.nickname);
        $("#image").val(data.image||"??");

        //Extract user information
        var user_links = data["@controls"];
        //Extracts urls from links. I need to get if the different links in the
        //response.
        if ("private-data" in user_links) {
            var private_profile_url = user_links["private-data"].href; //Restricted profile
        }
        if ("messages-history" in user_links){
            var messages_url = user_links["messages-history"].href;
            // cut out the optional query parameters. this solution is not pretty.
            messages_url = messages_url.slice(0, messages_url.indexOf("{?"));
        }
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

        //Fill the user profile with restricted user profile. This method
        // Will call also to the list of messages.
        if (private_profile_url){
            private_data(private_profile_url);
        }
        //Get the history link and ask for history.
        if (messages_url){
            messages_history(messages_url);
        }


    }).fail(function (jqXHR, textStatus, errorThrown){
        if (DEBUG) {
            console.log ("RECEIVED ERROR: textStatus:",textStatus, ";error:",errorThrown);
        }
        //Show an alert informing that I cannot get info from the user.
        alert ("Cannot extract information about this user from the forum service.");
        //Deselect the user from the list.
        deselectUser();
    });
}

function appendRoomToList(url, name) {


    var $room = $('<tr><td>' + name + '</td> ' +
        '<td><a href=' + url + ' class = "btn btn-info btn-sm"> <span class="glyphicon glyphicon-plus"></span> Join </a></td></tr>');
    //Append to list
    $("#roomlist").append($room);

}

function appendUserToList(url, name) {

    var $user2 = $('<tr><td><a href=' +url+ ' >' + name + '</a></td></tr>');

    $("#userslist").append($user2);
}

get_rooms(ENTRYPOINT);
get_users("http://localhost:5000/users");



