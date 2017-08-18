

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



var GLOBALS = {

    room_id: room_id

};

var room_id;



function getRooms(apiurl) {
    apiurl = apiurl || ENTRYPOINT;
    $("#room_list").hide();
    return $.ajax({
        url: apiurl,
        dataType:DEFAULT_DATATYPE
    }).always(function(){
        //Remove old list of users
        //clear the form data hide the content information(no selected)
        $("#room_list").empty();
      

    }).done(function (data, textStatus, jqXHR){
        if (DEBUG) {
            console.log ("RECEIVED RESPONSE: data:",data,"; textStatus:",textStatus);
        } else {
        	console.log("ei toimi");
        }
        //Extract the users
        rooms = data.items;
        for (var i=0; i < rooms.length; i++){
            var room = rooms[i];
            //Extract the nickname by getting the data values. Once obtained
            // the nickname use the method appendUserToList to show the user
            // information in the UI.
            appendUserToList(room["@controls"].self.href, room.name)
        }

    });
}




getRooms();


