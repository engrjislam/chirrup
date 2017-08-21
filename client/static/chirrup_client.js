const ENTRYPOINT = "http://localhost:5000/rooms/";
var DEBUG = true;

/**
 * Mason+JSON mime-type
 * @constant {string}
 * @default
 */
 const MASONJSON = "application/vnd.mason+json";

 const PLAINJSON = "application/json";
 const DEFAULT_DATATYPE = "json";

 function get_room(apiurl){
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
        var room_url = data["@controls"].self.href;
        var admin = data.admin;

        for (i = 0; i < data["rooms-all"].length; i++) {

            var name =  data["rooms-all"][i].name;
            appendRoomToList(room_url, admin, name);
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



function get_user(apiurl){
    apiurl = "http://localhost:5000/users/";
    $.ajax({
        url: apiurl,
        dataType:DEFAULT_DATATYPE
    }).always(function(){

        $("#nickname").empty();

    }).done(function (data, textStatus, jqXHR){
        if (DEBUG) {
            console.log ("RECEIVED RESPONSE: data:",data,"; textStatus:",textStatus);
        }
        var user_url = data["@controls"].self.href;
        var user = data.user;


        var nickname =  data["users-all"][0].nickname;
        appendNicknameToProfile(user_url, nickname);
        


    }).fail(function (jqXHR, textStatus, errorThrown){
        if (DEBUG) {
            console.log ("RECEIVED ERROR: textStatus:",textStatus, ";error:",errorThrown);
        }
        alert("Cannot get information from message: "+ apiurl);
    });
}



function appendRoomToList(url, admin, name) {


    var $room = $('<tr><td>' + name + '</td> ' +
        '<td><a href=' + url + ' class = "btn btn-info btn-sm"> <span class="glyphicon glyphicon-plus"></span> Join </a></td></tr>');
    //Append to list
    $("#roomlist").append($room);

}

function appendNicknameToProfile(url, nickname) {


    var $user = $('<h4>' + 'Nickname: ' +'  '+ nickname +'</h4>');
    //Append to list
    $("#nickname").append($user);

}






get_room(ENTRYPOINT);
get_user(ENTRYPOINT);




