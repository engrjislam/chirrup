// Global variables
var nickname;
var room_id;
var user_id = 1;


// Save data to sessionStorage if available.
// Saved data survives page reloads and moving between pages.
// Data is deleted when browser is closed. SessionStorage not used yet.
if (typeof(Storage) !== 'undefined'  && 1===5) {
    // Select some room_id from list of possible rooms. User would probably pick one manually.
    room_id = sessionStorage.getItem('room_id');
    // check if user nickname already gotten from api
    nickname = sessionStorage.getItem('nickname');
    // get_one_room returns a promise. .then clause is run after the ajax request has finished.
    // If a promise or equivalent structure wasn't used room_id would be undefined
    get_one_room()
        .then(function (data) {
            console.log('Saving room_id to session');
            room_id = data;
            // save the room_id to sessionStorage
            sessionStorage.setItem('room_id', parseInt(room_id));
            return Promise.resolve();
        })
        .then(function () {
            return get_user_nickname(user_id);
        })
        .then(function (data) {
            console.log('Saving nickname to session');
            nickname = data;
            // save the nickname to sessionStorage
            sessionStorage.setItem('nickname', nickname);
            return Promise.resolve();
        });
} else {
    // Sorry! No Web Storage support..
    console.log('Web storage can\'t be used');
    get_user_nickname(user_id)
        .then(function (data) {
            nickname = data;
            return Promise.resolve();
        })
        .then(get_one_room)
        .then(function (data) {
            room_id = data;
            console.log('Room_id set:', room_id);
            return Promise.resolve();
        });
}

function get_one_room() {
    return new Promise(function (resolve, reject) {
        if (room_id !== undefined && nickname!==null){
            resolve(room_id)
        }
        $.get('http://localhost:5000/rooms/', function (data, status) {
            console.log(data);
            // example of getting a room from room_id
            resolve(parseInt(data['rooms-all'][0]['room_id']));
        });
    });
}

function get_user_nickname(user_id) {
    return new Promise(function (resolve, reject) {
        if (nickname!==undefined && nickname!==null){
            resolve(nickname)
        }
        $.get('http://localhost:5000/users/' + user_id + '/', function (data, status) {
            console.log(data);
            // example of getting a room from room_id
            resolve(data['users-info']['nickname']);
        });
    });
}