

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
    }).done(function (data, textStatus, jqXHR){
        if (DEBUG) {
            console.log ("RECEIVED RESPONSE: data:",data,"; textStatus:",textStatus);
        }
        var room_url = data["@controls"].self.href;
        var admin = data.admin;
        var name =  data.name;
        appendRoomToList(room_url, admin, name);
        console.log("KMDSKFMSDKFMSDKFMSDKMFS");

    }).fail(function (jqXHR, textStatus, errorThrown){
        if (DEBUG) {
            console.log ("RECEIVED ERROR: textStatus:",textStatus, ";error:",errorThrown);
        }
        alert("Cannot get information from message: "+ apiurl);
    });
}

function appendRoomToList(url, admin, name) {
        
    var $room = $("<div>").addClass('room').html(""+
                        "<form action='"+url+"'>"+
                        "   <div class='form_content'>"+
                        "       <input type=text class='admin' value='"+admin+"' readonly='readonly'/>"+
                        "       <div class='name'>"+name+"</div>"+
                        "   </div>"+
                        "   <div class='commands'>"+
                        "        <input type='button' class='deleteButton deleteMessage' value='Delete'/>"+
                        "   </div>" +
                        "</form>"
                    );
    //Append to list
    $("#rooms_list").append($room);


}



get_room(ENTRYPOINT);
